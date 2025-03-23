import json
import os
import smtplib
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

import tenacity
from loguru import logger
from pydantic import EmailStr, Field, field_validator

from plurally.crypto import decrypt, encrypt
from plurally.models.misc import File
from plurally.models.node import Node

GMAIL = """
To use this block with GMail you need to:
1. [First enable 2-step verification on your Google account](https://myaccount.google.com/signinoptions/two-step-verification/enroll-welcome).
2. [Create an App Password](https://myaccount.google.com/apppasswords). **Do not include spaces in the password**.
3. Use the following settings:
    - **SMTP Server**: `smtp.gmail.com`
    - **Port**: `587`
```warning
The password is the one generated in step 2, do not use the password of your Google account (the one you use to connect from the browser). **Do not include spaces in the password**.
```
"""

SMTP_COMMON = f"""
#### Common Email Providers
Follow the steps below to configure the block for some common email providers. If you encounter any issues, reach out to us on [Discord](https://discord.gg/aGpMJfYpDb).
```accordion
{json.dumps([
    {"title": "GMail", "content": GMAIL, "icon": "gmail"},
])}
```
"""


def get_email_input_schema(email_default):
    class SendEmailInputSchema(Node.InputSchema):
        email_address: EmailStr = Field(
            email_default,
            max_length=320,
            title="Email Address",
            description="The email address of the recipient.",
            examples=["recipient@domain.com"],
        )
        subject: str = Field(
            "",
            title="Subject",
            description="The subject of the email. If empty and replying to an email, the subject will be prefixed with 'Re:'.",
            examples=["Hello!"],
        )
        body: str = Field(
            "",
            title="Body",
            description="The body of the email.",
            examples=["This is the email body."],
        )
        reply_to: str = Field(
            "unspecified",
            title="Reply-To (Email ID)",
            description="The email ID to reply to.",
        )
        previous_email_subject_: str = Field(
            "",
            title="Previous Email Subject",
        )
        previous_email_body_: str = Field(
            "",
            title="Previous Email Body",
        )
        previous_email_datetime_received_: datetime = Field(
            "",
            title="Previous Email Datetime",
        )

        previous_email_sender_name_: str = Field(
            "",
            title="Previous Email Name",
        )

        previous_email_sender_email_: str = Field(
            "",
            title="Previous Email Sender's Email Address",
        )

        attachments: List[File] = Field([])

        @field_validator("subject")
        def validate_subject(cls, v):
            v = v.strip().replace("\n", " ").replace("\r", " ")
            if not v:
                raise ValueError("Subject cannot be empty.")
            return v

    return SendEmailInputSchema


def _login_server(username: EmailStr, password: str, smtp_server, port):
    logger.debug(f"Logging to {smtp_server}:{port}")
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    password = decrypt(password)
    server.login(username, password)
    logger.debug(f"Connected successfully to {smtp_server}:{port}")
    return server


def apply_reply_to(
    msg,
    body,
    subject,
    reply_to,
    previous_email_subject,
    previous_email_body,
    previous_email_datetime,
    previous_email_name,
    previous_email_sender_email,
):
    if reply_to and reply_to != "unspecified":
        assert all(
            [
                previous_email_subject,
                previous_email_body,
                previous_email_datetime,
                previous_email_name,
                previous_email_sender_email,
            ]
        ), "All previous email fields are required for replying to an email."
        if reply_to != "unspecified":
            msg["In-Reply-To"] = reply_to
            msg["References"] = reply_to
        subject = msg.get("Subject")
        if not subject:
            subject = previous_email_subject
        dt_format = previous_email_datetime.strftime("%a, %d %b %Y at %H:%M")
        previous_email_body = "\n".join([">" + ("" if line.startswith(">") else " ") + line for line in previous_email_body.splitlines()])
        body = f"{body}\n\n{dt_format}, {previous_email_name} <{previous_email_sender_email   }> wrote:\n{previous_email_body}"
    return body, subject


