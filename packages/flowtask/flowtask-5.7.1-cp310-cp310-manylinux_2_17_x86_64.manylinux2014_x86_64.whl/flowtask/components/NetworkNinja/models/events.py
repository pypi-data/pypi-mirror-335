from typing import List
from datetime import datetime
from datamodel import BaseModel, Field
from .abstract import AbstractPayload


class EventPosition(BaseModel):
    """
    Event Position Model.
    """
    event_position_id: int = Field(primary_key=True, required=True)
    staff_position_id: int = Field(required=True)
    staff_position_name: str = Field(required=True)
    position_start_time: datetime = Field(required=True)
    position_end_time: datetime = Field(required=True)
    assigned_staff_id: int
    staffing_status: str = Field(required=True)
    position_created_at: datetime = Field(required=True)
    position_updated_at: datetime = Field(required=True)
    position_duration_hours: int = Field(default=1)

class Event(AbstractPayload):
    """
    Event Model.
    """
    event_id: int = Field(primary_key=True, required=True)
    client_id: int
    name: str = Field(required=True)
    start_timestamp: datetime = Field(required=True)
    end_timestamp: datetime = Field(required=True)
    created_at: datetime = Field(required=True)
    updated_at: datetime = Field(required=True)
    program_id: int = Field(required=True)
    duration_hours: int = Field(default=1)
    form_id: int = Field(required=True)
    description: str
    status: str = Field(required=True)
    type: str = Field(required=True)
    program_name: str = Field(required=True)
    store_id: int = Field(required=True)  # "store_id": 5432
    category: str = Field(required=True)
    event_positions: List[EventPosition] = Field(required=False)

    class Meta:
        strict = True
        as_objects = True
        name = 'events'
        schema: str = 'networkninja'
