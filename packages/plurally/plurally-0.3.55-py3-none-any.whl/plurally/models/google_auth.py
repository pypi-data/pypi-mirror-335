from __future__ import annotations

import base64
import os.path
import re
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import parseaddr
from functools import lru_cache
from typing import Dict, List

import tenacity
from bs4 import BeautifulSoup
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from loguru import logger
from pydantic import ConfigDict, EmailStr, Field, field_validator

from plurally.models import utils
from plurally.models.action.email_smtp import apply_reply_to, get_email_input_schema
from plurally.models.action.format import FormatTable
from plurally.models.action.indexer import Indexer
from plurally.models.adapters import table_to_str_adapter
from plurally.models.jinja_template import get_undeclared_vars
from plurally.models.misc import Table
from plurally.models.node import Node
from plurally.models.source.email_imap import (
    EmailSchema,
    EmailSourceInputSchema,
    EmailSourceOutputSchema,
)
from plurally.templateable_str import TemplateableStr

GMAIL_WARNING = """
```warning
Gmail blocks are functional but are waiting for approval from Google. If this is an issue, you can use the IMAP/SMTP counterparts. Do not hesitate to contact us for any questions.
```"""


def parse_email(gmail_response: dict) -> EmailSchema:
    payload = gmail_response.get("payload", {})
    headers = payload.get("headers", [])

    # Helper function to extract a header value
    def get_header(name):
        for header in headers:
            if header["name"].lower() == name.lower():
                return header["value"]
        return None

    # Extract the sender's name and email from the 'From' header
    from_header = get_header("From")
    if from_header:
        # Parsing the 'From' header (usually in the format 'Name <email@example.com>')
        sender_name, sender_email = parseaddr(from_header)
    else:
        sender_name, sender_email = None, None

    # Extract subject
    subject = get_header("Subject") or ""

    # Extract the body content (handling text/plain)
    content = ""
    if "body" in payload and payload["body"].get("data"):
        content = payload["body"]["data"]
    else:
        # If the email has parts (e.g., multipart/alternative), search for the plain text part
        parts = payload.get("parts", [])
        for part in parts:
            if part["mimeType"] == "text/plain" and "data" in part["body"]:
                content = part["body"]["data"]
                break
    content = base64.urlsafe_b64decode(content).decode("utf-8")
    # Extract datetime received from 'internalDate'
    internal_date = gmail_response.get("internalDate")
    datetime_received = datetime.fromtimestamp(int(internal_date) / 1000) if internal_date else datetime.now(timezone.utc)
    datetime_received = datetime_received.replace(tzinfo=None)

    # Build and return the Pydantic model
    return EmailSchema(
        sender_name=sender_name or "Unknown",
        sender_email=sender_email or "unknown@example.com",
        subject=subject,
        content=content,
        datetime_received=datetime_received,
    )


COMMON_DESC = """
```info
This block requires you to connect your GMail account to Plurally.
```"""


class Google(Node):
    SCOPES: List[str] = ["openid", "email"]
    SERVICE: str = None
    VERSION: str = None

    class InitSchema(Node.InitSchema): ...

    class InputSchema(Node.InputSchema): ...

    def get_necessary_env_vars(self) -> List[EmailStr]:
        return super().get_necessary_env_vars() + [
            "PLURALLY_TOKEN_URL",
            "PLURALLY_API_KEY",
        ]

    def __init__(self, init_inputs: InitSchema, outputs=None):
        assert self.SCOPES is not None, "SCOPES must be defined in the subclass"
        assert self.SERVICE is not None, "SERVICE must be defined in the subclass"
        assert self.VERSION is not None, "VERSION must be defined in the subclass"

        self._token = None
        self._token_expiry = None
        self._service = None
        super().__init__(init_inputs, outputs)

    @property
    def token_params(self) -> Dict[str, str]:
        return {}

    def token(self):
        now = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        if self._token is None or self._token_expiry < now:
            self.reset()
            self._token, self._token_expiry = utils.get_access_token(self.SCOPES, self.token_params)
        return self._token

    @property
    def service(self):
        if self._service is None:
            creds = Credentials(token=self.token())
            self._service = build(self.SERVICE, self.VERSION, credentials=creds)
        return self._service

    def reset(self):
        self._token = None
        self._token_expiry = None
        self._service = None

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_fixed(5),
        retry=tenacity.retry_if_exception_type(RefreshError),
    )
    def forward(self, input_schema: InputSchema):
        try:
            self._forward(input_schema)
        except RefreshError:
            # resetting will request a new token
            self.reset()
            raise


