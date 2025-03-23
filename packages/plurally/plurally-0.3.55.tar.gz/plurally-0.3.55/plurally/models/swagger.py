import importlib
import json
import os
import sys
from collections import defaultdict
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Literal, Optional

import dpath
import requests
import yaml
from datamodel_code_generator import DataModelType, generate
from loguru import logger
from pydantic import ConfigDict, Field, create_model

from plurally.auth.oauth import Oauth2Authenticator
from plurally.json_utils import load_from_json_dict, replace_refs
from plurally.llm.llm_utils import build_messages, forward_llm
from plurally.models.action.instruct import InstructModel
from plurally.models.env_vars import BaseEnvVars, OpenAiApiKey
from plurally.models.fields import NameableHandle, NameableInputFields, get_nameable_fields
from plurally.models.jinja_template import get_undeclared_vars
from plurally.models.node import Node
from plurally.models.utils import get_auth_config
from plurally.specs.security_schemes import get_security_schemes


def get_type_from_json_schema(schema: Dict[str, Any] | str):
    """Convert a JSON Schema type definition to a Python type annotation."""
    if isinstance(schema, str):
        schema = {"type": schema}
    if "anyOf" in schema:
        # Recursively handle multiple types in anyOf
        types = [get_type_from_json_schema(sub_schema) for sub_schema in schema["anyOf"]]
        t0 = types[0]
        for t in types[1:]:
            t0 |= t
        return t0
    if schema.get("type") == "string":
        if schema.get("enum"):
            return Literal[tuple(schema["enum"])]
        return str
    elif schema.get("type") == "integer":
        return int
    elif schema.get("type") == "number":
        return float
    elif schema.get("type") == "boolean":
        return bool
    elif schema.get("type") == "null" or schema.get("type") is None:
        return None
    elif schema.get("type") == "array":
        return List[get_type_from_json_schema(schema["items"])]
    elif schema.get("type") == "object":
        if schema.get("additionalProperties") is not None:
            return Dict[str, get_type_from_json_schema(schema["additionalProperties"])]
        raise ValueError(f"Unsupported object schema: {schema}")
    raise ValueError(f"Unsupported type: {schema.get('type')}")


def get_payload_kls(method_schema):
    is_required = dpath.get(method_schema, "requestBody/required", default=False)
    schema = dpath.get(method_schema, "requestBody|content|application/json|schema", "|", default=None)
    if dpath.get(method_schema, "requestBody|content|multipart/form-data", "|", default=None):
        raise NotImplementedError("Multipart form data is not supported")

    if schema:
        with NamedTemporaryFile(suffix="_tmp.py", delete=False) as tmpfile:
            output = Path(tmpfile.name)

            generate(
                json.dumps(schema),
                output=output,
                class_name="Payload",
                output_model_type=DataModelType.PydanticV2BaseModel,
            )
            module_name = f"temp_model_payload"
            spec = importlib.util.spec_from_file_location(module_name, output)
            module = importlib.util.module_from_spec(spec)

            sys.modules[module_name] = module
            try:
                spec.loader.exec_module(module)
                payload_kls = getattr(module, "Payload")
                return payload_kls, is_required
            except Exception as e:
                raise ValueError(f"Error loading generated schema: {e}") from e
            finally:
                sys.modules.pop(module_name, None)
                output.unlink(missing_ok=True)
    return None, False


def get_response_kls(method_schema):
    for rc in ("200", "201"):
        schema = dpath.get(method_schema, f"responses|{rc}|content|application/json|schema", separator="|", default=None)
        if schema:
            break
    else:
        raise ValueError("Response schema not found")
    with NamedTemporaryFile(suffix="_tmp.py", delete=False) as tmpfile:
        output = Path(tmpfile.name)

        generate(
            json.dumps(schema),
            output=output,
            class_name="Payload",
            output_model_type=DataModelType.PydanticV2BaseModel,
        )
        module_name = f"temp_model_payload"
        spec = importlib.util.spec_from_file_location(module_name, output)
        module = importlib.util.module_from_spec(spec)

        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
            payload_kls = getattr(module, "Payload")
            return payload_kls
        except Exception as e:
            raise ValueError(f"Error loading generated schema: {e}") from e
        finally:
            sys.modules.pop(module_name, None)
            output.unlink(missing_ok=True)


