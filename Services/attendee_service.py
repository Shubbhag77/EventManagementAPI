from models import AttendeeCreate, AttendeeUpdate, AttendeeInDB, EventStatus
from database import attendees_collection, events_collection
from Services.event_service import get_event, get_event_attendee_count
from datetime import datetime
from bson import ObjectId
from typing import List, Optional, Dict, Any
import csv
import io


async def register_attendee(attendee: AttendeeCreate) -> Optional[AttendeeInDB]:
    # Check if event exists
    event = await get_event(attendee.event_id)
    if not event:
        return None

    # Check if event is scheduled or ongoing
    if event.status not in [EventStatus.SCHEDULED, EventStatus.ONGOING]:
        return None

    # Check if max attendees limit reached
    current_attendees = await get_event_attendee_count(attendee.event_id)
    if current_attendees >= event.max_attendees:
        return None

    # Check if email already registered for this event
    existing_attendee = await attendees_collection.find_one({
        "event_id": ObjectId(attendee.event_id),
        "email": attendee.email
    })
    if existing_attendee:
        return None

    # Create attendee
    attendee_data = attendee.dict()
    attendee_data["event_id"] = ObjectId(attendee.event_id)
    attendee_data["check_in_status"] = False
    attendee_data["registration_time"] = datetime.utcnow()

    result = await attendees_collection.insert_one(attendee_data)
    return await get_attendee(str(result.inserted_id))


async def get_attendee(attendee_id: str) -> Optional[AttendeeInDB]:
    if not ObjectId.is_valid(attendee_id):
        return None

    attendee = await attendees_collection.find_one({"_id": ObjectId(attendee_id)})
    if attendee:
        return AttendeeInDB(**attendee)
    return None


async def update_attendee(attendee_id: str, attendee_update: AttendeeUpdate) -> Optional[AttendeeInDB]:
    if not ObjectId.is_valid(attendee_id):
        return None

    # Get current attendee
    current_attendee = await get_attendee(attendee_id)
    if not current_attendee:
        return None

    # Update fields
    update_data = attendee_update.dict(exclude_unset=True)

    # Execute update
    await attendees_collection.update_one(
        {"_id": ObjectId(attendee_id)},
        {"$set": update_data}
    )

    return await get_attendee(attendee_id)


async def check_in_attendee(attendee_id: str) -> Optional[AttendeeInDB]:
    if not ObjectId.is_valid(attendee_id):
        return None

    # Get attendee
    attendee = await get_attendee(attendee_id)
    if not attendee:
        return None

    # Check if event is ongoing
    event = await get_event(str(attendee.event_id))
    if not event or event.status != EventStatus.ONGOING:
        return None

    # Update check-in status
    await attendees_collection.update_one(
        {"_id": ObjectId(attendee_id)},
        {"$set": {"check_in_status": True}}
    )

    return await get_attendee(attendee_id)


async def list_attendees(
        event_id: str,
        checked_in: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
) -> List[AttendeeInDB]:
    if not ObjectId.is_valid(event_id):
        return []

    # Build filter query
    query = {"event_id": ObjectId(event_id)}

    if checked_in is not None:
        query["check_in_status"] = checked_in

    # Execute query
    cursor = attendees_collection.find(query).skip(skip).limit(limit)
    attendees = await cursor.to_list(length=limit)

    return [AttendeeInDB(**attendee) for attendee in attendees]


async def bulk_check_in(event_id: str, csv_content: bytes) -> Dict[str, Any]:
    if not ObjectId.is_valid(event_id):
        return {"success": False, "message": "Invalid event ID"}

    # Check if event exists and is ongoing
    event = await get_event(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}

    if event.status != EventStatus.ONGOING:
        return {"success": False, "message": "Event is not ongoing"}

    # Process CSV file
    try:
        content = csv_content.decode('utf-8-sig')
        csv_reader = csv.DictReader(io.StringIO(content))

        success_count = 0
        failed_emails = []

        for row in csv_reader:

            # Check if email exists in CSV
            if 'email' not in row:
                continue

            email = row['email'].strip()

            # Find attendee by email and event_id
            attendee = await attendees_collection.find_one({
                "event_id": ObjectId(event_id),
                "email": email
            })

            if attendee and not attendee.get("check_in_status", False):
                # Update check-in status
                await attendees_collection.update_one(
                    {"_id": attendee["_id"]},
                    {"$set": {"check_in_status": True}}
                )
                success_count += 1
            else:
                failed_emails.append(email)

        return {
            "success": True,
            "checked_in_count": success_count,
            "failed_emails": failed_emails
        }

    except Exception as e:
        return {"success": False, "message": str(e)}
