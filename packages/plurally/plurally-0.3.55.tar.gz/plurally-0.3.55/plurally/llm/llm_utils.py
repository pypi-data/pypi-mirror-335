import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pytz
from jinja2 import Environment, FileSystemLoader
from loguru import logger
from pydantic import BaseModel, Field, create_model

from plurally.models.jinja_template import get_public_env_vars, load_jinja_template
from plurally.models.misc import File, ImageFile

JINJA_ENV = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))  # Specify the directory with your template


def format_examples(examples: List[dict]) -> str:
    template = JINJA_ENV.get_template("examples.jinja2")
    return template.render(examples=examples)


def format_general_info(general_info: list | None = None) -> str:
    general_info = general_info or []
    tz = os.environ.get("PLURALLY_PUBLIC_PLURALLY_TZ", "Europe/Paris")
    general_info.extend(
        [
            f"Current time and date: {datetime.now(tz=pytz.timezone(tz)).strftime('%A %d. %B %Y %H:%M')} ({tz})",
        ]
    )
    template = JINJA_ENV.get_template("general_info.jinja2")
    return template.render(general_info=general_info)


def build_messages(
    prompt, node_inputs: BaseModel | None, examples: str = "null", general_info: str = "null"
) -> List[Dict[str, str | Dict[str, str]]]:
    for key in ("{PLURALLY_GENERAL_INFO}", "{PLURALLY_EXAMPLES}"):
        if key not in prompt:
            logger.warning(f"You should include {key} in your instructions.")
            prompt += f"\n\n{key}"

    prompt = prompt.replace("{PLURALLY_EXAMPLES}", format_examples(json.loads(examples or "null")))
    prompt = prompt.replace("{PLURALLY_GENERAL_INFO}", format_general_info(json.loads(general_info or "null")))

    # TODO deprecated: please remove
    prompt = prompt.replace("{PLURALLY_OUTPUT_LANGUAGE}", os.environ.get("PLURALLY_OUTPUT_LANGUAGE", "French"))
    # using model_dump could lead to issues as it does not return datetimes as strings for instance

    json_dict_kwargs = {}
    file_keys = []
    if node_inputs:
        file_keys = [k for k in node_inputs.model_fields if issubclass(type(getattr(node_inputs, k)), File)]
        json_dict_kwargs = node_inputs.model_dump(exclude=["run", *file_keys], mode="json")

    json_dict_kwargs.update(get_public_env_vars())
    template = load_jinja_template(prompt)
    prompt = template.render(**json_dict_kwargs)

    content = [
        {"type": "text", "text": prompt},
    ]

    for file_key in file_keys:
        file = getattr(node_inputs, file_key)
        if isinstance(file, ImageFile) and not file.is_empty:
            content.append({"type": "image_url", "image_url": {"url": file.file}})

    return [
        {"role": "user", "content": content},
    ]


def forward_llm(
    response_model: BaseModel,
    model: str,
    messages: List[Dict[str, str]],
    add_explanation: bool = False,
) -> Any:
    global instructor
    import instructor
    from openai import OpenAI

    client = instructor.from_openai(OpenAI())

    if add_explanation:
        if not response_model.model_fields.get("chain_of_thought"):
            response_model = create_model(
                "OutputSchema",
                explanation=(
                    str,
                    Field(
                        "",
                        description="Explain your output.",
                    ),
                ),
                __base__=response_model,
            )
    output = client.chat.completions.create(
        model=model,
        messages=messages,
        response_model=response_model,
        max_retries=3,
        temperature=0,
        top_p=0,
        seed=1234,
    )

    return output
