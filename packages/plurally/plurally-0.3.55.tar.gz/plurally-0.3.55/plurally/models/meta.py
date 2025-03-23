from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import List

import networkx as nx
import requests
import tenacity
from loguru import logger
from pydantic import Field
from thefuzz import fuzz

from plurally.models.adapters import table_to_str_adapter
from plurally.models.misc import Table
from plurally.models.node import Node


class MetaAuth(Node):
    SCOPES: List[str] = None
    ICON = "instagram"

    class InitSchema(Node.InitSchema): ...

    class InputSchema(Node.InputSchema): ...

    def __init__(self, init_inputs: InitSchema, outputs=None):
        self._token = None
        self._token_expiry = None
        self._service = None
        super().__init__(init_inputs, outputs)

    def token(self):
        now = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        if self._token is None or self._token_expiry < now:
            self.reset()
            self._token, self._token_expiry = self._get_access_token()
        return self._token

    def _get_access_token(self):
        token_url = os.environ.get("PLURALLY_TOKEN_URL")
        assert token_url, "PLURALLY_TOKEN_URL must be set in the environment"

        api_key = os.environ.get("PLURALLY_API_KEY")
        assert api_key, "PLURALLY_API_KEY must be set in the environment"

        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        res = requests.get(token_url, headers=headers, params={"scopes": " ".join(self.SCOPES)})
        res.raise_for_status()

        data = res.json()
        token_expiry = datetime.fromisoformat(data["expires_at"])
        return data["access_token"], token_expiry

    def reset(self):
        self._token = None
        self._token_expiry = None
        self._service = None