class GCalendarRead(Google):
    ICON = "gcalendar"


class GCalendarWrite(Google):
    ICON = "gcalendar"


class GmailRead(Google):
    ICON = "gmail"
    SCOPES = list(set(Google.SCOPES + ["https://www.googleapis.com/auth/gmail.readonly"]))
    SERVICE = "gmail"
    VERSION = "v1"
    IS_DEPRECATED = True  # for now, we are using the IMAP/SMTP counterparts

    SensitiveFields = ("email",)

    class InitSchema(Google.InitSchema):
        email: EmailStr = Field(
            title="Email",
            description="The email address to read emails from.",
            examples=["yourname@gmail.com"],
            max_length=320,
        )

    class InputSchema(Node.InputSchema): ...

    def __init__(self, init_inputs: Google.InitSchema):
        self.email = init_inputs.email
        super().__init__(init_inputs)

    @property
    def token_params(self):
        return super().token_params | {"email": self.email}

    def serialize(self):
        return super().serialize() | {"email": self.email}

    def get_scopes_and_meta_data(self):
        return [(self.SCOPES, {"email": self.email})]


class GMailNewEmail(GmailRead):
    ICON = "gmail"
    IS_TRIGGER = True
    OutputSchema = EmailSchema

    class InitSchema(GmailRead.InitSchema):
        __doc__ = f"""Trigger the flow when a new email is received in a mailbox from a GMail address.
```info
If you wish to process multiple emails or use them as source data, use the **kls::GmailSource** node instead.
```
{COMMON_DESC}
{GMAIL_WARNING}"""

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: InitSchema):
        if os.environ.get("PLURALLY_START_ISO_TIMESTAMP"):
            self.check_after = datetime.fromisoformat(os.environ["PLURALLY_START_ISO_TIMESTAMP"])
        else:
            self.check_after = datetime.now(timezone.utc).replace(tzinfo=None)
        self.last_processed_id = None
        super().__init__(init_inputs)

    def _forward(self, _):
        self.outputs = None
        # Format self.check_after to YYYY/MM/DD for the Gmail query
        formatted_check_after = self.check_after.strftime("%Y/%m/%d")

        # Fetch unread messages received after `self.check_after`
        query = f"is:unread after:{formatted_check_after}"
        messages = self.service.users().messages().list(userId="me", q=query).execute()

        # If no unread messages are found, return an empty result
        if "messages" not in messages:
            return

        email_ids = [msg["id"] for msg in messages["messages"]]
        emails = []

        for email_id in email_ids:
            email = self.service.users().messages().get(userId="me", id=email_id).execute()

            # Add email along with its received date (internalDate)
            emails.append(email)

        emails = sorted(emails, key=lambda x: (int(x["internalDate"]), x["id"]))

        for email in emails:
            email_received_timestamp = int(email["internalDate"]) / 1000  # Convert from ms to seconds
            email_received_datetime = datetime.fromtimestamp(email_received_timestamp).replace(tzinfo=None)

            # need to use >= here because it is possible that some emails
            # will have exactly the same timestamp.
            if email_received_datetime > self.check_after and (not self.last_processed_id or email["id"] > self.last_processed_id):
                self.outputs = parse_email(email).model_dump()
                self.check_after = email_received_datetime
                self.last_processed_id = email["id"]
                logger.debug(f"Email processed, setting check_after={self.check_after.isoformat()}")
                return


