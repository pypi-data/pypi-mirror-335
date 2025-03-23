from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from plurally.models.ol.base import parse_datetime


def get_OverloopProspectRead():
    class OverloopProspectRead(BaseModel):
        id: int
        email: Optional[str] = None
        first_name: Optional[str] = None
        last_name: Optional[str] = None
        description: Optional[str] = None
        jobtitle: Optional[str] = None
        linkedin_profile: Optional[str] = None
        phone: Optional[str] = None
        title: Optional[str] = None
        country: Optional[str] = None
        state: Optional[str] = None
        city: Optional[str] = None
        industry: Optional[str] = None
        created_from: Optional[str] = None
        last_emailed_at: Optional[datetime] = None
        excluded: Optional[bool] = None
        opened: Optional[bool] = None
        opened_at: Optional[datetime] = None
        open_count: Optional[int] = None
        clicked: Optional[bool] = None
        clicked_at: Optional[datetime] = None
        click_count: Optional[int] = None
        replied: Optional[bool] = None
        replied_at: Optional[datetime] = None
        email_reply_count: Optional[int] = None
        linkedin_reply_count: Optional[int] = None
        bounced: Optional[bool] = None
        url: Optional[str] = None
        lists: Optional[List[str]] = None
        email_status: Optional[str] = None
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None

        @field_validator("created_at", "updated_at", "last_emailed_at", "opened_at", "clicked_at", "replied_at", mode="before")
        def validate_datetime(cls, value):
            return parse_datetime(value)

    return OverloopProspectRead


def get_OverloopProspectCreate():
    class OverloopProspectCreate(BaseModel):
        model_config = ConfigDict(
            title="OverloopProspectCreate",
            description="Create a new prospect in Overloop. Either email or first_name + last_name is required.",
        )

        @model_validator(mode="before")
        def validate_email_or_name(cls, values):
            if not values.get("email") and not (values.get("first_name") and values.get("last_name")):
                raise ValueError("Either email or first_name + last_name must be provided")
            return values

        email: Optional[str] = None
        first_name: Optional[str] = None
        last_name: Optional[str] = None
        phone: Optional[str] = None
        description: Optional[str] = None
        jobtitle: Optional[str] = None
        linkedin_profile: Optional[str] = None
        country: Optional[str] = None
        state: Optional[str] = None
        city: Optional[str] = None
        industry: Optional[str] = None

    return OverloopProspectCreate
