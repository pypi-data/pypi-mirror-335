import enum
from contextlib import suppress
from datetime import datetime
from typing import List, Tuple

import requests
from loguru import logger
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from plurally.models.env_vars import BaseEnvVars
from plurally.models.node import Node

BASE_URL = "https://api.overloop.com"


def parse_datetime(datetime_str: str | None):
    if not datetime_str:
        return datetime_str
    try:
        return datetime.fromisoformat(datetime_str)
    except:
        with suppress(ValueError):
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S %z")
    logger.error(f"Unexpected datetime: {datetime_str}")
    return None


class OverloopObjectType(enum.Enum):
    ORGANIZATION = "organization"
    DEAL = "deal"
    PROSPECT = "prospect"
    NOTE = "note"
    TASK = "task"


REQUIRED_ORGANIZATION_PROPERTIES = ("website",)
REQUIRED_DEAL_PROPERTIES = ("stage_id", "title")
REQUIRED_PROSPECT_PROPERTIES = ("email",)
REQUIRED_NOTE_PROPERTIES = ("content",)


OverloopObjectTypeToRoot = {
    OverloopObjectType.ORGANIZATION: "/public/v1/organizations",
    OverloopObjectType.DEAL: "/public/v1/deals",
    OverloopObjectType.PROSPECT: "/public/v1/prospects",
    OverloopObjectType.NOTE: "/private/notes",
    OverloopObjectType.TASK: "/public/v1/tasks",
}


def get_headers(api_key: str):
    return {
        "Authorization": api_key,
        "Content-Type": "application/vnd.api+json; charset=utf-8",
    }


def create_entity(root: str, create_model: BaseModel, api_key: str, model_kls, exclude_fields: List[str] = None):
    payload = {
        "data": {
            "type": root[1:],
            "attributes": create_model.model_dump(exclude_unset=True, exclude=exclude_fields),
        }
    }
    response = requests.post(BASE_URL + root, headers=get_headers(api_key), json=payload)
    try:
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to create {root}: {response.status_code} {response.text}")
        raise e

    if response.status_code == 201:
        entity = response.json()["data"]
        return model_kls(id=entity["id"], **entity["attributes"])
    else:
        logger.error(f"Failed to create {root}: {response.status_code} {response.text}")
        raise RuntimeError(f"Failed to create {root}: {response.status_code} {response.text}")


def update_entity(root: str, entity_id: str, update_model: BaseModel, api_key: str, model_kls, exclude_fields: List[str] = None):
    payload = update_model.model_dump(exclude_unset=True, exclude_none=True, exclude=exclude_fields)
    payload = {
        "data": {
            "type": root[1:],
            "attributes": payload,
        }
    }
    response = requests.put(BASE_URL + f"{root}/{entity_id}", headers=get_headers(api_key), json=payload)
    try:
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to update {root}: {response.status_code} {response.text} {payload=}")
        raise e

    if response.status_code == 200:
        entity = response.json()["data"]
        return model_kls(id=entity["id"], **entity["attributes"])
    else:
        logger.error(f"Failed to update {root}: {response.status_code} {response.text}")
        raise RuntimeError(f"Failed to update {root}: {response.status_code} {response.text}")


def read_entity_by_key_vals(root: str, key_vals: List[Tuple[str, str]], api_key: str, model_kls):
    params = {"filter": ",".join([f"{key}:{val}" for key, val in key_vals])}
    response = requests.get(BASE_URL + root, headers=get_headers(api_key), params=params)

    try:
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to read {root}: {response.status_code} {response.text}")
        raise e

    if response.status_code == 200:
        data = response.json().get("data")
        entity = data[0] if data else None
        if entity:
            return model_kls(id=entity["id"], **entity["attributes"])
        return None
    else:
        logger.error(f"Failed to read {root}: {response.status_code} {response.text}")
        raise RuntimeError(f"Failed to read {root}: {response.status_code} {response.text}")


class OverloopModelBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class OverloopBase(Node):
    ICON = "overloop"

    class EnvVars(BaseEnvVars):
        OVERLOOP_API_KEY: str = Field(
            description="API key for the Overloop API",
            json_schema_extra={"help": "You can find your API keys in your [API page](https://app.overloop.com/integrations/api)"},
        )
