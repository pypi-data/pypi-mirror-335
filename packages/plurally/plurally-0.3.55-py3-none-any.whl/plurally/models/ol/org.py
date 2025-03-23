from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator

from plurally.models import utils
from plurally.models.ol.base import parse_datetime


def get_OverloopOrganizationRead():
    class OverloopOrganizationRead(BaseModel):
        id: int
        name: Optional[str] = None
        website: Optional[str] = None
        description: Optional[str] = None
        email: Optional[str] = None
        phone: Optional[str] = None
        country: Optional[str] = None
        city: Optional[str] = None
        state: Optional[str] = None
        address: Optional[str] = None
        lists: Optional[List[str]] = None
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None

        @field_validator("created_at", "updated_at", mode="before")
        def validate_datetime(cls, value):
            return parse_datetime(value)

    return OverloopOrganizationRead


def get_OverloopOrganizationCreate():
    class OverloopOrganizationCreate(BaseModel):
        @field_validator("website")
        def validate_website(cls, value):
            return utils.get_normalized_domain_from_url(value)

        name: Optional[str] = None
        website: Optional[str] = None
        description: Optional[str] = None
        email: Optional[str] = None
        phone: Optional[str] = None
        country: Optional[str] = None
        city: Optional[str] = None
        state: Optional[str] = None
        address: Optional[str] = None

    return OverloopOrganizationCreate