class InstagramNewDm(MetaAuth):
    SCOPES = (
        "pages_show_list",
        "pages_manage_metadata",
        "business_management",
        "instagram_basic",
        "instagram_manage_messages",
    )
    IS_TRIGGER = True

    class InitSchema(MetaAuth.InitSchema):
        __doc__ = """
Will trigger the flow for each new incoming Instagram direct message sent to the connected account.

```info
This block requires you to connect your Instagram Business Account to Plurally.
```
        """

        delay: int = Field(
            10,
            title="Delay (in seconds)",
            description="The delay (in seconds) to wait before handling a message. This is useful in case someone sends multiple messages in a row. Delay is ignored when testing.",
            json_schema_extra={
                "advanced": True,
            },
        )
        history_limit: int = Field(
            20,
            description="The number of past messages to fetch in the conversation history.",
            json_schema_extra={
                "advanced": True,
            },
        )

    class OutputSchema(Node.OutputSchema):
        new_message_content: str = Field(
            description="The message that was received.",
            json_schema_extra={"example-force": "Hello! How are you doing today?"},
        )
        sender_username: str = Field(
            description="The username of the sender.",
            json_schema_extra={
                "example-force": "plurallyai.test",
                "example-desc-force": "Sender's username is fixed when testing.",
                "uiSchema": {
                    "ui:disabled": True,
                },
            },
        )
        sender_id: int = Field(
            description="The ID of the sender.",
            json_schema_extra={
                "example-force": 1682774559178836,
                "example-desc-force": "Sender's ID is fixed when testing.",
                "uiSchema": {
                    "ui:disabled": True,
                },
            },
        )
        new_message_date_received: datetime = Field(
            default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
            description="The date and time the message was received.",
            format="date-time",
        )
        history: Table = Field(
            title="Conversation History",
            description="The conversation history is a table with columns: from_user, to_user, message, and date_received.",
            format="table",
            json_schema_extra={
                "uiSchema": {
                    "ui:options": {"label": False},
                    "ui:widget": "hidden",
                },
                "markdown-examples": f"""
```table
{json.dumps([
    ["from_user", "to_user", "message", "date_received"],
    ["username1", "username2", "Hello!", "2022-01-01T12:00:00Z"],
    ["username2", "username1", "Hi!", "2022-01-01T12:01:00Z"],
])}
```""",
                "markdown-desc": """The messages that were received in the past in this conversation, from oldest to newest, with following columns:
- **from_user**: The username of the sender.
- **to_user**: The username of the recipient.
- **message**: The message content.
- **date_received**: The date and time the message was received.
""",
            },
        )

        was_escalated_previously_: bool = Field(
            False,
            description="Whether the conversation was escalated to a human previously.",
        )

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: "InitSchema", outputs=None):
        self.history_limit = init_inputs.history_limit
        self.delay = init_inputs.delay
        self.mark_processed_params = None

        if os.environ.get("PLURALLY_START_ISO_TIMESTAMP"):
            self.check_after = datetime.fromisoformat(os.environ["PLURALLY_START_ISO_TIMESTAMP"])
        else:
            self.check_after = datetime.now(timezone.utc).replace(tzinfo=None)
        super().__init__(init_inputs, outputs)

    @property
    def adapters(self):
        return super().adapters | {"history": {str: table_to_str_adapter}}

    @tenacity.retry(
        wait=tenacity.wait_fixed(5),
        stop=tenacity.stop_after_attempt(5),
    )
    def callback(self):
        super().callback()
        if self.mark_processed_params:
            mark_processed_url = os.environ.get("PLURALLY_INSTA_DMS_MARK_PROCESSED_URL")
            assert mark_processed_url, "PLURALLY_INSTA_DMS_MARK_PROCESSED_URL must be set in the environment"

            api_key = os.environ.get("PLURALLY_API_KEY")
            assert api_key, "PLURALLY_API_KEY must be set in the environment"

            r = requests.post(
                mark_processed_url,
                params=self.mark_processed_params,
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
            )
            try:
                r.raise_for_status()
            except Exception as e:
                logger.exception(e)
                raise ValueError(f"Failed to mark message as processed {r.text}")

    def early_stop_if_needed(self, graph: nx.MultiDiGraph):
        if self.outputs is None:
            return
        is_early_stop = self.outputs.get("was_escalated_previously_", False)
        if not is_early_stop:
            # only do this if was not previously escalated
            # if has direct connection to send dm and is triggered, it should stop
            for _, tgt in graph.out_edges(self):
                if isinstance(tgt, InstagramSendDm):
                    assert all(
                        key in self.outputs
                        for key in [
                            "history",
                            "sender_id",
                            "sender_username",
                            "new_message_content",
                        ]
                    )
                    data = list(self.outputs["history"].data) + [
                        {
                            "from_user": self.outputs["sender_username"],
                            "to_user": "you",
                            "message": self.outputs["new_message_content"],
                            "date_received": self.outputs["new_message_date_received"],
                        }
                    ]
                    history_and_last_dm = Table(data=data)
                    is_triggered = tgt.process_escalation_if_needed(
                        history_and_last_dm,
                        self.outputs["sender_id"],
                        self.outputs["sender_username"],
                    )
                    if is_triggered:
                        is_early_stop = True
                        break
        if is_early_stop:
            self.outputs = None

    @tenacity.retry(
        wait=tenacity.wait_fixed(5),
        stop=tenacity.stop_after_attempt(5),
    )
    def _fetch_new_dms(self):
        dms_url = os.environ.get("PLURALLY_INSTA_DMS_URL")
        assert dms_url, "PLURALLY_INSTA_DMS_URL must be set in the environment"

        api_key = os.environ.get("PLURALLY_API_KEY")
        assert api_key, "PLURALLY_API_KEY must be set in the environment"

        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        res = requests.get(
            dms_url,
            headers=headers,
            params={
                "limit_history": self.history_limit,
                "delay": self.delay,
                "after": int(self.check_after.timestamp() * 1000),
            },
        )
        try:
            res.raise_for_status()
        except Exception as e:
            logger.exception(e)
            raise ValueError(f"Failed to fetch new messages: {res.text}")
        data = res.json()
        was_escalated_previously = data.get("was_escalated_previously", False)
        history = data["history"]
        if not history:
            return None, None, None, False

        timestamp = int(data["timestamp"])

        history, last_message = history[:-1], history[-1]
        return history, last_message, timestamp, was_escalated_previously

    def forward(self, _):
        mark_processed_url = os.environ.get("PLURALLY_INSTA_DMS_MARK_PROCESSED_URL")
        assert mark_processed_url, "PLURALLY_INSTA_DMS_MARK_PROCESSED_URL must be set in the environment"

        history, last_message, last_processed_timestamp, was_escalated_previously = self._fetch_new_dms()

        if not last_message:
            self.outputs = None
            self.mark_processed_params = None
            return

        self.mark_processed_params = {
            "last_processed_timestamp": last_processed_timestamp,
            "sender_id": last_message["from_user"]["id"],
        }
        sender_id = last_message["from_user"]["id"]

        self.outputs = {
            "new_message_content": last_message["message"],
            "new_message_date_received": last_message["timestamp"],
            "sender_username": last_message["from_user"]["username"],
            "sender_id": sender_id,
            "was_escalated_previously_": was_escalated_previously,
            "history": Table(
                data=[
                    {
                        "from_user": dm["from_user"]["username"],
                        "to_user": dm["to_user"]["username"],
                        "message": dm["message"],
                        "date_received": dm["timestamp"],
                    }
                    for dm in history
                ]
            ),
        }

    def serialize(self):
        return super().serialize() | {
            "history_limit": self.history_limit,
            "delay": self.delay,
        }

    DESC = InitSchema.__doc__