class GMailBase(GmailRead):
    class InitSchema(GmailRead.InitSchema):
        __doc__ = f"""
{COMMON_DESC}
{GMAIL_WARNING}"""

        limit: int = Field(
            default=200,
            ge=1,
            le=200,
            title="Max Emails",
            examples=[200],
            description="The maximum number of emails to process.",
        )
        q: str = Field(
            title="Filter",
            description="A Gmail search query.",
            default="",
            examples=["from:email@gmail.com subject:hello"],
            json_schema_extra={
                "advanced": True,
                "markdown-desc": "A Gmail search query, see [Gmail search operators](https://support.google.com/mail/answer/7190).",
            },
            max_length=300,
        )

    DESC = InitSchema.__doc__

    InputSchema = EmailSourceInputSchema
    OutputSchema = EmailSourceOutputSchema

    def __init__(self, init_inputs: "InitSchema"):
        self.limit = init_inputs.limit
        self.q = init_inputs.q
        super().__init__(init_inputs)

    def serialize(self):
        return super().serialize() | {"limit": self.limit, "q": self.q}

    @lru_cache(maxsize=200)
    def _fetch_email(self, email_id: str):
        email = self.service.users().messages().get(userId="me", id=email_id).execute()
        return email

    def _build_query(self, range_start: datetime, range_end: datetime):
        formatted_check_after = range_start.strftime("%Y/%m/%d")
        query = f"after:{formatted_check_after}"

        formatted_check_before = range_end.strftime("%Y/%m/%d")

        if query is None:
            query = f"before:{formatted_check_before}"
        else:
            query = f"{query} before:{formatted_check_before}"
        return f"{query} {self.q}"

    @lru_cache(2)
    def _fetch_email_ids(self, query: str, ttl_hash: int):
        email_ids = []
        max_batch_size = min(self.limit, 500)
        next_page_token = None
        while len(email_ids) < self.limit:
            limit = min(self.limit - len(email_ids), max_batch_size)
            results = self.service.users().messages().list(userId="me", q=query, maxResults=limit, pageToken=next_page_token).execute()

            messages = results.get("messages", [])
            email_ids.extend([msg["id"] for msg in messages])

            next_page_token = results.get("nextPageToken")
            if not next_page_token:
                logger.debug("No more pages, breaking")
                break
            if not len(email_ids) > self.limit:
                logger.debug("Reached limit, breaking")
                break

        return email_ids

    def _forward(self, node_input: "InputSchema"):
        query = self._build_query(node_input.range_start, node_input.range_end)
        logger.debug(f"Query: {query}")
        cache_secs = 60
        email_ids = self._fetch_email_ids(query, ttl_hash=time.time() // cache_secs)  # TTL of 1 minute
        logger.debug(f"Found {len(email_ids)} emails, filtering between {node_input.range_start} and {node_input.range_end}")
        emails = []
        range_start_timestamp = node_input.range_start.timestamp() // cache_secs * cache_secs
        range_end_timestamp = node_input.range_end.timestamp() // cache_secs * cache_secs

        for email_id in email_ids:
            email = self._fetch_email(email_id)

            email_received_timestamp = int(email["internalDate"]) / 1000
            if email_received_timestamp < range_start_timestamp:
                logger.debug(
                    f"Skipping email {email_id} as it is before the range ({datetime.fromtimestamp(email_received_timestamp)} {email_received_timestamp} < {range_start_timestamp})"
                )
                continue
            if email_received_timestamp > range_end_timestamp:
                logger.debug(f"Skipping email {email_id} as it is after the range ({email_received_timestamp} > {range_end_timestamp})")
                continue

            emails.append(parse_email(email).model_dump())
            if len(emails) == self.limit:
                break

        logger.debug(f"Processed {len(emails)} emails")
        self.outputs = {"emails": Table(data=emails)}


class GMailSource(GMailBase):
    class InitSchema(GMailBase.InitSchema):
        __doc__ = f"""Read emails in the inbox from a Gmail address.
```info
If you want to trigger the flow when a new email is received, use the **kls::GmailNewEmail** node instead.
```
{GMailBase.InitSchema.__doc__}"""

    def _build_query(self, range_start: datetime, range_end: datetime):
        q = super()._build_query(range_start, range_end)
        return f"{q} label:INBOX"

    DESC = InitSchema.__doc__


class GMailOutbox(GMailBase):
    class InitSchema(GMailSource.InitSchema):
        __doc__ = f"""Read emails sent from a Gmail address.
{GMailBase.InitSchema.__doc__}"""

    def _build_query(self, range_start: datetime, range_end: datetime):
        q = super()._build_query(range_start, range_end)
        return f"{q} from:me"

    DESC = InitSchema.__doc__


class GMailSendBase(Google):
    ICON = "gmail"
    SERVICE = "gmail"
    VERSION = "v1"
    SensitiveFields = ("email", "fullname")

    class InitSchema(Google.InitSchema):
        __doc__ = f"""Send email using Gmail.

{COMMON_DESC}
{GMAIL_WARNING}"""

        email: TemplateableStr = Field(
            title="Email",
            description="The email address to read emails from.",
            examples=["yourname@gmail.com"],
            max_length=320,
        )
        fullname: TemplateableStr = Field(
            "",
            title="Full Name",
            description="The full name of the sender.",
            examples=["John Doe"],
            max_length=100,
        )

        @field_validator("fullname", mode="after")
        def validate_fullname(cls, value):
            value.template = value.template.strip().replace("\n", " ").replace("\r", " ")
            return value

    DESC = InitSchema.__doc__

    class OutputSchema(Node.OutputSchema): ...

    def __init__(self, init_inputs: InitSchema):
        self.email = init_inputs.email
        self.fullname = init_inputs.fullname
        super().__init__(init_inputs)

    @property
    def token_params(self):
        p = super().token_params
        if self.email:
            p["email"] = self.email.expanded()
        return p

    @property
    def from_email(self):
        return f"{self.fullname.expanded()} <{self.email.expanded()}>" if self.fullname else self.email.expanded()

    def _forward(self, node_input):
        message = EmailMessage()
        message["To"] = node_input.email_address
        message["From"] = self.from_email

        body, subject = apply_reply_to(
            message,
            node_input.body,
            node_input.subject,
            node_input.reply_to,
            node_input.previous_email_subject_,
            node_input.previous_email_body_,
            node_input.previous_email_datetime_received_,
            node_input.previous_email_sender_name_,
            node_input.previous_email_sender_email_,
        )
        message["Subject"] = subject

        html_parser = BeautifulSoup(body, "html.parser")
        if bool(html_parser.find()):
            plain_text = html_parser.get_text(separator="\n", strip=True)
            message.set_content(plain_text)
            message.add_alternative(body, subtype="html")
        else:
            message.set_content(body)

        for attachment in node_input.attachments or []:
            logger.debug(f"Adding attachment: {attachment.filename}")
            message.add_attachment(
                attachment.content,
                maintype="application",
                subtype="octet-stream",
                filename=attachment.filename,
            )

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}

        message = self.create_message(create_message)
        logger.debug(f"Sent email with ID: {message['id']}")

    def serialize(self):
        return super().serialize() | {
            "email": self.email.template,
            "fullname": self.fullname.template,
        }

    def get_scopes_and_meta_data(self):
        if self.email:
            return [(self.SCOPES, {"email": self.email.expanded()})]
        return [(self.SCOPES, {})]

    def get_necessary_env_vars(self):
        return super().get_necessary_env_vars()


