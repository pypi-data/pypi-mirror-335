import enum
from datetime import datetime
from typing import Optional

import requests
from pydantic import BaseModel, ConfigDict, computed_field, field_validator

from plurally.models import utils
from plurally.models.ol.base import BASE_URL, create_entity, get_headers, parse_datetime


class OverloopDealStage(BaseModel):
    id: str
    name: str
    probability: int


class OverloopDealStatus(enum.Enum):
    WON = "won"
    LOST = "lost"
    OPEN = "open"


def get_stages(api_key: str) -> list[OverloopDealStage]:
    stages = requests.get(BASE_URL + "/public/v1/stages", headers=get_headers(api_key))
    stages.raise_for_status()

    stage_objs = []
    for stage in stages.json()["data"]:
        stage_objs.append(OverloopDealStage(id=stage["id"], **stage["attributes"]))
    return stage_objs


def get_OverloopDealRead():
    class OverloopDealRead(BaseModel):
        model_config = ConfigDict(
            title="Deal",
            description="Read a deal in Overloop.",
            use_enum_values=True,
        )

        id: int
        title: Optional[str] = None
        value: Optional[float] = None
        status: OverloopDealStatus = OverloopDealStatus.OPEN.value
        closed_at: Optional[datetime] = None
        expected_close_date: Optional[datetime] = None
        entered_stage_at: Optional[datetime] = None
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None

        @field_validator(
            "closed_at",
            "expected_close_date",
            "entered_stage_at",
            "created_at",
            "updated_at",
            mode="before",
        )
        def validate_datetime(cls, value):
            return parse_datetime(value)

    return OverloopDealRead


def get_OverloopDealCreate(api_key: str | None):
    stages = get_stages(api_key) if api_key else []
    stages_per_enum_value = {stage.name: stage.id for stage in stages}
    DealStageEnum = enum.Enum("OverloopDealStage", {stage.name.upper(): stage.name for stage in stages}) if stages else None

    class OverloopDealCreate(BaseModel):
        model_config = ConfigDict(
            title="Deal",
            description="Create a new deal in Overloop.",
            use_enum_values=True,
        )

        @field_validator("value", mode="before")
        def validate_value(cls, value):
            return utils.get_normalized_amount(value)

        stage: DealStageEnum = list(stages_per_enum_value)[0] if stages else None  # type: ignore
        title: Optional[str] = None
        value: Optional[float] = None
        status: OverloopDealStatus = OverloopDealStatus.OPEN.value

        @computed_field(return_type=int)
        def stage_id(self):
            stage = DealStageEnum(self.stage)
            return stages_per_enum_value[stage.value]

    return OverloopDealCreate
