from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId


# Custom ObjectId field to work with MongoDB
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# Enum for event status
class EventStatus(str, Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELED = "canceled"


# Base models
class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True


# Event models
class EventBase(BaseModel):
    name: str = ""
    description: str = ""
    start_time: datetime
    end_time: datetime
    location: str = ""
    max_attendees: int

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    max_attendees: Optional[int] = None
    status: Optional[EventStatus] = None

    @validator('max_attendees')
    def max_attendees_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('max_attendees must be positive')
        return v


class EventInDB(EventBase, MongoBaseModel):
    status: EventStatus = EventStatus.SCHEDULED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EventResponse(EventInDB):
    pass


# Attendee models
class AttendeeBase(BaseModel):
    first_name: str = ""
    last_name: str = ""
    email: EmailStr = ""
    phone_number: str = ""


class AttendeeCreate(AttendeeBase):
    event_id: str = ""


class AttendeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    check_in_status: Optional[bool] = None


class AttendeeInDB(AttendeeBase, MongoBaseModel):
    event_id: PyObjectId
    check_in_status: bool = False
    registration_time: datetime = Field(default_factory=datetime.utcnow)


class AttendeeResponse(AttendeeInDB):
    pass


# CSV Upload model
class CSVUpload(BaseModel):
    event_id: str = ""
    file: bytes


# Authentication models
class Token(BaseModel):
    access_token: str = ""
    token_type: str = ""


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str = ""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str = ""