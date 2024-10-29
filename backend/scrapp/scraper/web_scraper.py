import logging
import time
import traceback
from typing import Literal, NotRequired, Optional, Union, Unpack

from lib.dependency_trees import topological_sort_dependency_tree
from typing_extensions import TypedDict

from .util import QueryArgs, QuerySet, Thread
from .web_page3 import BaseWebPage

DEFAULT_LOG_FORMATTER = logging.Formatter(
    "[{levelname:^10}] [ {asctime} ] [{threadName:^20}]  {message}",
    "%I:%M:%S %p",
    style="{",
)
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(DEFAULT_LOG_FORMATTER)


def format_dict_as_list(input: dict | list, bullets: Literal["-", "num"] = "-") -> str:
    """
    Format a dictionary's attributes out in a list-like display.
    """
    if bullets == "num":
        bulletting = [f"{i}." for i in range(len(input))]
    else:
        bulletting = ["-"] * len(input)

    idx, res_str = 0, ""
    for inp in input:
        if type(input) == dict:
            res_str += f"\n\t{bulletting[idx]} {inp} = {input[inp]}"
        elif type(input) == list:
            res_str += f"\n\t{bulletting[idx]} {inp}"
        idx += 1

    return res_str


def format_dict_as_list_inline(input: dict) -> str:
    """
    Format a dictionary's attributes out in a list-like display.
    """
    idx, res_str = 0, ""
    for key, value in input.items():
        res_str += f"{key} = {value}, "
        idx += 1

    return res_str.strip(", ")


class WebScraperKwargs(TypedDict):
    web_pages: NotRequired[dict[str, BaseWebPage]]
    log_level: NotRequired[int]
    download_rate: NotRequired[int]
    active: NotRequired[bool]
    align: NotRequired[Union[Literal["nested"], Literal["inline"]]]


class BaseWebScraper(Thread):

    def __init__(self, name: str, *args, **kwargs: Unpack[WebScraperKwargs]) -> None:
        super().__init__(name, *args, **kwargs)

        self._web_pages: dict[str, BaseWebPage] = kwargs.get("web_pages") or {}
        self._configured: bool = False

        self.download_rate = kwargs.get("download_rate", 5)
        self.last_download_time = time.time()

        self.alignment = kwargs.get("align", "inline")

    @property
    def is_configured(self):
        return self._configured

    def __str__(self):
        return f"{self.name}Scraper"

    def add_web_page(self, web_page: BaseWebPage):
        """
        Add a web page configuration to the scraper.
        """
        self._web_pages[web_page.name] = web_page

        # web_page.set_logger(self.logger)
        web_page.bind_scraper(self)

    def configure(self):
        """
        Configure the web_pages based on dependency tree.
        Must be run before the datascraper starts.
        """
        # Sort the web pages by order of dependencies.
        sorted: list[str] = topological_sort_dependency_tree(dependency_tree=self._web_pages)  # type: ignore

        web_pages: dict[str, BaseWebPage] = {}

        # Configure each web page in order of how they are sorted
        for web_page_name in sorted:
            self._web_pages[web_page_name].configure()

        if self.alignment == "nested":
            # Take the first item as the current page
            current_page = web_pages[sorted[0]] = self._web_pages[sorted[0]]

            # For the remaining pages, nest them together
            for web_page_name in sorted[1:]:
                nested_web_page = self._web_pages[web_page_name]
                current_page.add_nested_web_page(web_page=nested_web_page)
                current_page = nested_web_page

        else:
            for web_page_name in sorted:
                web_pages[web_page_name] = self._web_pages[web_page_name]

        self._web_pages = web_pages

        self._configured = True

    def execute(self):
        """
        Make a forward pass downloading and saving each dataset in
        the scraper's configuration. To add more web pages, use the 'add_web_page'
        method.
        """
        if not self._web_pages:
            raise Exception(
                "No web pages defined - to add web pages, use the 'add_web_page' method."
            )

        for web_page in self._web_pages.values():
            if self.RUNNING == False:
                break

            web_page.process()

    def run(self):

        if not self.is_configured:
            raise Exception(
                "Must call '.configure()' on the scraper before running it."
            )

        super().run()