class GMailSend(GMailSendBase):
    SCOPES = list(set(Google.SCOPES + ["https://www.googleapis.com/auth/gmail.send"]))
    InputSchema = get_email_input_schema(...)

    def create_message(self, create_message):
        return self.service.users().messages().send(userId="me", body=create_message).execute()


class GMailDraft(GMailSendBase):
    IS_DEPRECATED = True
    SCOPES = list(set(Google.SCOPES + ["https://www.googleapis.com/auth/gmail.compose"]))
    InputSchema = get_email_input_schema("")

    def __init__(self, init_inputs):
        super().__init__(init_inputs)

    def create_message(self, create_message):
        return self.service.users().drafts().create(userId="me", body={"message": create_message}).execute()


def handle_sheet_error(name, e):
    if e.status_code == 403:
        raise ValueError(f"{name}: You do not have permission to write to this sheet. Did you connect the right Google Sheets Account?")
    elif e.status_code == 404:
        raise ValueError(f"{name}: Sheet not found, did you enter the correct ID?")
    elif e.status_code == 400:
        if "Invalid values" in e.content.decode():
            raise ValueError(f"{name}: Invalid values")
        elif "Invalid range" in e.content.decode():
            raise ValueError(f"{name}: Invalid range name")
        elif "Unable to parse range" in e.content.decode():
            raise ValueError(f"{name}: Cannot parse range name")
        raise ValueError(f"{name}: {e.content.decode()}")
    raise e


