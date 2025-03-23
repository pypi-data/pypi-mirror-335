import enum
import os
import re
import urllib
from typing import List

import requests
from bs4 import BeautifulSoup
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field

from plurally.models.action.hunterio import GuessEmail
from plurally.models.env_vars import BaseEnvVars
from plurally.models.misc import Table
from plurally.models.node import Node


class ScrapePageBase(Node):
    class OutputSchema(Node.OutputSchema):
        content: str = Field(
            title="Content",
            description="The content of the page",
        )

    def _get_html_content(self, url):
        req = requests.get(url)
        req.raise_for_status()

        return req.text

    def scrape(self, url, selector):
        from bs4 import BeautifulSoup

        html_content = self._get_html_content(url)

        soup = BeautifulSoup(html_content, "html.parser")
        selected = soup.select_one(selector)
        if selected is None:
            self.outputs = {"content": ""}
        else:
            content = selected.get_text()
            self.outputs = {"content": content}


class ScrapePageDynamic(ScrapePageBase):
    ICON = "scrape-one"

    class InitSchema(Node.InitSchema):
        """Scrape the content of a webpage, with dynamic inputs"""

    class InputSchema(Node.InputSchema):
        url: str = Field(
            title="URL",
            description="The URL of the page to scrape",
            examples=["https://example.com"],
        )
        selector: str = Field(
            "body",
            title="Selector",
            description="The selector to use to scrape the content, defaults to 'body' which will scrape the entire page",
            examples=["h1"],
        )

    DESC = InitSchema.__doc__

    def forward(self, node_inputs):
        return self.scrape(node_inputs.url, node_inputs.selector)


class ScrapePagesDynamic(ScrapePageBase):
    ICON = "scrape-many"

    class InitSchema(Node.InitSchema):
        """Scrape the content of multiple webpages.\n\nEach row in the input table should contain a url and a selector.\n\nInput columns should be named 'url' and 'selector'. The output will be a table with the content of the pages, with one column named 'content'."""

    class InputSchema(Node.InputSchema):
        urls_and_selectors: Table = Field(
            title="URLs and Selectors",
            description="The urls and selectors to use to scrape the content",
        )

    class OutputSchema(Node.OutputSchema):
        contents: Table = Field(
            title="Contents",
            description="The contents of the pages, with one column named 'content'.",
        )

    DESC = InitSchema.__doc__

    def forward(self, node_inputs):
        urls_and_selectors = node_inputs.urls_and_selectors
        if urls_and_selectors.is_empty():
            self.outputs = {"contents": Table(data=[])}
            return

        contents = []
        if not all(col in urls_and_selectors.columns for col in ["url", "selector"]):
            raise ValueError("Input table must have columns 'url' and 'selector'")

        for row in urls_and_selectors.data:
            url = row["url"]
            selector = row["selector"]
            self.scrape(url, selector)
            contents.append({"content": self.outputs["content"]})
        self.outputs = {"contents": Table(data=contents)}


class ScrapePageStatic(ScrapePageBase):
    ICON = "scrape-one"

    class InitSchema(Node.InitSchema):
        """Scrape the content of a webpage, with static inputs"""

        url: str = Field(
            title="URL",
            description="The URL of the page to scrape",
            examples=["https://example.com"],
            min_length=1,
            json_schema_extra={
                "uiSchema": {
                    "ui:widget": "url",
                    "ui:placeholder": "https://example.com",
                }
            },
        )
        selector: str = Field(
            "body",
            title="Selector",
            description="The selector to use to scrape the content, defaults to 'body' which will scrape the entire page",
            examples=["h1"],
            min_length=1,
            json_schema_extra={
                "uiSchema": {
                    "ui:placeholder": "Html selector, e.g. h1. If not sure use 'body'.",
                }
            },
        )

    class InputSchema(Node.InputSchema): ...

    DESC = InitSchema.__doc__

    def __init__(self, init_inputs: InitSchema, outputs=None):
        self.url = init_inputs.url
        self.selector = init_inputs.selector
        super().__init__(init_inputs, outputs)

    def forward(self, _: Node.InputSchema):
        return self.scrape(self.url, self.selector)

    def serialize(self):
        return super().serialize() | {
            "url": self.url,
            "selector": self.selector,
        }


class SelectorMode(enum.Enum):
    TEXT = "TEXT"
    HTML = "HTML"