class SMTPBase(Node):
    ICON: str = "email"

    def __init__(self, init_inputs: Node.InitSchema):
        super().__init__(init_inputs)
        self._server = None  # lazy init
        self.username = None
        self.password = None
        self.smtp_server = None
        self.port = None
        self.fullname = None

    @property
    def from_email(self):
        return f"{self.fullname} <{self.username}>" if self.fullname else self.username

    @property
    def server(self):
        if self._server is None:
            self._server = _login_server(self.username, self.password, self.smtp_server, self.port)
        return self._server

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_fixed(5),
        retry=tenacity.retry_if_exception_type(smtplib.SMTPServerDisconnected),
    )
    def _forward(
        self,
        email_address,
        subject,
        body,
        reply_to=None,
        previous_email_subject=None,
        previous_email_body=None,
        previous_email_datetime=None,
        previous_email_name=None,
        previous_email_sender_email=None,
        attachments=None,
    ):
        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = email_address

        body, subject = apply_reply_to(
            msg,
            body,
            subject,
            reply_to,
            previous_email_subject,
            previous_email_body,
            previous_email_datetime,
            previous_email_name,
            previous_email_sender_email,
        )
        msg["Subject"] = subject

        if body.strip().startswith("<!DOCTYPE html>"):
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        # add attachments
        attachments = attachments or []
        for attachment in attachments:
            logger.debug(f"Attaching file: {attachment.filename}")

            part = MIMEApplication(attachment.content)
            part.add_header("Content-Disposition", f'attachment; filename="{attachment.filename}"')
            msg.attach(part)

        try:
            self.server.sendmail(
                self.from_email,
                email_address,
                msg.as_string(),
            )
        except smtplib.SMTPException as e:
            logger.error(f"Failed to send email: {e}")
            self._server = None
            raise e

        logger.debug(f"Email sent successfully from {self.from_email}")


class SendEmailSMTP(SMTPBase):
    class InitSchema(Node.InitSchema):
        __doc__ = f"""Send an email using SMTP.

        {SMTP_COMMON}"""

        class Config:
            json_schema_extra = {
                "description": "The inputs of this block represents the configuration for sending emails from an SMTP server.\n\nAll passwords are encrypted and private.",
            }

        username: str = Field(
            title="Email",
            examples=["myname@gmail.com"],
            format="email",
            description="Your email address to send emails from.",
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
            description="The password for your email address.",
            min_length=1,
            max_length=1000,
            json_schema_extra={
                "is-encrypted": True,
                "uiSchema": {
                    "ui:emptyValue": None,
                    "ui:widget": "password",
                    "ui:placeholder": "Enter your password",
                },
            },
        )
        smtp_server: str = Field(
            title="SMTP Server",
            description="The SMTP server's address of your email provider.",
            examples=["smtp.gmail.com"],
            min_length=1,
            max_length=100,
        )
        fullname: str = Field(
            "",
            title="Full name",
            description="Your name to be displayed in the email.",
            examples=["John Doe"],
            max_length=100,
        )
        port: int = Field(
            587,
            title="Port",
            description="The SMTP server's port of your email provider.",
            examples=[587],
            json_schema_extra={
                "advanced": True,
            },
        )

        @field_validator("fullname", mode="after")
        def validate_fullname(cls, value):
            value = value.strip().replace("\n", " ").replace("\r", " ")
            return value

    DESC = InitSchema.__doc__

    SensitiveFields = ("username", "password", "smtp_server", "fullname", "port")
    InputSchema = get_email_input_schema(...)

    class OutputSchema(Node.OutputSchema): ...

    def __init__(
        self,
        init_inputs: InitSchema,
        is_password_encrypted: bool = False,
    ):
        super().__init__(init_inputs)
        self.username = init_inputs.username
        self.fullname = init_inputs.fullname

        if is_password_encrypted:
            self.password = init_inputs.password
        else:
            self.password = encrypt(init_inputs.password)

        self.smtp_server = init_inputs.smtp_server
        self.port = init_inputs.port

    def forward(self, node_input: InputSchema):
        return self._forward(
            node_input.email_address,
            node_input.subject,
            node_input.body,
            node_input.reply_to,
            node_input.previous_email_subject_,
            node_input.previous_email_body_,
            node_input.previous_email_datetime_received_,
            node_input.previous_email_sender_name_,
            node_input.previous_email_sender_email_,
            attachments=node_input.attachments,
        )

    def serialize(self):
        payload = super().serialize()
        payload.update(
            {
                "username": self.username,
                "smtp_server": self.smtp_server,
                "port": self.port,
                "fullname": self.fullname,
                "password": self.password,
            }
        )
        return payload

    @classmethod
    def _parse(cls, **kwargs):
        return cls(cls.InitSchema(**kwargs), is_password_encrypted=True)


