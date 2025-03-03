from models import EventCreate, EventUpdate, EventInDB, EventStatus
from database import events_collection, attendees_collection
from datetime import datetime
from bson import ObjectId
from typing import List, Optional


async def create_event(event: EventCreate) -> EventInDB:
    event_data = event.dict()
    event_data["status"] = EventStatus.SCHEDULED
    event_data["created_at"] = datetime.utcnow()
    event_data["updated_at"] = datetime.utcnow()

    result = await events_collection.insert_one(event_data)
    return await get_event(result.inserted_id)


async def get_event(event_id: str) -> Optional[EventInDB]:
    if not ObjectId.is_valid(event_id):
        return None

    event = await events_collection.find_one({"_id": ObjectId(event_id)})
    if event:
        return EventInDB(**event)
    return None


async def update_event(event_id: str, event_update: EventUpdate) -> Optional[EventInDB]:
    if not ObjectId.is_valid(event_id):
        return None

    # Get current event
    current_event = await get_event(event_id)
    if not current_event:
        return None

    # Update fields
    update_data = event_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # Execute update
    await events_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": update_data}
    )

    # Return updated event
    return await get_event(event_id)


async def delete_event(event_id: str) -> bool:
    if not ObjectId.is_valid(event_id):
        return False

    result = await events_collection.delete_one({"_id": ObjectId(event_id)})

    # Delete all attendees for this event
    await attendees_collection.delete_many({"event_id": ObjectId(event_id)})

    return result.deleted_count > 0


async def list_events(
        status: Optional[EventStatus] = None,
        location: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
) -> List[EventInDB]:
    # Build filter query
    query = {}

    if status:
        query["status"] = status

    if location:
        query["location"] = {"$regex": location, "$options": "i"}

    date_filter = {}
    if start_date:
        date_filter["$gte"] = start_date
    if end_date:
        date_filter["$lte"] = end_date

    if date_filter:
        query["start_time"] = date_filter

    # Execute query
    cursor = events_collection.find(query).skip(skip).limit(limit)
    events = await cursor.to_list(length=limit)

    # Update event status based on current time if needed
    current_time = datetime.utcnow()
    updated_events = []

    for event in events:
        # If event has ended, update status to completed
        if event["status"] == EventStatus.SCHEDULED and event["end_time"] <= current_time:
            await events_collection.update_one(
                {"_id": event["_id"]},
                {"$set": {"status": EventStatus.COMPLETED, "updated_at": current_time}}
            )
            event["status"] = EventStatus.COMPLETED
            event["updated_at"] = current_time

        # If event has started but not ended, update status to ongoing
        elif event["status"] == EventStatus.SCHEDULED and event["start_time"] <= current_time < event["end_time"]:
            await events_collection.update_one(
                {"_id": event["_id"]},
                {"$set": {"status": EventStatus.ONGOING, "updated_at": current_time}}
            )
            event["status"] = EventStatus.ONGOING
            event["updated_at"] = current_time

        updated_events.append(EventInDB(**event))

    return updated_events


async def get_event_attendee_count(event_id: str) -> int:
    if not ObjectId.is_valid(event_id):
        return 0

    return await attendees_collection.count_documents({"event_id": ObjectId(event_id)})