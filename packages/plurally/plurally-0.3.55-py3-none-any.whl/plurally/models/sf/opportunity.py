import enum
from datetime import date, datetime, timedelta, timezone
from typing import Type

from simple_salesforce import Salesforce

DEFAULT_OPPORTUNITY_PROPERTIES = "Name,Amount,CloseDate,StageName"
REQUIRED_OPPORTUNITY_PROPERTIES = ("Name", "CloseDate", "StageName")
OPPORTUNITY_PROPERTY_DEFAULTS = {"CloseDate": lambda: (datetime.now(timezone.utc) + timedelta(days=30)).date()}
OPPORTUNITY_PROPERTY_TYPES = {"CloseDate": date, "Amount": float | None}


class SalesforceOpportunityStatus(enum.Enum):
    WON = "won"
    LOST = "lost"
    OPEN = "open"


def get_OpportunityStage_enum(service: Salesforce | None) -> Type[enum.Enum]:
    if service is None:
        return enum.Enum("SalesforceOpportunityStage", {})
    stages = service.query_all("SELECT MasterLabel, ApiName FROM OpportunityStage ORDER BY SortOrder")
    OpportunityStageEnum = enum.Enum(
        "SalesforceOpportunityStage",
        {stage["MasterLabel"]: stage["ApiName"] for stage in stages["records"]},
    )
    return OpportunityStageEnum
