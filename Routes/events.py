from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional
from datetime import datetime

from models import EventCreate, EventUpdate, EventResponse
from Services import event_service

router = APIRouter()

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate):
    created_event = await event_service.create_event(event)
    return created_event

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    event = await event_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, event_update: EventUpdate):
    updated_event = await event_service.update_event(event_id, event_update)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str):
    deleted = await event_service.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
    return None

@router.get("/", response_model=List[EventResponse])
async def list_events(
    status: Optional[str] = Query(None, description="Filter by event status"),
    location: Optional[str] = Query(None, description="Filter by location"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (from)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (to)"),
    skip: int = Query(0, ge=0, description="Number of events to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of events to return"),
):
    events = await event_service.list_events(
        status=status,
        location=location,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return events