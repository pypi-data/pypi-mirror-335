import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from typing import Dict, List, get_origin
from urllib.parse import urlparse

import dateparser
import requests
from loguru import logger
from pydantic import BaseModel, Field, create_model

from plurally.crypto import EncryptionHelper


def is_list_type(schema):
    return hasattr(schema, "annotation") and get_origin(schema.annotation) is list


def get_required_fields(schema):
    required_fields = set()
    for field_name, field in schema.model_fields.items():
        if field.is_required():
            required_fields.add(field_name)
    return required_fields


def create_dynamic_model(
    model_name: str,
    fields: List[str],
    defaults: dict = None,
    types: dict = None,
    titles: dict = None,
    base=None,
):
    fields_map = {}
    defaults = defaults or {}
    types = types or {}
    titles = titles or {}
    for field_name in fields:
        field_type = types.get(field_name, str)
        title = titles.get(field_name)
        if field_name in defaults:  # do not replace by defaults.get(field_name), as None is not the same as ...
            fields_map[field_name] = (
                field_type,
                Field(default=defaults[field_name], title=title),
            )
        else:
            fields_map[field_name] = (field_type, Field(..., title=title))
    return create_model(model_name, **fields_map, __base__=base)


class Link(BaseModel):
    key: str
    label: str
    source: str
    src_handle: str
    target: str
    tgt_handle: str


def serialize_link(link: Dict, input_schemas, output_schemas) -> Dict:
    source = link["source"]
    target = link["target"]

    src_handle_title = output_schemas[source.node_id]["properties"][link["src_handle"]].get("title")
    tgt_handle_title = input_schemas[target.node_id]["properties"][link["tgt_handle"]].get("title")

    label = f"{src_handle_title} -> {tgt_handle_title}"
    return Link(
        **{
            **link,
            "label": label,
            "source": source.node_id,
            "target": target.node_id,
        }
    ).model_dump()


def get_input_schemas(nodes, to_json=True) -> Dict[str, Dict]:
    input_schemas = {}
    for node in nodes:
        input_schemas[node.node_id] = node.InputSchema.model_json_schema() if to_json else node.InputSchema
    return input_schemas


def get_output_schemas(nodes, to_json=True) -> Dict[str, Dict]:
    output_schemas = {}
    for node in nodes:
        output_schemas[node.node_id] = node.OutputSchema.model_json_schema() if to_json else node.OutputSchema
    return output_schemas


def get_naive_datetime(dt):
    if dt.tzinfo:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def get_normalized_domain_from_url(value: str) -> str:
    if not value:
        return value
    value = value.strip().lower()
    parsed = urlparse(value if value.startswith(("http://", "https://")) else f"http://{value}")
    domain = parsed.netloc or parsed.path
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def get_auth_config(scopes):
    token_url = os.environ.get("PLURALLY_REFRESH_TOKEN_URL")
    assert token_url, "PLURALLY_REFRESH_TOKEN_URL must be set in the environment"

    api_key = os.environ.get("PLURALLY_API_KEY")
    assert api_key, "PLURALLY_API_KEY must be set in the environment"

    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    logger.debug(f"Getting access token for scopes {scopes}")
    res = requests.get(
        token_url,
        headers=headers,
        params={"scopes": " ".join(scopes)},
    )
    res.raise_for_status()
    return res.json()


def get_access_token(scopes, token_params: dict = None):
    token_url = os.environ.get("PLURALLY_TOKEN_URL")
    assert token_url, "PLURALLY_TOKEN_URL must be set in the environment"

    api_key = os.environ.get("PLURALLY_API_KEY")
    assert api_key, "PLURALLY_API_KEY must be set in the environment"

    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    logger.debug(f"Getting access token for scopes {scopes}")
    res = requests.get(
        token_url,
        headers=headers,
        params={"scopes": " ".join(scopes), **(token_params or {})},
    )
    res.raise_for_status()
    data = res.json()
    token_expiry = datetime.fromisoformat(data["expires_at"])
    return data["access_token"], token_expiry


def validate_name(name):
    if not name:
        return name
    return name.strip().title()


def get_normalized_domain_from_url(url, return_none_on_error=False):
    if not url:
        if return_none_on_error:
            return None
        return url

    domain_regex = r"^(?:https?:\/\/)?(?:www\.)?([^\/:\?]+)"
    match = re.search(domain_regex, url.strip().lower())
    if match:
        return match.group(1)
    if return_none_on_error:
        return None
    return url


def get_normalized_amount(v):
    if isinstance(v, (int, float)):
        return round(v)
    # if can extract number from string, return that, else return None
    amount_regex = r"(\d+(?:\.\d{1,2})?)"
    match = re.search(amount_regex, v)
    if match:
        return round(match.group(1))
    return None


def validate_datetime(v):
    if not v:
        v = datetime.now()
    if isinstance(v, str):
        parsed = dateparser.parse(v)
        if not parsed:
            logger.warning(f"Could not parse datetime string {v}")
            v = datetime.now()
    elif isinstance(v, (int, float)):
        v = datetime.fromtimestamp(v)
    return v.replace(tzinfo=timezone.utc).isoformat()


def validate_date(v):
    if not v:
        return v
    return datetime.fromisoformat(validate_datetime(v)).date().toisoformat()


def remove_accents(input_str: str) -> str:
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join(char for char in nfkd_form if not unicodedata.combining(char))


def slugify(text):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", re.sub(r"\s", "_", text)).lower()