def _validate_sheet_id(value):
    if not value:
        raise ValueError("Sheet ID is required")
    value = value.strip()
    # parse id from https://docs.google.com/spreadsheets/d/1stK6QvcrMxs8eQQuykePF5iNjqHR_LvojfmbLBxFe4w/edit?gid=1987894739#gid=1987894739 using regex
    if "docs.google.com/spreadsheets/d" in value:
        try:
            return re.search(r"/d/([a-zA-Z0-9-_]+)", value).group(1)
        except Exception:
            raise ValueError("Invalid Google Sheet URL ")
    else:
        pattern = r"[a-zA-Z0-9-_]{44}"
        if not re.match(pattern, value):
            raise ValueError("Invalid Google Sheet ID")
    return value


class SheetsRead(Google):
    ICON = "gsheets"
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    SERVICE = "sheets"
    VERSION = "v4"

    SensitiveFields = ("sheet_id", "range_name")

    class InitSchema(Google.InitSchema):
        """Read data from a Google Sheet."""

        model_config = ConfigDict(json_schema_extra={"auto:create_gsheet": True})

        sheet_id: str = Field(
            title="Sheet URL or ID",
            description="The URL or ID of the Google Sheet to read from.",
            examples=["1CM29gwKIzeXsAppeNwrc8lbYaVcmUclprLuLYuHog4k"],
            json_schema_extra={
                "uiSchema": {
                    "ui:widget": "SheetIdWidget",
                    "ui:placeholder": "Enter a Google Sheet URL or ID",
                }
            },
        )

        range_name: str = Field(
            default="Sheet1",
            title="Range Name",
            description="The range of the sheet to read.",
            examples=["Sheet1", "Sheet1!A1:B2"],
            min_length=1,
            max_length=100,
        )

        @field_validator("sheet_id", mode="after")
        def validate_sheet_id(cls, value):
            return _validate_sheet_id(value)

        @classmethod
        def get_overrideable_fields(cls):
            return ["range_name"]

    class InputSchema(Node.InputSchema): ...

    class OutputSchema(Node.OutputSchema):
        values: Table = Field(
            title="Values",
            description="The values in the spreadsheet.",
        )

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: InitSchema, outputs=None):
        self.sheet_id = init_inputs.sheet_id
        self.range_name = init_inputs.range_name
        super().__init__(init_inputs, outputs)

    @property
    def sheet_url(self):
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"

    def _read_values(self):
        sheet = self.service.spreadsheets()
        try:
            result = sheet.values().get(spreadsheetId=self.sheet_id, range=self.range_name).execute()
        except HttpError as e:
            handle_sheet_error(self.name, e)
        return result.get("values", [])

    def _get_table_from_raw_values(self, values):
        if not values or len(values) == 1:
            return Table(data=[])

        headers = values[0]
        rows = values[1:]
        # turn into list of dicts
        data = []
        if rows:
            for row in rows:
                if len(row) < len(headers):
                    row = row + [""] * (len(headers) - len(row))
                # # we want to skip incomplete rows, as the might be while the user is updating his/her table
                # if len(row) == len(headers):
                data.append(dict(zip(headers, row)))
        return Table(data=data)

    def _forward(self, _: InputSchema):
        values = self._read_values()
        table = self._get_table_from_raw_values(values)
        self.outputs = {"values": table}

    def serialize(self):
        return super().serialize() | {
            "sheet_id": self.sheet_id,
            "range_name": self.range_name,
        }

    @property
    def adapters(self):
        return super().adapters | {"values": {str: table_to_str_adapter}}

    def get_all_necessary_columns(self, graph):
        columns = set()
        for _, tgt, key in graph.out_edges(self, data=True):
            if isinstance(tgt, FormatTable):
                src_handle, tgt_handle = key["src_handle"], key["tgt_handle"]
                if src_handle == "values" and tgt_handle == "table":
                    columns |= set(tgt.get_necessary_columns())
            elif isinstance(tgt, Indexer):
                src_handle, tgt_handle = key["src_handle"], key["tgt_handle"]
                if src_handle == "values" and tgt_handle == "knowledge":
                    columns |= set(tgt.get_necessary_columns())
        return columns

    def get_issues(self, graph):
        # ensure that the sheet exists
        try:
            values = self._read_values()
        except Exception as e:
            return [str(e)]

        issues = []
        all_necessary_cols = self.get_all_necessary_columns(graph)
        if values:
            missing = all_necessary_cols - set(values[0])
            if missing:
                issues.append(f"{self.name}: sheet is missing the following columns: {', '.join(missing)}")
        elif all_necessary_cols:
            issues.append(f"{self.name}: sheet has no data, but the following columns are required: {', '.join(all_necessary_cols)}")
        return issues


