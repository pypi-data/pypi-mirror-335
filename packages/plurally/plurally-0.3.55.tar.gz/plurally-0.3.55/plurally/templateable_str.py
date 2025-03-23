import os
import re
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from plurally.models.jinja_template import get_public_env_vars, load_jinja_template


class TemplateableStr(str):
    def __new__(cls, template: str):
        instance = super().__new__(cls, template)
        instance._template = template  # Store the original template
        return instance

    def __str__(self):
        try:
            return self.expanded()
        except Exception:
            return self.template

    def expanded(self):
        """Returns the expanded string."""
        template = load_jinja_template(self.template)
        return template.render(**get_public_env_vars())

    @property
    def template(self):
        """Returns the raw template string."""
        return self._template

    @template.setter
    def template(self, value):
        self._template = value

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))
