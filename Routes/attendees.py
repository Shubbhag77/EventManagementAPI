from fastapi import APIRouter, HTTPException, Query, Depends, status, UploadFile, File
from typing import List, Optional

from models import AttendeeCreate, AttendeeUpdate, AttendeeResponse
from Services import attendee_service

router = APIRouter()


@router.post("/", response_model=AttendeeResponse, status_code=status.HTTP_201_CREATED)
async def register_attendee(attendee: AttendeeCreate):
    created_attendee = await attendee_service.register_attendee(attendee)
    if not created_attendee:
        raise HTTPException(
            status_code=400,
            detail="Unable to register attendee. Event may not exist, may be full, or email already registered."
        )
    return created_attendee


@router.get("/{attendee_id}", response_model=AttendeeResponse)
async def get_attendee(attendee_id: str):
    attendee = await attendee_service.get_attendee(attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return attendee


@router.put("/{attendee_id}", response_model=AttendeeResponse)
async def update_attendee(attendee_id: str, attendee_update: AttendeeUpdate):
    updated_attendee = await attendee_service.update_attendee(attendee_id, attendee_update)
    if not updated_attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return updated_attendee


@router.post("/{attendee_id}/check-in", response_model=AttendeeResponse)
async def check_in_attendee(attendee_id: str):
    checked_in_attendee = await attendee_service.check_in_attendee(attendee_id)
    if not checked_in_attendee:
        raise HTTPException(status_code=404, detail="Attendee not found or event is not ongoing")
    return checked_in_attendee


@router.get("/event/{event_id}", response_model=List[AttendeeResponse])
async def list_attendees(
        event_id: str,
        checked_in: Optional[bool] = Query(None, description="Filter by check-in status"),
        skip: int = Query(0, ge=0, description="Number of attendees to skip"),
        limit: int = Query(100, ge=1, le=100, description="Number of attendees to return"),
):
    attendees = await attendee_service.list_attendees(
        event_id=event_id,
        checked_in=checked_in,
        skip=skip,
        limit=limit
    )
    return attendees


@router.post("/event/{event_id}/bulk-check-in")
async def bulk_check_in(event_id: str, file: UploadFile = File(...)):
    content = await file.read()

    result = await attendee_service.bulk_check_in(event_id, content)

    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("message", "Bulk check-in failed"))

    return result