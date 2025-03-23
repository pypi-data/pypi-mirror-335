import email
import imaplib
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from email.header import decode_header
from email.policy import default
from email.utils import parseaddr
from functools import lru_cache

import tenacity
from loguru import logger
from pydantic import EmailStr, Field, model_validator
from thefuzz import fuzz

from plurally.crypto import decrypt, encrypt
from plurally.json_utils import load_from_json_dict
from plurally.models import adapters as model_adapters
from plurally.models.misc import Table
from plurally.models.node import Node
from plurally.models.utils import get_naive_datetime

GMAIL = """
To use this block with GMail you need to:
1. [First enable 2-step verification on your Google account](https://myaccount.google.com/signinoptions/two-step-verification/enroll-welcome).
2. [Create an App Password](https://myaccount.google.com/apppasswords). **Do not include spaces in the password**.
3. [Enable IMAP access](https://mail.google.com/mail/u/6/?tab=km#settings/fwdandpop).
4. Use the following settings:
    - **IMAP Server**: `imap.gmail.com`
    - **Port**: `993`
    - **Mailbox**: `inbox`
```warning
The password is the one generated in step 2, **do not use the password of your Gmail account** (the one you use to connect from the browser).
**Do not include spaces in the password**
```
"""

IMAP_COMMON = f"""
### Common Email Providers
Follow the steps below to configure the block for some common email providers. If you encounter any issues, reach out to us on [Discord](https://discord.gg/aGpMJfYpDb).
```accordion
{json.dumps([
    {"title": "GMail", "content": GMAIL, "icon": "gmail"},
])}
```
"""


def decode_body(part):
    charset = part.get_content_charset() or "utf-8"
    try:
        return part.get_payload(decode=True).decode(charset)
    except UnicodeDecodeError:
        return part.get_payload(decode=True).decode("iso-8859-1")
    except Exception as e:
        logger.error(f"Error decoding email body with charset {charset}")
        raise e


class EmailSourceInputSchema(Node.InputSchema):
    range_start: datetime = Field(
        None,
        title="Start Date",
        examples=["2023-08-01 00:00:00"],
        format="date-time",
        description="Only emails received after this date will be processed. If not provided, only emails in the last 24 hours will be processed.",
    )

    range_end: datetime = Field(
        None,
        title="End Date",
        examples=["2023-08-01 00:00:00"],
        format="date-time",
        description="Only emails received before this data will be processed. If not provided, all emails after 'Start Date' will be processed.",
    )

    @model_validator(mode="after")
    def ckeck_model(cls, schema):
        range_start = schema.range_start or datetime.now(tz=timezone.utc).replace(tzinfo=None) - timedelta(days=1)

        assert range_start, "Start date is required"
        if range_start.tzinfo:
            range_start = range_start.astimezone(timezone.utc).replace(tzinfo=None)

        range_end = schema.range_end
        if range_end:
            if range_end.tzinfo:
                range_end = range_end.astimezone(timezone.utc).replace(tzinfo=None)
        else:
            range_end = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        range_end += timedelta(days=1)  # Add a day to include the end date

        if range_start > range_end:
            raise ValueError(f"End date must be after start date, got {range_start} and {range_end}")

        schema.range_start = range_start
        schema.range_end = range_end
        return schema


class EmailSourceOutputSchema(Node.OutputSchema):
    emails: Table = Field(
        title="Emails",
        description="""The emails read from the mailbox, columns will be sender_name, sender_email, datetime_received, subject, body""",
        json_schema_extra={
            "markdown-examples": f"""
```table
{json.dumps([
    ["sender_name", "sender_email", "datetime_received", "subject", "body"],
    ["John Doe", "john@tryplurally.com", "2023-08-01 00:00:00", "Hello", "Hello, World!"],
])}
```""",
            "markdown-desc": """The emails read from the mailbox, with following columns:
- **sender_name**: The name of the sender.
- **sender_email**: The email address of the sender.
- **datetime_received**: The datetime when the email was received.
- **subject**: The subject of the email.
- **body**: The body of the email.
""",
        },
        # - seen""", removing seen column because not working with gmail atm
    )