class NotifyInputSchemaBase(Node.InputSchema):
    subject: str = Field(
        "",
        title="Subject",
        description="The subject of the email.",
        examples=["Hello!"],
    )
    body: str = Field(
        "",
        title="Body",
        description="The body of the email.",
        examples=["This is the email body."],
    )
    attachments: List[File] = Field([])


class NotifyMeDynamic(SMTPBase):
    class InitSchema(Node.InitSchema):
        __doc__ = """Send an email notification from Plurally, using dynamic email address"""

    class InputSchema(NotifyInputSchemaBase):
        email: EmailStr = Field(
            ...,
            title="Email",
            max_length=320,
            examples=["hello@gmail.com"],
        )

    NECESSARY_ENVS = [
        "PLURALLY_SMTP_USERNAME",
        "PLURALLY_SMTP_PASSWORD",
        "PLURALLY_SMTP_SERVER",
        "PLURALLY_SMTP_PORT",
    ]

    def forward(self, node_input: InputSchema):
        if self.username is None:
            for env in self.NECESSARY_ENVS:
                assert env in os.environ, f"Missing environment variable: {env}"
            self.username = os.environ["PLURALLY_SMTP_USERNAME"]
            self.fullname = "Plurally"
            self.password = encrypt(os.environ["PLURALLY_SMTP_PASSWORD"])
            self.smtp_server = os.environ["PLURALLY_SMTP_SERVER"]
            self.port = int(os.environ["PLURALLY_SMTP_PORT"])

        body = node_input.body
        body += "\n\nStreamline the tedious - tryplurally.com/en."

        return self._forward(
            node_input.email,
            node_input.subject,
            body,
            attachments=node_input.attachments,
        )


class NotifyMe(SMTPBase):
    class InitSchema(Node.InitSchema):
        __doc__ = """Send an email notification from Plurally"""
        email: EmailStr = Field(
            title="Email",
            max_length=320,
            examples=["emma@gmail.com"],
            format="email",
            description="The email address where you want to receive notifications.",
            json_schema_extra={
                "uiSchema": {
                    "ui:placeholder": "Enter your email address",
                }
            },
        )

    DESC = InitSchema.__doc__

    SensitiveFields = ("email",)

    InputSchema = NotifyInputSchemaBase

    class OutputSchema(Node.OutputSchema): ...

    NECESSARY_ENVS = [
        "PLURALLY_SMTP_USERNAME",
        "PLURALLY_SMTP_PASSWORD",
        "PLURALLY_SMTP_SERVER",
        "PLURALLY_SMTP_PORT",
    ]

    def __init__(self, init_inputs: InitSchema):
        super().__init__(init_inputs)
        self.email = init_inputs.email

    def forward(self, node_input: InputSchema):
        if self.username is None:
            for env in self.NECESSARY_ENVS:
                assert env in os.environ, f"Missing environment variable: {env}"
            self.username = os.environ["PLURALLY_SMTP_USERNAME"]
            self.fullname = "Plurally"
            self.password = encrypt(os.environ["PLURALLY_SMTP_PASSWORD"])
            self.smtp_server = os.environ["PLURALLY_SMTP_SERVER"]
            self.port = int(os.environ["PLURALLY_SMTP_PORT"])

        return self._forward(
            self.email,
            node_input.subject,
            node_input.body,
            attachments=node_input.attachments,
        )

    def serialize(self):
        return super().serialize() | {"email": self.email}
