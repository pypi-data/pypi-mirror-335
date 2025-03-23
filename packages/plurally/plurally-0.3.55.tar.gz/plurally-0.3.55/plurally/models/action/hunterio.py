import os

import requests
from pydantic import Field

from plurally.models.env_vars import BaseEnvVars
from plurally.models.node import Node


class GuessEmail(Node):
    ICON = "hunter"

    class EnvVars(BaseEnvVars):
        HUNTER_API_KEY: str = Field(
            description="The Hunter.io API key",
            examples=["abc123"],
            json_schema_extra={
                "help": "Create an account and find your API key at [https://hunter.io/api-keys](https://hunter.io/api-keys) to get an API key."
            },
        )

    class InitSchema(Node.InitSchema):
        """Uses Hunter.io to guess the email address of a person at a given company."""

    DESC = "Guess the email address of a person at a company using Hunter.io"

    class InputSchema(Node.InputSchema):
        firstname: str = Field(description="The first name of the person")
        lastname: str = Field(description="The last name of the person")
        company_domain: str = Field(description="The domain of the company")

    class OutputSchema(Node.OutputSchema):
        email: str = Field(description="The guessed email address")
        score: int = Field(description="The confidence score of the guess, from 0 to 100", ge=0, le=100)

    def forward(self, inputs: InputSchema) -> OutputSchema:
        key = os.environ.get("HUNTER_API_KEY")
        if not key:
            raise ValueError("HUNTER_API_KEY is required")
        r = requests.get(
            f"https://api.hunter.io/v2/email-finder?domain={inputs.company_domain}&first_name={inputs.firstname}&last_name={inputs.lastname}&api_key={key}"
        )
        data = r.json()
        self.outputs = {
            "email": data["data"]["email"],
            "score": data["data"]["score"],
        }