class SheetsWrite(Google):
    ICON = "gsheets"
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SERVICE = "sheets"
    VERSION = "v4"
    SensitiveFields = ("sheet_id", "range_name")

    class InitSchema(Google.InitSchema):
        """Write data to a Google Sheet."""

        model_config = ConfigDict(json_schema_extra={"auto:create_gsheet": True})

        sheet_id: str = Field(
            title="Sheet URL or ID",
            description="The URL or ID of the Google Sheet to write to.",
            examples=["1CM29gwKIzeXsAppeNwrc8lbYaVcmUclprLuLYuHog4k"],
            json_schema_extra={
                "uiSchema": {
                    "ui:widget": "SheetIdWidget",
                    "ui:placeholder": "Enter a Google Sheet URL or ID",
                }
            },
        )
        append: bool = Field(
            True,
            title="Append",
            description="Whether to append to the sheet or reset the sheet before writing.",
            json_schema_extra={"advanced": True},
        )
        range_name: str = Field(
            default="Sheet1",
            title="Range Name",
            description="The range of the sheet to write.",
            examples=["Sheet1", "Sheet1!A1:B2"],
            min_length=1,
        )

        @field_validator("sheet_id", mode="after")
        def validate_sheet_id(cls, value):
            return _validate_sheet_id(value)

        @classmethod
        def get_overrideable_fields(cls):
            return ["range_name"]

    def get_all_necessary_columns(self, graph):
        return []

    def _read_values(self):
        sheet = self.service.spreadsheets()
        try:
            result = sheet.values().get(spreadsheetId=self.sheet_id, range=self.range_name).execute()
        except HttpError as e:
            handle_sheet_error(self.name, e)
        return result.get("values", [])

    def get_issues(self, graph):
        # ensure that the sheet exists
        try:
            self._read_values()
        except Exception as e:
            return [str(e)]
        return []

    class InputSchema(Node.InputSchema):
        values: Table

    class OutputSchema(Node.OutputSchema):
        url: str = Field(title="Url")
        icon: str = Field("", title="Icon")

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: InitSchema, outputs=None):
        self.sheet_id = init_inputs.sheet_id
        self.append = init_inputs.append
        self.range_name = init_inputs.range_name
        self.value_input_option = "RAW"

        super().__init__(init_inputs, outputs)

    @property
    def sheet_url(self):
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"

    def _reorder_rows_to_write(self, headers, rows):
        # in case the columns are not in the same order as the headers
        return [[row.get(header, None) for header in headers] for row in rows]

    @staticmethod
    def _get_header_range(sheet_range_name):
        splitted = sheet_range_name.split("!")
        if len(splitted) > 1:
            assert len(splitted) == 2
            sheet_name, range_name = splitted
            splitted_range = range_name.split(":")
            start_range = splitted_range[0]
            if len(splitted_range) > 1:
                end_range = re.findall(r"[a-zA-Z]+", splitted_range[1])[0]
            else:
                end_range = "Z"
            start_row_line = re.findall(r"\d+", start_range)
            if start_row_line:
                end_row_line = int(start_row_line[0]) + 1
            else:
                start_range += "1"
                end_row_line = 2
            return f"{sheet_name}!{start_range}:{end_range}{end_row_line}"
        else:
            sheet_name = splitted[0]
            range_name = "A1:Z2"
            return f"{sheet_name}!{range_name}"

    def _write_values(self, data: List[Dict[str, str]]):
        if not data:
            logger.debug("No data to write")
            return

        sheet = self.service.spreadsheets()
        headers = list(data[0].keys())

        if self.append:
            # Get the first row of the sheet to check if headers are present
            header_range_name = self._get_header_range(self.range_name)
            result = (
                sheet.values()
                .get(
                    spreadsheetId=self.sheet_id,
                    range=header_range_name,
                    majorDimension="ROWS",
                )
                .execute()
            )
            existing_row = result.get("values", [])
        else:
            # clear sheet
            sheet.values().clear(
                spreadsheetId=self.sheet_id,
                range=self.range_name,
            ).execute()
            existing_row = []

        is_current_headers_contained = False
        existing_headers = None
        if existing_row:
            existing_headers = existing_row[0]
            is_current_headers_contained = set(existing_headers).issuperset(headers)

        if is_current_headers_contained:
            rows = self._reorder_rows_to_write(existing_headers, data)
            logger.debug("Headers already present, skipping header row")
            body = {"values": rows}
        else:
            rows = [headers] + self._reorder_rows_to_write(headers, data)
            logger.debug("Headers not present, writing headers and data")
            body = {"values": rows}

        try:
            if self.append:
                sheet.values().append(
                    spreadsheetId=self.sheet_id,
                    range=self.range_name,
                    valueInputOption=self.value_input_option,
                    body=body,
                ).execute()
            else:
                sheet.values().update(
                    spreadsheetId=self.sheet_id,
                    range=self.range_name,
                    valueInputOption=self.value_input_option,
                    body=body,
                ).execute()
        except HttpError as e:
            handle_sheet_error(self.name, e)

    def _forward(self, node_input: InputSchema):
        self._write_values(node_input.values.data)
        self.outputs = {
            "url": f"https://docs.google.com/spreadsheets/d/{self.sheet_id}",
            "icon": self.ICON,
        }

    def serialize(self):
        return super().serialize() | {
            "sheet_id": self.sheet_id,
            "range_name": self.range_name,
            "append": self.append,
        }
