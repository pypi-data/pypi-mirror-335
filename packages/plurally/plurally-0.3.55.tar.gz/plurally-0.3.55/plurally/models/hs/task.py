import enum
from datetime import datetime

from hubspot.crm.objects import PublicObjectSearchRequest, SimplePublicObjectInput
from pydantic import BaseModel, field_validator

from plurally.models.hs.base import (
    HubspotEntityReadBuilder,
    HubspotModelBase,
    HubspotObjectType,
    associations,
)
from plurally.models.hs.hubspot_crm import HubspotEntityCreateBuilder
from plurally.models.hs.utils import validate_timestamp

DEFAULT_TASK_PROPERTIES = "hs_timestamp,hs_task_body,hs_task_subject,hs_task_status,hs_task_type"
REQUIRED_TASK_PROPERTIES = ("hs_timestamp",)


class HubspotTaskCreateModel(HubspotModelBase): ...


class HubspotTaskReadModel(HubspotModelBase):
    id: str


class HubspotTaskToContactUnique(BaseModel):
    hs_task_subject: str
    contact_email: str


class HubspotTaskStats(enum.Enum):
    COMPLETED = "COMPLETED"
    NOT_STARTED = "NOT_STARTED"


class HubspotTaskPriority(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class HubspotTaskType(enum.Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    LINKED_IN = "LINKED_IN"
    MEETING = "MEETING"
    LINKED_IN_CONNECT = "LINKED_IN_CONNECT"
    LINKED_IN_MESSAGE = "LINKED_IN_MESSAGE"
    TODO = "TODO"


def get_task_validators(properties):
    validators = {}
    if "hs_timestamp" in properties:
        validators["validate_timestamp"] = field_validator("hs_timestamp")(validate_timestamp)
    return validators


_HubspotTasksRead = HubspotEntityReadBuilder.build(
    HubspotObjectType.TASK,
    DEFAULT_TASK_PROPERTIES,
    "tasks",
)


class HubspotTasksRead(_HubspotTasksRead):
    pass


_HubspotTaskCreate = HubspotEntityCreateBuilder.build(
    "task",
    "hs_task_subject",
    DEFAULT_TASK_PROPERTIES,
    "tasks",
    HubspotTaskCreateModel,
    HubspotTaskReadModel,
    SimplePublicObjectInput,
    PublicObjectSearchRequest,
    associations,
    property_required=REQUIRED_TASK_PROPERTIES,
    field_props={
        "hs_timestamp": {"title": "Task Due Date"},
    },
    property_types={
        "hs_timestamp": datetime,
        "hs_task_status": HubspotTaskStats,
        "hs_task_priority": HubspotTaskPriority,
        "hs_task_type": HubspotTaskType,
    },
    get_validators=get_task_validators,
)


class HubspotTaskCreate(_HubspotTaskCreate):
    pass