class EmailSchema(Node.OutputSchema):
    sender_name: str = Field(
        title="Sender Name",
        examples=["John Doe"],
        description="Name of the sender of the incoming email.",
    )
    sender_email: EmailStr = Field(
        title="Sender's Email Address",
        description="Email address of the sender of the incoming email.",
    )
    subject: str = Field(
        "",
        title="Incoming Email's Subject",
        examples=["Hello"],
        description="Subject of the incoming email.",
    )
    content: str = Field(
        "",
        title="Incoming Email's Body",
        examples=["Hello, World!"],
        description="Body of the incoming email.",
        format="textarea",
    )
    datetime_received: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        title="Datetime Received",
        examples=["2023-08-01 00:00:00"],
        format="date-time",
        description="Datetime when the incoming email was received.",
        json_schema_extra={
            "auto:default": "local-dt",
        },
    )
    message_id: str = Field(
        "unspecified",
        title="Email ID",
        description="Unique identifier of the incoming email, connect it to Send Email's 'Reply-To' to create a reply or continue a thread.",
        json_schema_extra={
            "hide-in-example": True,
        },
    )

    class Config:
        json_schema_extra = {
            "description": "The outputs of this block represents the data associated with each incoming email.",
        }


class EmailIMAPBase(Node):
    ICON = "email"
    SensitiveFields = ("username", "password", "imap_server", "mailbox", "port")

    class InitSchema(Node.InitSchema):
        class Config:
            json_schema_extra = {
                "description": "The inputs of this block represents the configuration for reading emails from an IMAP server.\n\nAll passwords are encrypted and private.",
            }

        username: str = Field(
            title="Email",
            examples=["name@outlook.com"],
            format="email",
            description="Your email address",
            min_length=1,
            max_length=320,
            json_schema_extra={
                "uiSchema": {
                    "ui:placeholder": "Enter your email address",
                }
            },
        )
        password: str = Field(
            title="Password",
            examples=["password123"],
            description="Your email address's password.",
            min_length=1,
            max_length=1000,
            json_schema_extra={
                "is-encrypted": True,
                "uiSchema": {
                    "ui:widget": "password",
                    "ui:placeholder": "Enter your assword",
                    "ui:emptyValue": None,
                },
            },
        )
        imap_server: str = Field(
            title="IMAP Server",
            examples=["imap.gmail.com"],
            description="The IMAP server's address of your email provider.",
            max_length=100,
            json_schema_extra={
                "uiSchema": {
                    "ui:placeholder": "Enter the IMAP server address",
                }
            },
            min_length=1,
        )
        port: int = Field(
            993,
            title="IMAP Port",
            examples=[993],
            description="Port for connecting to the IMAP server.",
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:placeholder": "Enter the IMAP port",
                },
            },
        )
        mailbox: str = Field(
            "inbox",
            title="Mailbox",
            examples=["inbox"],
            max_length=100,
            description="The mailbox to read emails from.",
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:placeholder": "mailbox",
                },
            },
        )
        refresh_every: int = Field(
            600,
            title="Refresh Every",
            examples=[60],
            description="The interval in seconds to check for new emails.",
            gt=0,
            json_schema_extra={
                "advanced": True,
                "uiSchema": {
                    "ui:placeholder": "Enter the interval in seconds",
                },
            },
        )

    def __init__(
        self,
        init_inputs: InitSchema,
        is_password_encrypted: bool = False,
    ) -> None:
        super().__init__(init_inputs)
        self.username = init_inputs.username

        if is_password_encrypted:
            self.password = init_inputs.password
        else:
            self.password = encrypt(init_inputs.password)

        self.imap_server = init_inputs.imap_server
        self.port = init_inputs.port
        self.mailbox = init_inputs.mailbox
        self.refresh_every = init_inputs.refresh_every
        self._server = None  # lazy init

    @property
    def server(self):
        if self._server is None:
            self._server = self._login_server(
                self.username,
                self.password,
                self.imap_server,
                self.port,
            )
            self._select_mailbox()
        return self._server

    def _select_mailbox(self):
        result, mailboxes = self.server.list()
        mailboxes = [m.decode() for m in mailboxes]
        logger.debug(f"Mailboxes: {mailboxes}")
        mailbox_clean = self.mailbox
        if result == "OK":
            ms = []
            for mailbox in mailboxes:
                try:
                    mailbox_parts = re.findall(r'\(.*?\)|".*?"|\S+', mailbox)
                except Exception as e:
                    logger.error(f"Could not parse mailbox {mailbox}")
                    logger.exception(e)

                if not mailbox_parts:
                    logger.error(f"Could not parse mailbox {mailbox}")
                    continue

                mailbox = mailbox_parts[-1].strip()
                mailbox_compare = mailbox.replace('"', "").replace("[Gmail]/", "")
                score = fuzz.ratio(mailbox_compare.lower(), self.mailbox.lower())
                ms.append((score, mailbox))
            mailbox_clean_score, mailbox_clean = max(ms)
            logger.debug(f"Matched mailbox {self.mailbox} to {mailbox_clean} with score={mailbox_clean_score}")
        else:
            logger.warning("Could not list mailboxes, trying with default")
        logger.debug(f"Selecting mailbox {mailbox_clean}")
        self._server.select(mailbox_clean)

    def _login_server(
        self,
        username: EmailStr,
        password: str,
        imap_server: str,
        port: int,
    ):
        logger.debug(f"Logging into {imap_server}:{port}")
        imap = imaplib.IMAP4_SSL(imap_server, port=port)
        password = decrypt(password)
        imap.login(username, password)
        logger.debug(f"Connected successfully to {imap_server}:{port}")
        return imap

    def serialize(self):
        payload = super().serialize()
        payload.update(
            {
                "username": self.username,
                "password": self.password,
                "imap_server": self.imap_server,
                "port": self.port,
                "mailbox": self.mailbox,
                "refresh_every": self.refresh_every,
            }
        )
        return payload

    @classmethod
    def _parse(cls, **kwargs):
        return cls(cls.InitSchema(**kwargs), is_password_encrypted=True)

    def _parse_email(self, msg, msg_id):
        # Check if the email has been read (based on the \Seen flag)
        status, flags_data = self.server.fetch(msg_id, "(FLAGS)")
        flags = flags_data[0].decode("utf-8")
        is_seen = "\\Seen" in flags

        if msg["Subject"]:
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
        else:
            subject = ""

        from_ = msg.get("From")
        name, email_address = parseaddr(from_)

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = decode_body(part)
        else:
            body = decode_body(msg)

        if True:
            # Remove any prefix quotes from the email body
            body = re.sub(r"(?:> ?)*", "", body).strip()

        return {
            "subject": subject,
            "sender_name": name,
            "sender_email": email_address,
            "body": body,
            "seen": is_seen,
        }

    @lru_cache(maxsize=1000)
    def _fetch_email(self, email_id):
        res, msg = self.server.fetch(email_id, "(BODY.PEEK[])")  # does not open email
        for response_part in msg:
            if isinstance(response_part, tuple):
                # this is the part containing the actual email content
                msg = email.message_from_bytes(response_part[1], policy=default)
                message_id = msg.get("Message-ID", None)
                email_date = msg["Date"]
                email_date_parsed = email.utils.parsedate_to_datetime(email_date)

                logger.debug(f"Processing email from {email_date} with id={message_id}")

                if msg["Subject"]:
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                else:
                    subject = ""

                from_ = msg.get("From")
                name, email_address = parseaddr(from_)

                if msg.is_multipart():
                    html = None
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = decode_body(part)
                            break
                        elif part.get_content_type() == "text/html":
                            html = decode_body(part)
                    else:
                        logger.warning(f"Could not find text/plain part in email {subject}")
                        body = html
                else:
                    body = decode_body(msg)
                return EmailSchema(
                    sender_name=name,
                    sender_email=email_address,
                    datetime_received=email_date_parsed,
                    subject=subject,
                    content=body or "",
                    message_id=message_id,
                )

        logger.warning(f"email {email_id}, could not be processed")

    @lru_cache(maxsize=10)
    def _fetch_email_ids(self, query: str, ttl_hash: int):
        logger.debug(f"Fetching email ids with query: {query}")
        self.server.noop()
        status, messages = self.server.search(None, query)

        if status != "OK":
            logger.error("Error fetching emails")
            return []

        email_ids = messages[0].split()
        logger.debug(f"Found {len(email_ids)} emails with {query}")
        return email_ids


