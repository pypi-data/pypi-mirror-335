from datetime import date, datetime
from enum import Enum
from typing import List, Union

import dateparser
from pydantic import BaseModel, field_validator


class SalesforceSOQLComparisonOperatorSingle(Enum):
    EQUALS = "="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LIKE = "LIKE"


class SalesforceSOQLComparisonOperatorMulti(Enum):
    IN = "IN"
    NOT_IN = "NOT IN"
    INCLUDES = "INCLUDES"
    EXCLUDES = "EXCLUDES"


class SalesforceSOQLLogicalOperator(Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class SalesforceSOQLFilterSingle(BaseModel):
    field: str
    operator: SalesforceSOQLComparisonOperatorSingle
    value: str | int | float | datetime | date

    @field_validator("value", mode="before")
    def check_value(cls, value):
        if isinstance(value, str):
            value = dateparser.parse(value) or value
        return value

    def __str__(self):
        value = self.value
        if isinstance(value, (int, float, datetime, date)):
            if isinstance(value, (datetime, date)):
                # YYYY-MM-DDThh:mm:ss with tz
                value = value.strftime("%Y-%m-%dT%H:%M:%S%z")
            return f"{self.field} {self.operator.value} {value}"
        return f"{self.field} {self.operator.value} '{value}'"


class SalesforceSOQLFilterMulti(BaseModel):
    field: str
    operator: SalesforceSOQLComparisonOperatorMulti
    values: List[str]

    def __str__(self):
        enclosed = [f"'{v}'" for v in self.values]
        return f"{self.field} {self.operator.value} ({', '.join(enclosed)})"


class SalesforceSOQLFilterGroup(BaseModel):
    filters: List[Union["SalesforceSOQLFilterSingle", "SalesforceSOQLFilterMulti"]]
    logical_operator: SalesforceSOQLLogicalOperator = SalesforceSOQLLogicalOperator.AND

    def __str__(self):
        if len(self.filters) == 1:
            return str(self.filters[0])
        joined_filters = f" {self.logical_operator.value} ".join(str(f) for f in self.filters)
        return f"({joined_filters})"


SalesforceSOQLFilter = SalesforceSOQLFilterSingle | SalesforceSOQLFilterMulti | SalesforceSOQLFilterGroup