def load_swagger(swagger: str | dict) -> dict:
    if isinstance(swagger, dict):
        loaded_swagger = swagger
    try:
        loaded_swagger = yaml.safe_load(swagger)
    except yaml.YAMLError as e:
        try:
            loaded_swagger = json.loads(swagger)  # type: ignore
        except json.JSONDecodeError as e:
            raise ValueError(f"swagger must be a valid yaml or json string") from e

    if len(loaded_swagger.get("servers", [])) != 1:
        raise ValueError("swagger must have exactly one server")

    return replace_refs(loaded_swagger)


class Swagger(Node, NameableInputFields):
    class EnvVars(BaseEnvVars):
        OPENAI_API_KEY: str = OpenAiApiKey

    class InitSchema(Node.InitSchema):
        swagger: str = Field(
            ...,
            description="The OpenAPI specification in JSON or YAML format.",
            json_schema_extra={"uiSchema": {"ui:widget": "textarea", "ui:options": {"rows": 10}}},
        )

        input_fields: List[NameableHandle] = get_nameable_fields(
            title="Inputs",
            description="The different inputs of the AI model.",
            default_factory=list,
            json_schema_extra_extra={"is_input": True, "name_singular": "Input"},
        )

        prompt: str = Field(
            ...,
            description="The prompt to send to the model.",
            json_schema_extra={"uiSchema": {"ui:widget": "textarea", "ui:options": {"rows": 10}}},
        )
        model: InstructModel = Field(
            InstructModel.GPT_4O,
            title="Model",
            description="The OpenAI model to use.",
            examples=[InstructModel.GPT_4O_MINI.value],
            json_schema_extra={"advanced": True},
        )
        add_explanation: bool = Field(
            False,
            json_schema_extra={"advanced": True},
        )
        examples: str = Field(
            "",
            description="Examples in JSON format (list of dicts)",
            json_schema_extra={"uiSchema": {"ui:widget": "textarea", "ui:options": {"rows": 10}}},
        )
        general_info: str = Field(
            "",
            description="General information in JSON format (list of strings)",
            json_schema_extra={"uiSchema": {"ui:widget": "textarea", "ui:options": {"rows": 10}}},
        )

    class InputSchemaBase(Node.InputSchema):
        model_config = ConfigDict(json_schema_extra={"can-add-fields": True})

    def __init__(self, init_inputs):
        self.renamable_input_fields = NameableInputFields(init_inputs.input_fields, Swagger.InputSchemaBase, "input_fields")
        self.prompt = init_inputs.prompt
        self.examples = init_inputs.examples
        self.general_info = init_inputs.general_info
        self.add_explanation = init_inputs.add_explanation
        self.model = init_inputs.model
        self.response_model = None
        self.swagger = init_inputs.swagger  # order matters
        super().__init__(init_inputs)

    @property
    def input_fields(self):
        return self.renamable_input_fields.values

    @input_fields.setter
    def input_fields(self, value):
        self.renamable_input_fields.values = value

    @property
    def InputSchema(self):
        return self.renamable_input_fields.InputSchema

    @InputSchema.setter
    def InputSchema(self, value):
        self.renamable_input_fields.InputSchema = value

    @property
    def tgt_handles(self):
        return self.renamable_input_fields.tgt_handles

    @tgt_handles.setter
    def tgt_handles(self, value):
        self.renamable_input_fields.tgt_handles = value

    @property
    def swagger(self):
        return self._swagger

    @swagger.setter
    def swagger(self, swagger: str | dict):
        self._swagger = load_swagger(swagger)
        self._set_schemas()

    def _create_response_model(self):
        fields = {}
        self.ops = {}
        for path, methods in self.swagger.get("paths", {}).items():
            for method, method_schema in methods.items():
                method_fields = {}
                payload_kls, is_payload_required = get_payload_kls(method_schema)
                class_name = f"{method_schema.get('operationId', '').capitalize()}{method.capitalize()}"

                for param_def in method_schema.get("parameters", []):
                    param_name = param_def.get("name")
                    param_schema = param_def.get("schema")
                    if not param_schema:
                        raise ValueError(f"Parameter schema not found for {param_def}")
                    if method_fields.get(param_name):
                        raise ValueError(f"Duplicate parameter name: {param_name}")
                    ptype = get_type_from_json_schema(param_schema)
                    default = ...
                    if not param_def.get("required"):
                        default = None
                        ptype = Optional[ptype]
                    method_fields[param_name] = (ptype, Field(default, description=param_def.get("description"), title=param_name))

                if payload_kls:
                    if method_fields.get("payload"):
                        raise ValueError("Reserved field name: payload already exists")
                    default = ...
                    if not is_payload_required:
                        default = None
                        payload_kls = Optional[payload_kls]
                    method_fields["payload"] = (payload_kls, Field(default, title="Payload"))

                method_schema_kls = create_model(class_name, **method_fields, __doc__=method_schema.get("summary"))
                fields[class_name] = (List[method_schema_kls], Field(None))
                self.ops[class_name] = (path, method)

        if self.add_explanation:
            fields["explanation"] = (str, Field("", description="Explain your output.", title="Explanation"))

        return create_model("Response", **fields)

    def _create_output_schema(self):
        fields = {}
        for class_name, (path, method) in self.ops.items():
            method_schema = self.swagger["paths"][path][method]
            resp_kls = get_response_kls(method_schema)
            fields[f"{path}_{method}"] = (List[resp_kls], Field([], description=resp_kls.__doc__, title=f"{path}_{method}"))

        if self.add_explanation:
            fields["explanation"] = (str, Field("", description="Explain your output.", title="Explanation"))

        return create_model("OutputSchema", **fields, __base__=Swagger.OutputSchema)

    def _set_schemas(self):
        self.renamable_input_fields.set_schemas()
        self.response_model = self._create_response_model()
        self.OutputSchema = self._create_output_schema()

    def build_session(self):
        session = requests.Session()
        scopes = self.get_scopes_and_meta_data()
        if len(scopes) > 1:
            raise NotImplementedError("Multiple scopes are not supported")

        cfg = get_auth_config(scopes[0][0])
        if cfg.pop("auth_type", None) == "oauth2":
            session.auth = Oauth2Authenticator(**cfg)
        return session

    def _forward_llm(self, node_inputs):
        messages = build_messages(self.prompt, node_inputs, self.examples, self.general_info)
        output = forward_llm(self.response_model, self.model, messages, self.add_explanation)
        return output

    def _forward(self, session: requests.Session, node_inputs):
        outputs = defaultdict(list)
        output = self._forward_llm(node_inputs)
        for class_name, (path, method) in self.ops.items():
            for payload in getattr(output, class_name, None) or []:
                query_params = set(payload.model_fields) - {"payload"}
                query_params = {k: getattr(payload, k) for k in query_params}
                url = self.swagger["servers"][0]["url"] + path
                json_args = payload.model_dump(mode="json")
                response = session.request(method, url, json=json_args.get("payload"), params=query_params)
                response.raise_for_status()
                outputs[f"{path}_{method}"].append(response.json())

        self.outputs = dict(outputs)
        if self.add_explanation:
            self.outputs["explanation"] = output.explanation

    def forward(self, node_inputs):
        session = self.build_session()
        try:
            self._forward(session, node_inputs)
        finally:
            session.close()

    def add_target_handle(self, src_handle):
        return self.renamable_input_fields.add_target_handle(src_handle)

    def serialize(self):
        return (
            super().serialize()
            | {
                "swagger": yaml.dump(self.swagger),
                "prompt": self.prompt,
                "examples": self.examples,
                "general_info": self.general_info,
                "add_explanation": self.add_explanation,
                "model": self.model,
                "output_schema": replace_refs(self.OutputSchema.model_json_schema()),
            }
            | self.renamable_input_fields.serialize()
        )

    @classmethod
    def _parse(cls, **kwargs):
        kwargs = load_from_json_dict(kwargs)
        NameableInputFields.parse(kwargs, Swagger.InputSchemaBase, "input_fields")
        return cls(cls.InitSchema(**kwargs))

    def get_scopes_and_meta_data(self):
        outputs = []
        sec_schemes = dpath.get(self.swagger, "components/securitySchemes", default={})
        sec_schemes.update(get_security_schemes())
        for path_data in self.swagger["paths"].values():
            for method_data in path_data.values():
                for sec_data in method_data.get("security", []):
                    for sec_schema_name, sec_scopes in sec_data.items():
                        if sec_schemes[sec_schema_name].get("type") == "oauth2":
                            outputs.append((sec_scopes, {"securityScheme": sec_schemes[sec_schema_name]}))
        return outputs

    def get_necessary_env_vars(self):
        necessary_env_vars = {"OPENAI_API_KEY"}
        ignore = {field.free for field in self.input_fields}
        env_vars = get_undeclared_vars(self.prompt, ignore=ignore)
        # rm the ones that are provided by inputs
        return necessary_env_vars.union(env_vars)


__all__ = ["Swagger"]
