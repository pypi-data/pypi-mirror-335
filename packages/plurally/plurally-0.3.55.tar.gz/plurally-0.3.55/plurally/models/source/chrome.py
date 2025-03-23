from pydantic import Field

from plurally.models.node import Node


class Chrome(Node):
    IS_TRIGGER = True
    ICON = "chrome"

    class InitSchema(Node.InitSchema):
        __doc__ = "Creates a connection between your flow and Plurally's Chrome extension."
        # selectors: List[str] = Field(
        #     title="Selectors",
        #     description="The CSS selectors of the elements you want to extract.",
        #     json_schema_extra={
        #         "uiSchema": {
        #             "ui:widget": "textarea",
        #             "ui:options": {"rows": 10},
        #         }
        #     },
        # )

    DESC = InitSchema.__doc__

    class InputSchema(Node.InputSchema): ...

    class OutputSchema(Node.OutputSchema):
        page_url: str = Field(
            title="Page URL",
            description="The URL of the page where the data was extracted.",
        )
        html: str = Field(
            title="HTML",
            description="The HTML code transferred from the Chrome extension.",
            json_schema_extra={"uiSchema": {"ui:widget": "textarea", "ui:options": {"rows": 10}}},
        )

    def start_worker(self) -> bool:
        return True