class HtmlSelector(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    selector: str = Field(
        "",
        title="Selector",
        description="The CSS selector to extract the data. Leave empty to extract the entire HTML content.",
        examples=["h1"],
    )
    mode: SelectorMode = Field(
        SelectorMode.TEXT.value,
        title="Mode",
        description=f"{SelectorMode.TEXT.value} will remove the Html tags.",
        examples=[SelectorMode.TEXT.value],
    )


class HtmlParser(Node):
    ICON = "scrape-one"

    class InitSchema(Node.InitSchema):
        """Parse HTML content"""

        selectors: List[HtmlSelector] = Field(
            title="Selectors",
            description="The list of selectors to extract data from the HTML content.",
            min_items=1,
            examples=[{"name": "title", "selector": "h1"}],
            json_schema_extra={
                "name_singular": "Selector",
                "uiSchema": {
                    "items": {
                        "ui:label": False,
                        "ui:grid": [
                            ("selector", 8),
                            ("mode", 4),
                        ],
                        "selector": {
                            "ui:placeholder": "Html selector, e.g. h1",
                        },
                    },
                },
                "uniqueItems": True,
            },
        )

    DESC = InitSchema.__doc__

    class InputSchema(Node.InputSchema):
        html: str = Field(
            title="HTML",
            description="The HTML content to parse.",
            examples=["<html><body><h1>Hello World</h1></body></html>"],
        )

    class OutputSchema(Node.OutputSchema):
        text: str = Field(
            title="Text",
            description="The extracted text from the HTML content.",
        )

    def __init__(self, init_inputs: InitSchema):
        self.selectors = init_inputs.selectors
        super().__init__(init_inputs)

    def serialize(self):
        return super().serialize() | {
            "selectors": [(s if isinstance(s, dict) else s.model_dump()) for s in self.selectors],
        }

    def forward(self, node_inputs: Node.InputSchema):
        soup = BeautifulSoup(node_inputs.html, "html.parser")

        txts = []
        for selector in self.selectors:
            if selector.selector:
                for selected in soup.select(selector.selector):
                    if selector.mode == SelectorMode.HTML.value:
                        dirty = str(selected)
                    elif selector.mode == SelectorMode.TEXT.value:
                        dirty = selected.get_text()
                    else:
                        raise ValueError(f"Invalid mode: {selector.mode}")
                    clean_text = re.sub(r"\n+", "\n", dirty.strip())
                    txts.append(clean_text)
            else:
                txts.append(soup.get_text())
        self.outputs = {"text": "\n".join(txts)}


class SearchResult(BaseModel):
    link: str
    title: str
    snippet: str


class GoogleSearch(Node):
    class EnvVars(BaseEnvVars):
        GOOGLE_SEARCH_API_KEY: str = Field(description="API key for the Google Search API")

    class InitSchema(Node.InitSchema):
        """Search the internet"""

        search_engine_id: str = Field(
            title="Google Search Engine ID",
            description="The search engine to use, can create one here: https://programmablesearchengine.google.com/controlpanel/all",
        )

    class InputSchema(Node.InputSchema):
        query: str = Field(
            title="Query",
            description="The search query",
            examples=["plurally"],
        )

    class OutputSchema(Node.OutputSchema):
        results: List[SearchResult] = Field(
            title="Results",
            description="The search results",
        )

    def __init__(self, init_inputs, outputs=None):
        self.search_engine_id = init_inputs.search_engine_id
        super().__init__(init_inputs, outputs)

    def forward(self, node_input):
        key = os.environ.get("GOOGLE_SEARCH_API_KEY")
        assert key, "GOOGLE_SEARCH_API_KEY is not set"
        try:
            res = requests.get(
                f"https://www.googleapis.com/customsearch/v1?key={key}&cx={self.search_engine_id}&q={urllib.parse.quote_plus(node_input.query)}",
            )
            res.raise_for_status()
            self.outputs = {
                "results": [
                    SearchResult(
                        link=item["link"],
                        title=item["title"],
                        snippet=item["snippet"],
                    )
                    for item in res.json().get("items", [])
                ]
            }
        except Exception as e:
            logger.exception(e)
            self.outputs = {"results": []}

    def serialize(self):
        return super().serialize() | {
            "search_engine_id": self.search_engine_id,
        }


__all__ = [
    "ScrapePageDynamic",
    "ScrapePageStatic",
    "ScrapePagesDynamic",
    "HtmlParser",
    "GuessEmail",
    "GoogleSearch",
]
