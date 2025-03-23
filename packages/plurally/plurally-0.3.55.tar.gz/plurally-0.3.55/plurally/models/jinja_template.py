import os
import uuid
from typing import Any, Dict, List, Optional, Type

import jinja2
from jinja2 import Template, meta
from jinja2schema import infer, to_json_schema
from pydantic import BaseModel, Field, create_model


def json_schema_to_field_defs(json_schema: Dict[str, Any]) -> dict:
    # Extract the field definitions from the schema properties.
    field_definitions = {
        name: json_schema_to_pydantic_field(name, prop, json_schema.get("required", []))
        for name, prop in json_schema.get("properties", {}).items()
    }
    return field_definitions


def json_schema_to_field_defs(json_schema: Dict[str, Any]) -> dict:
    # Extract the field definitions from the schema properties.
    field_definitions = {
        name: json_schema_to_pydantic_field(name, prop, json_schema.get("required", []))
        for name, prop in json_schema.get("properties", {}).items()
    }
    return field_definitions


def json_schema_to_model(json_schema: Dict[str, Any]) -> Type[BaseModel]:
    """
    Converts a JSON schema to a Pydantic BaseModel class.

    Args:
        json_schema: The JSON schema to convert.

    Returns:
        A Pydantic BaseModel class.
    """
    # Extract the model name from the schema title.
    model_name = json_schema.get("title")
    field_definitions = json_schema_to_field_defs(json_schema)
    # Create the BaseModel class using create_model().
    return create_model(model_name, **field_definitions)


def json_schema_to_pydantic_field(name: str, json_schema: Dict[str, Any], required: List[str]) -> Any:
    """
    Converts a JSON schema property to a Pydantic field definition.

    Args:
        name: The field name.
        json_schema: The JSON schema property.

    Returns:
        A Pydantic field definition.
    """

    # Get the field type.
    type_ = json_schema_to_pydantic_type(json_schema)

    # Get the field description.
    description = json_schema.get("description")

    # Get the field examples.
    examples = json_schema.get("examples")

    # Create a Field object with the type, description, and examples.
    # The 'required' flag will be set later when creating the model.
    if name not in required:
        type_ = type_ | None
    return (
        type_,
        Field(
            description=description,
            examples=examples,
            default=... if name in required else None,
        ),
    )


def json_schema_to_pydantic_type(json_schema: Dict[str, Any]) -> Any:
    """
    Converts a JSON schema type to a Pydantic type.

    Args:
        json_schema: The JSON schema to convert.

    Returns:
        A Pydantic type.
    """

    type_ = json_schema.get("type")

    if type_ == "string":
        return str
    elif type_ == "integer":
        return int
    elif type_ == "number":
        return float
    elif type_ == "boolean":
        return bool
    elif type_ == "array":
        items_schema = json_schema.get("items")
        if items_schema:
            item_type = json_schema_to_pydantic_type(items_schema)
            return List[item_type]
        else:
            return List
    elif type_ == "object":
        # Handle nested models.
        properties = json_schema.get("properties")
        if properties:
            nested_model = json_schema_to_model(json_schema)
            return nested_model
        else:
            return Dict
    elif type_ == "null":
        return Optional[Any]  # Use Optional[Any] for nullable fields
    else:
        # TODO: handle anyOf, allOf, oneOf, etc.
        return str
        raise ValueError(f"Unsupported JSON schema type: {type_}")


def get_jinja_filters() -> dict:
    return {}


def get_jinja_globals() -> dict:
    return {"uuid": lambda: uuid.uuid4().hex}


def load_jinja_template(template_str, undefined=jinja2.StrictUndefined) -> jinja2.Template:
    env = jinja2.Environment(undefined=undefined)
    env.filters.update(get_jinja_filters())
    env.globals.update(get_jinja_globals())
    return env.from_string(template_str)


def get_public_env_vars() -> Dict[str, str]:
    env_vars = {}
    for key, val in os.environ.items():
        if key.startswith("PLURALLY_PUBLIC_"):
            env_vars[key.partition("PLURALLY_PUBLIC_")[-1]] = val
    return env_vars


def get_undeclared_vars(source: str, ignore: set = None) -> set:
    env = jinja2.Environment()
    env.filters.update(get_jinja_filters())
    env.globals.update(get_jinja_globals())
    parsed_content = env.parse(source)
    undeclared = set(meta.find_undeclared_variables(parsed_content))
    if ignore:
        undeclared = undeclared - ignore
    return {f"PLURALLY_PUBLIC_{k}" for k in undeclared}


class Jinja2Templater:
    @staticmethod
    def get_input_schema(title, template: str) -> Type[BaseModel]:
        s = infer(template)
        json_schema = to_json_schema(s)
        json_schema["title"] = title
        return json_schema_to_model(json_schema)

    @staticmethod
    def get_field_defs(template) -> dict:
        s = infer(template)
        json_schema = to_json_schema(s)
        return json_schema_to_field_defs(json_schema)

    @staticmethod
    def get_field_defs(template) -> dict:
        s = infer(template)
        json_schema = to_json_schema(s)
        return json_schema_to_field_defs(json_schema)

    @staticmethod
    def render_jinja2_template(template: str, data: dict) -> str:
        template = Template(template)
        return template.render(data)