class InstagramSendDm(MetaAuth):
    SCOPES = (
        "pages_show_list",
        "business_management",
        "instagram_basic",
        "instagram_manage_messages",
    )

    class InitSchema(MetaAuth.InitSchema):
        __doc__ = """
Sends a direct message to a user on Instagram.

This block should be used for building chatbots or automating responses to Instagram direct messages for your business account.

It includes a human escalation feature, which when triggered will notify you when a user requests to talk to a human.

```info
This block requires you to connect your Instagram Business Account to Plurally.
```
        """
        human_escalation_template: str = Field(
            "To talk to me directly, please type {trigger}.",
            title="Human Escalation Template",
            pattern=r".*\{trigger\}.*",
            description="The content to explain the user how to trigger a human escalation. This will be appended to your automated answer. Use {trigger} to indicate where the human escalation trigger should be placed.",
            min_length=5,
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:widget": "textarea",
                    "ui:placeholder": "Write template here, for example: To talk to me directly, please type {trigger}.",
                    "errorMessages": {
                        "pattern": "You must provide a template with the {trigger} placeholder, for example: To talk to me directly, please type {trigger}."
                    },
                },
            },
        )
        human_escalation_message: str = Field(
            "Understood! I will get back to you shortly.",
            description="The message that will be sent to the user when a human escalation is triggered.",
            min_length=5,
            max_length=1000,
            format="textarea",
            json_schema_extra={"advanced": True},
        )
        human_escalation_trigger: str = Field(
            "Talk to a human",
            title="Human Escalation Trigger",
            description="The message that will trigger a human escalation.",
            min_length=5,
        )

    class InputSchema(MetaAuth.InputSchema):
        recipient_id: int = Field(
            description="The username of the recipient.",
        )
        message: str = Field(
            description="The message to send.",
        )
        was_escalated_previously_: bool = Field(
            description="Whether the conversation was escalated to a human previously.",
        )

    class OutputSchema(Node.OutputSchema): ...

    def __init__(self, init_inputs: MetaAuth.InitSchema, outputs=None):
        super().__init__(init_inputs, outputs)
        self.human_escalation_message = init_inputs.human_escalation_message
        self.human_escalation_template = init_inputs.human_escalation_template
        self.human_escalation_trigger = init_inputs.human_escalation_trigger

    def serialize(self):
        return super().serialize() | {
            "human_escalation_message": self.human_escalation_message,
            "human_escalation_trigger": self.human_escalation_trigger,
            "human_escalation_template": self.human_escalation_template,
        }

    @tenacity.retry(
        wait=tenacity.wait_fixed(5),
        stop=tenacity.stop_after_attempt(5),
    )
    def _send_message(self, page_access_token, recipient_id, message):
        r = requests.post(
            "https://graph.facebook.com/v20.0/me/messages",
            params={
                "access_token": page_access_token,
            },
            json={
                "recipient": {"id": recipient_id},
                "message": {"text": message},
            },
        )
        try:
            r.raise_for_status()
        except Exception as e:
            logger.exception(e)
            raise ValueError(f"Failed to send message: {r.text}")

    def handle_escalation(self, escalate_url, sender_id, sender_username):
        api_key = os.environ.get("PLURALLY_API_KEY")
        assert api_key, "PLURALLY_API_KEY must be set in the environment"

        r = requests.post(
            escalate_url,
            json={
                "sender_id": sender_id,
                "sender_username": sender_username,
                "message": self.human_escalation_message,
            },
            headers={
                "Authorization": f"Bearer {api_key}",
            },
        )
        try:
            r.raise_for_status()
        except Exception as e:
            logger.exception(e)
            raise ValueError("Failed to escalate message")

    def process_escalation_if_needed(self, history: Table, recipient_id, sender_username):
        escalate_url = os.environ.get("PLURALLY_INSTA_ESCALATE_URL")
        assert escalate_url, "PLURALLY_INSTA_ESCALATE_URL must be set in the environment"

        # if there is escalation trigger in the last minute
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for dm in history.data:
            recv = datetime.strptime(dm["date_received"], "%Y-%m-%dT%H:%M:%SZ")
            if (now - recv).total_seconds() > 60:
                continue
            if dm["from_user"] != sender_username:
                continue
            new_message_content = dm["message"].lower()
            if fuzz.partial_ratio(self.human_escalation_trigger.lower(), new_message_content) > 80:
                logger.debug(f"Detected human escalation trigger: {new_message_content}")
                self.outputs = None
                self.handle_escalation(
                    escalate_url,
                    recipient_id,
                    sender_username,
                )
                return True
        return False

    def forward(self, node_input):
        if node_input.was_escalated_previously_:
            return
        page_access_token = os.environ.get("PLURALLY_INSTA_PAGE_ACCESS_TOKEN")
        assert page_access_token, "PLURALLY_INSTA_PAGE_ACCESS_TOKEN must be set in the environment"

        message_left = str(node_input.message)
        # message limit is 1000, split if longer
        recipient_id = node_input.recipient_id
        while len(message_left) > 1000:
            message = message_left[:1000]
            message_left = message_left[1000:]
            self._send_message(page_access_token, recipient_id, message)
        self._send_message(page_access_token, recipient_id, message_left)
        self._send_message(
            page_access_token,
            recipient_id,
            self.human_escalation_template.format(trigger=self.human_escalation_trigger),
        )

    DESC = InitSchema.__doc__


__all__ = ["InstagramNewDm", "InstagramSendDm"]
