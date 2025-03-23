import base64
import os
import time
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import List

import requests
from loguru import logger
from pydantic import BaseModel, Field

from plurally.models.env_vars import BaseEnvVars
from plurally.models.node import Node

EXAMPLE_SUMMARY_OF_CALL = """In the sales call, Alice from CoolCompany introduced their ergonomic office chair line to John from SupaCompany, emphasizing how the chairs could improve employee comfort, productivity, and overall wellness. Alice highlighted key features such as customizable lumbar support, adjustable armrests, and breathable materials, tailored to meet the needs of modern office environments. After discussing SupaCompany's specific office setup and employee feedback, John showed interest in the solution. Alice then outlined the pricing, stating that the chairs would be available at $15,000 for the required quantity. They agreed to reconvene next week to finalize the purchase details.""".strip()


def get_basic_auth_header(username, password):
    return {"Authorization": "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()}


LEEXI_BASE_URL = "https://public-api.leexi.ai/v1"
LEEXI_DT_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"


class LeexiSpeaker(BaseModel):
    name: str = Field(description="Name of the speaker")
    email: str = Field("", description="Email of the speaker")
    phone_number: str = Field("", description="Phone number of the speaker", title="Phone number")


class Leexi(Node):
    IS_TRIGGER = True
    ICON = "leexi"

    class EnvVars(BaseEnvVars):
        LEEXI_API_KEY: str = Field(
            description="API key for the Leexi API",
            json_schema_extra={
                "help": "You can generate an API key/secret pair by going to [Leexi → Settings → Company Settings → API Keys](https://app.leexi.ai/settings/api_keys), and clicking on add (requires a Leexi admin account)."
            },
        )
        LEEXI_SECRET: str = Field(
            description="Secret for the Leexi API",
            json_schema_extra={"help": "[Leexi → Settings → Company Settings → API Keys](https://app.leexi.ai/settings/api_keys)."},
        )

    class InitSchema(Node.InitSchema):
        """
        This flow will be triggered as soon as a new recording is finished being processed by Leexi and there is a summary available. Leexi does not provide summaries for calls shorter than 90 seconds or calls longer than 3 hours.
        """

    class InputSchema(Node.InputSchema):
        pass

    class OutputSchema(Node.OutputSchema):
        summary: str = Field(
            description="Summary of the call",
            json_schema_extra={
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": "Summary of the call",
                },
                "example-default": EXAMPLE_SUMMARY_OF_CALL,
            },
        )
        speakers: List[LeexiSpeaker] = Field(
            [],
            title="Speakers",
            description="People who spoke during the call",
            json_schema_extra={
                "name_singular": "Speaker",
                "uiSchema": {"ui:label": False, "items": {"ui:label": False}},
                "example-default": [
                    {"name": "Alice Gold", "email": "alice@coolcompany.com"},
                    {"name": "John Doe", "email": "john@supacompany.com"},
                ],
            },
        )
        follow_up_tasks: List[str] = Field(
            [],
            description="Follow-up tasks",
            json_schema_extra={
                "name_singular": "Follow-up task",
                "uiSchema": {"ui:label": False, "items": {"ui:label": False}},
                "example-default": [
                    "Send the pricing details to John",
                    "Schedule a follow-up call with John",
                ],
            },
        )
        performed_at: datetime = Field(description="Time when the call was performed")

    def __init__(self, node_inputs: InitSchema):
        if os.environ.get("PLURALLY_START_ISO_TIMESTAMP"):
            self.check_after = datetime.fromisoformat(os.environ["PLURALLY_START_ISO_TIMESTAMP"])
        else:
            self.check_after = datetime.now(timezone.utc).replace(tzinfo=None)
        self.next_check_after = None
        super().__init__(node_inputs)

    def get_auth_header(self):
        api_key = os.environ.get("LEEXI_API_KEY")
        assert api_key, "LEEXI_API_KEY is required"

        secret = os.environ.get("LEEXI_SECRET")
        assert secret, "LEEXI_SECRET is required"
        return get_basic_auth_header(api_key, secret)

    def callback(self):
        super().callback()
        if self.next_check_after:
            self.check_after = self.next_check_after
            self.next_check_after = None

    @lru_cache(maxsize=1)
    def get_calls(self, check_after, ttl_hash):
        url = LEEXI_BASE_URL + "/calls"
        calls = requests.get(
            url,
            headers=self.get_auth_header(),
            params={
                "items": 100,
                "from": check_after.strftime(LEEXI_DT_FMT),
                "order": "created_at asc",
            },
        )
        try:
            calls.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                raise RuntimeError("Leexi API error: Unauthorized. Please check your API key and secret.")
        res = calls.json()
        if res.get("success") is False:
            raise RuntimeError(f"Leexi API error: {res.get('message')}")
        return res

    @staticmethod
    def _get_follow_up_tasks(call):
        follow_up_tasks = []
        for prompt in call.get("prompts", []):
            if prompt.get("title") == "follow-up tasks":
                completions = prompt.get("completions")
                if isinstance(completions, list):
                    for completion in completions:
                        follow_up_tasks.append(completion)
        return follow_up_tasks

    def forward(self, *args, **kwargs):
        self.outputs = None
        calls = self.get_calls(self.check_after, ttl_hash=time.time() // 60)  # 1 minute TTL
        calls = calls.get("data")
        if calls:
            for call in calls:
                follow_up_tasks = self._get_follow_up_tasks(call)

                if call.get("summary"):
                    logger.debug("Found call with summary")
                    self.next_check_after = datetime.strptime(call["created_at"], LEEXI_DT_FMT) + timedelta(seconds=1)
                    self.outputs = self.OutputSchema(
                        summary=call["summary"],
                        speakers=[
                            LeexiSpeaker(
                                name=sp.get("name") or "",  # we need empty string, not None
                                email=sp.get("email_address") or "",
                                phone_number=sp.get("phone_number") or "",
                            )
                            for sp in call.get("speakers", [])
                        ],
                        follow_up_tasks=follow_up_tasks,
                        performed_at=call["performed_at"],
                    ).model_dump()
                    return
                else:
                    logger.debug("No summary found in call")
