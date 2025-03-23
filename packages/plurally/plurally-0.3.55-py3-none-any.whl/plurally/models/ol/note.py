from datetime import datetime

from pydantic import ConfigDict, Field, field_validator

from plurally.models.ol.base import BaseModel, parse_datetime


def get_OverloopNoteRead():
    class OverloopNoteRead(BaseModel):
        id: str
        content: str
        created_at: datetime
        updated_at: datetime

        @field_validator("created_at", "updated_at", mode="before")
        def validate_datetime(cls, value):
            return parse_datetime(value)

    return OverloopNoteRead


def get_OverloopNoteCreate():
    class OverloopNoteCreate(BaseModel):
        model_config = ConfigDict(
            json_schema_extra={
                "title": "Create a CRM note",
                "description": "A note to be created in the CRM (could be call notes, meeting notes, etc.)",
            },
        )

        content: str
        title: str

    return OverloopNoteCreate
