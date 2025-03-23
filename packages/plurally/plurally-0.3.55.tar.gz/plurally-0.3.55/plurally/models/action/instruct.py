import os
from collections import Counter
from enum import Enum
from typing import Any, Dict, List

import jinja2
from jinja2 import meta
from loguru import logger
from pydantic import ConfigDict, Field, create_model, model_validator
from pydantic_core import ValidationError

from plurally.json_utils import load_from_json_dict, replace_refs
from plurally.llm.llm_utils import build_messages, forward_llm
from plurally.models.auto import Auto
from plurally.models.env_vars import BaseEnvVars, OpenAiApiKey
from plurally.models.fields import (
    HANDLE_TYPE_FRIENDLY,
    HANDLE_TYPE_MAP,
    NameableHandle,
    get_nameable_fields,
)
from plurally.models.jinja_template import get_undeclared_vars
from plurally.models.misc import Table
from plurally.models.node import Node


class InstructModel(str, Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"


InstructField = Field(
    title="Instructions",
    description="Instructions for the AI model.",
    examples=[
        "Write a response to the incoming email (given by question_asked, person_asking_name), you should output a body and a subject."
    ],
    help="It is best to mention the inputs and outputs in the instructions, e.g. 'Write a response to the incoming email (given by question_asked, person_asking_name), you should output a body and a subject.'",
    min_length=1,
    json_schema_extra={
        "uiSchema": {
            "ui:widget": "textarea",
            "ui:options": {"rows": 10},
            "ui:placeholder": "Write instructions here. Example: Write a response to the incoming email (given by question_asked, person_asking_name), you should output a body and a subject.",
        }
    },
)


class Instruct(Node):
    ICON = "openai"
    PLURALLY_VERSION = 1

    class OutputSchema(Node.OutputSchema):
        key_vals: Dict[str, str]

    class EnvVars(BaseEnvVars):
        OPENAI_API_KEY: str = OpenAiApiKey

    class InputSchema(Node.InputSchema):
        model_config = ConfigDict(json_schema_extra={"can-add-fields": True})

    class InitSchema(Node.InitSchema):
        model: InstructModel = Field(
            InstructModel.GPT_4O,
            title="Model",
            description="The OpenAI model to use.",
            examples=[InstructModel.GPT_4O_MINI.value],
            json_schema_extra={"advanced": True},
        )
        is_table: bool = Field(
            False,
            title="Table Output",
            description="Whether the output is a table. For instance, if you want ChatGPT to output a list of outputs with the same columns, you should tick this.",
            examples=[True, False],
            json_schema_extra={
                "advanced": True,
                "uiSchema": {"ui:widget": "hidden"},
            },  # deprecated
        )

        input_fields: List[NameableHandle] = get_nameable_fields(
            title="Inputs",
            description="The different inputs of the AI model. For instance if you want to write an automatic support email, your inputs might be: like 'Question asked', 'Name of person asking'. Be sure to mention them in your instructions (see examples).",
            examples=["Question asked", "Name of person asking"],
            placeholder="Enter input name, example: Question asked",
            default_factory=list,
            json_schema_extra_extra={"is_input": True, "name_singular": "Input"},
        )
        instruct: str = InstructField
        output_fields: List[NameableHandle] = get_nameable_fields(
            title="Outputs",
            description="The different output attributes of the AI model. For instance if you want to write a support email, your outputs might be: like 'Email subject' and 'Email body'. Be sure to mention them in your instructions (see examples).",
            min_length=1,
            examples=["Email Subject", "Email Body"],
            placeholder="Enter output name, example: Email Subject",
            json_schema_extra_extra={"is_output": True, "name_singular": "Output"},
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

        add_chain_of_thought: bool = Field(
            False,
            title="Add Chain of Thought",
            json_schema_extra={"advanced": True},
        )
        add_explanation: bool = Field(
            False,
            title="Add Explanation",
            json_schema_extra={"advanced": True},
        )

        @model_validator(mode="after")
        def ckeck_model(cls, values):
            if len(set(field._clean for field in values.input_fields)) != len(values.input_fields):
                raise ValueError("Input fields must be unique")
            if len(set(field._clean for field in values.output_fields)) != len(values.output_fields):
                raise ValueError("Output fields must be unique")
            return values

        # @field_validator("examples", mode="before")
        # def check_examples(cls, value):
        #     if isinstance(value, list):
        #         value = json.dumps(value, indent=2)
        #     try:
        #         loaded = json.loads(value)
        #         assert not loaded or isinstance(loaded, list), "Examples must be a list of dictionaries."
        #         if loaded:
        #             for example in loaded:
        #                 assert isinstance(example, dict), "Each example must be a dictionary."
        #     except json.JSONDecodeError:
        #         raise ValueError("Examples must be in JSON format.")
        #     return value

        # @field_validator("general_info", mode="before")
        # def check_general_info(cls, value):
        #     if isinstance(value, list):
        #         value = json.dumps(value, indent=2)
        #     try:
        #         loaded = json.loads(value)
        #         assert not loaded or isinstance(loaded, list), "General information must be a list of strings."
        #         if loaded:
        #             for info in loaded:
        #                 assert isinstance(info, str), "Each general information must be a string."
        #     except json.JSONDecodeError:
        #         raise ValueError("General information must be in JSON format.")
        #     return value

    InitSchema.__doc__ = """Instruct an AI model to perform a task."""
    DESC = InitSchema.__doc__

    def __init__(
        self,
        init_inputs: InitSchema,
    ) -> None:
        self.is_table = init_inputs.is_table
        self._client = None  # lazy init
        self.model = init_inputs.model
        self.instruct = init_inputs.instruct
        self.examples = init_inputs.examples
        self.general_info = init_inputs.general_info

        self._input_fields = init_inputs.input_fields
        self._output_fields = init_inputs.output_fields
        self.add_chain_of_thought = init_inputs.add_chain_of_thought
        self.add_explanation = init_inputs.add_explanation

        super().__init__(init_inputs)

    def _set_schemas(self) -> None:
        # create pydantic model from output_fields
        out_fields_map = {}
        for field in self.output_fields:
            field_type = HANDLE_TYPE_MAP[field.type]
            json_schema_extra = {"handle_id": field.handle_id}

            type_friendly = HANDLE_TYPE_FRIENDLY.get(field.type)
            if type_friendly:
                json_schema_extra["type-friendly"] = type_friendly

            out_fields_map[field._clean] = (
                field_type,
                Field(
                    ...,
                    title=field.free,
                    json_schema_extra=json_schema_extra,
                ),
            )
        self.instruct_schema = create_model(
            "OutputSchema",
            **out_fields_map,
            __config__=ConfigDict(json_schema_extra={"can-add-fields": True}),
        )

        if self.is_table:
            self.instruct_schema = List[self.instruct_schema]

            class OutputSchema(Node.OutputSchema):
                data: Table = Field(
                    description=f"The ouputs converted to a table, columns are the output fields: {[o._clean for o in self.output_fields]}.",
                )

            self.OutputSchema = OutputSchema

        else:
            self.OutputSchema = self.instruct_schema

        # create pydantic model from input_fields
        in_fields_map = {}
        for field in self.input_fields:
            field_type = HANDLE_TYPE_MAP[field.type]
            json_schema_extra = {"handle_id": field.handle_id}
            type_friendly = HANDLE_TYPE_FRIENDLY.get(field.type)
            if type_friendly:
                json_schema_extra["type-friendly"] = type_friendly
            in_fields_map[field._clean] = (
                field_type,
                Field(
                    ...,
                    title=field.free,
                    json_schema_extra=json_schema_extra,
                ),
            )
        self.InputSchema = create_model(
            "InputSchema",
            **in_fields_map,
            __base__=Instruct.InputSchema,
        )
        assert self.InputSchema.model_json_schema()["can-add-fields"]

    @property
    def output_fields(self):
        return self._output_fields

    @output_fields.setter
    def output_fields(self, value):
        value = [v if isinstance(v, NameableHandle) else NameableHandle(**v) for v in value]
        assert len(set(field._clean for field in value)) == len(value), f"Output fields must be unique {value}"
        self._output_fields = value
        self._set_schemas()
        self.src_handles = self._get_handles(self.OutputSchema, None)

    @property
    def input_fields(self):
        return self._input_fields

    @input_fields.setter
    def input_fields(self, value):
        value = [v if isinstance(v, NameableHandle) else NameableHandle(**v) for v in value]
        assert len(set(field._clean for field in value)) == len(value), f"Input fields must be unique {value}"
        self._input_fields = value
        self._set_schemas()
        self.tgt_handles = self._get_handles(self.InputSchema, None)

    @property
    def client(self):
        global instructor
        import instructor

        global OpenAI
        from openai import OpenAI

        if self._client is None:
            self._client = instructor.from_openai(OpenAI())
        return self._client

    def create(self, messages: List[Dict[str, str]]) -> Any:
        model_override = os.environ.get("OPENAI_MODEL")
        model = self.model
        if model_override:
            logger.info(f"Found override for OPENAI_MODEL: {model_override}, using it.")
            model = model_override

        response_model = self.instruct_schema
        if self.add_explanation:
            if not response_model.model_fields.get("explanation"):
                response_model = create_model(
                    "OutputSchema",
                    explanation=(
                        str,
                        Field(
                            "",
                            description="Explain your reasoning.",
                        ),
                    ),
                    __base__=response_model,
                )
        if self.add_chain_of_thought:
            if not response_model.model_fields.get("chain_of_thought"):
                response_model = create_model(
                    "OutputSchema",
                    chain_of_thought=(
                        str,
                        Field(
                            "",
                            description="Think step by step to determine the output.",
                        ),
                    ),
                    __base__=response_model,
                )

        output = self.client.chat.completions.create(
            model=model,
            messages=messages,
            response_model=response_model,
            max_retries=3,
            temperature=0,
            top_p=0,
            seed=1234,
        )
        return output

    def forward(self, node_input) -> Any:
        messages = build_messages(self.instruct, node_input, self.examples, self.general_info)
        try:
            output = forward_llm(
                response_model=self.OutputSchema,
                model=self.model,
                messages=messages,
                add_explanation=self.add_explanation,
            )
        except ValidationError as e:
            raise ValueError(f"Error from OpenAI: {e}")

        if self.is_table:
            self.outputs["data"] = Table(data=[o.model_dump() for o in output])
        else:
            self.outputs = output.model_dump()

    def serialize(self) -> dict:
        return {
            **super().serialize(),
            "instruct": self.instruct,
            "output_fields": [o.model_dump() for o in self.output_fields],
            "input_fields": [i.model_dump() for i in self.input_fields],
            "output_schema": replace_refs(self.OutputSchema.model_json_schema()),
            "input_schema": replace_refs(self.InputSchema.model_json_schema()),
            "is_table": self.is_table,
            "model": self.model,
            "examples": self.examples,
            "general_info": self.general_info,
        }

    @classmethod
    def _parse(cls, **kwargs):
        kwargs = load_from_json_dict(kwargs)
        kwargs["output_fields"] = [NameableHandle(**o) for o in kwargs["output_fields"]]
        kwargs["input_fields"] = [NameableHandle(**i) for i in kwargs["input_fields"]]
        return cls(cls.InitSchema(**kwargs))

    def get_issues(self, graph):
        num_output_connections = Counter()
        for field_name, field in self.OutputSchema.model_fields.items():
            if field.annotation is Auto:
                num_output_connections[field_name] = 0
                # if there already is a connection, raise
                for _, _, key in graph.out_edges(self, data=True):
                    if key["src_handle"] == field_name:
                        num_output_connections[field_name] += 1
        issues = []
        for field_name, count in num_output_connections.items():
            if count > 1:
                title = self.OutputSchema.model_fields[field_name].title
                issues.append(f"Auto Output {title} has multiple connections: {count}")
            elif count == 0:
                title = self.OutputSchema.model_fields[field_name].title
                issues.append(f"Auto Output {title} has no connection")
        return issues

    def add_target_handle(self, src_handle):
        """
        src_handle is the handle that one wants to connect to the node while adding a tgt_handle
        """
        new_tgt_handle = NameableHandle(free=src_handle)
        ix = 1
        while new_tgt_handle._clean in [i._clean for i in self.input_fields]:
            new_tgt_handle = NameableHandle(free=new_tgt_handle.free + f" {ix}")
        self.input_fields = [*self.input_fields, new_tgt_handle]
        return new_tgt_handle._clean

    def add_source_handle(self, tgt_handle):
        """
        tgt_handle is the handle that one wants to connect to the node while adding a src_handle
        """
        new_src_handle = NameableHandle(free=tgt_handle)
        ix = 1
        while new_src_handle._clean in [i._clean for i in self.output_fields]:
            new_src_handle = NameableHandle(free=new_src_handle.free + f" {ix}")
        self.output_fields = [*self.output_fields, new_src_handle]
        return new_src_handle._clean

    def get_necessary_env_vars(self):
        necessary_env_vars = {"OPENAI_API_KEY"}
        ignore = {field.free for field in self.input_fields}
        return necessary_env_vars.union(get_undeclared_vars(self.instruct, ignore=ignore))