class EmailSourceIMAP(EmailIMAPBase):
    class InitSchema(EmailIMAPBase.InitSchema):
        __doc__ = f"""Read emails in a mailbox from an IMAP server.

```warning
If you want to trigger the flow for each new incoming email, use the **kls::NewEmail** block instead.
```
{IMAP_COMMON}"""

        limit: int = Field(
            default=200,
            ge=1,
            le=200,
            title="Max Emails",
            examples=[200],
            description="The maximum number of emails to process.",
            json_schema_extra={"advanced": True},
        )

    InputSchema = EmailSourceInputSchema
    OutputSchema = EmailSourceOutputSchema

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: InitSchema, is_password_encrypted: bool = False):
        self.limit = init_inputs.limit
        super().__init__(init_inputs, is_password_encrypted=is_password_encrypted)

    def serialize(self):
        return super().serialize() | {
            "limit": self.limit,
        }

    def _build_query(self, range_start: datetime, range_end: datetime):
        imap_date_start = range_start.strftime("%d-%b-%Y")
        imap_date_end = (range_end + timedelta(days=1)).strftime("%d-%b-%Y")
        return f"SINCE {imap_date_start} BEFORE {imap_date_end}"

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_fixed(5),
    )
    def forward(self, node_input: InputSchema):
        query = self._build_query(node_input.range_start, node_input.range_end)
        email_ids = self._fetch_email_ids(query, ttl_hash=time.time() // self.refresh_every)
        emails = []
        for email_id in email_ids:
            email_obj = self._fetch_email(email_id)
            naive_dt_received = get_naive_datetime(email_obj.datetime_received)
            if all(
                [
                    email_obj,
                    naive_dt_received > node_input.range_start,
                    naive_dt_received < node_input.range_end,
                ]
            ):
                row = email_obj.model_dump()
                # hotfix: we wrongly called the body as content, so we need to rename it
                # eventually we will need to update the schema but this will need careful renaming of the handles
                # and connections of existing flows
                row["body"] = row.pop("content")
                emails.append(row)
                if self.limit and len(emails) >= self.limit:
                    logger.debug("Limit reached, stopping processing")
                    break

        logger.debug(f"Processed {len(emails)} emails")
        self.outputs = {"emails": Table(data=emails)}

    @property
    def adapters(self):
        return super().adapters | {"emails": {str: model_adapters.table_to_str_adapter}}


class NewEmail(EmailIMAPBase):
    IS_TRIGGER = True

    class InitSchema(EmailIMAPBase.InitSchema):
        __doc__ = f"""Will trigger the flow for each new incoming email.
```warning
If you wish to process multiple emails or use them as source data, use the **kls::EmailSourceIMAP** block instead.
```
{IMAP_COMMON}"""

        # check_after: datetime = Field(
        #     default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        #     title="Check Emails After",
        #     examples=["2023-08-01 00:00:00"],
        #     format="hidden",
        #     description="Only emails received after this time will be processed.",
        # )

    DESC = InitSchema.__doc__

    SensitiveFields = (*EmailIMAPBase.SensitiveFields, "mailbox")

    class InputSchema(Node.InputSchema): ...

    class OutputSchema(EmailSchema): ...

    def __init__(
        self,
        init_inputs: InitSchema,
        is_password_encrypted: bool = False,
    ) -> None:
        if os.environ.get("PLURALLY_START_ISO_TIMESTAMP"):
            self.check_after = datetime.fromisoformat(os.environ["PLURALLY_START_ISO_TIMESTAMP"])
            logger.warning(f"Overriding check_after with PLURALLY_START_ISO_TIMESTAMP={self.check_after}")
        else:
            self.check_after = datetime.now(timezone.utc).replace(tzinfo=None)
        self.last_processed_id = None
        super().__init__(init_inputs, is_password_encrypted=is_password_encrypted)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_fixed(5),
    )
    def forward(self, _: InputSchema):
        try:
            imap_date = self.check_after.strftime("%d-%b-%Y")  # E.g., "01-Aug-2023"
            email_ids = self._fetch_email_ids(f"SINCE {imap_date}", ttl_hash=time.time() // 15)  # TTL of 15 secs

            self.outputs = None  # Will stop flow if no new emails are found

            candidates = []
            for email_id in email_ids:
                email_obj = self._fetch_email(email_id)
                if email_obj:
                    datetime_received_naive = get_naive_datetime(email_obj.datetime_received)

                    # need to use >= here because it is possible that some emails
                    # will have exactly the same timestamp.
                    if (datetime_received_naive >= self.check_after) and (not self.last_processed_id or email_id > self.last_processed_id):
                        candidates.append((datetime_received_naive, email_id, email_obj))

            if candidates:
                # take oldest email
                dt_received_naive, email_id, email = min(candidates)
                self.check_after = dt_received_naive
                self.last_processed_id = email_id
                self.outputs = email.model_dump()
                logger.debug(f"Email processed, setting check_after={self.check_after.isoformat()}")
        except imaplib.IMAP4.error as e:
            logger.error(f"Error processing email: {e}")
            self._server = None
            raise e

    @classmethod
    def _parse(cls, **kwargs):
        kwargs = load_from_json_dict(kwargs)
        return cls(cls.InitSchema(**kwargs), is_password_encrypted=True)


__all__ = ["EmailSourceIMAP", "NewEmail"]
