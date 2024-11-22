from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    name: str
    description: str
    start_time: time
    end_time: time
    date: date


class EventResponse(BaseModel):
    name: str
    description: str
    start_time: time
    end_time: time
    date: date


class EventUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the event")
    description: Optional[str] = Field(None, description="Description of the event")
    start_time: Optional[time] = Field(None, description="Start time of the event")
    end_time: Optional[time] = Field(None, description="End time of the event")
    # date: Optional[date] = Field(None, description="Date of the event")
