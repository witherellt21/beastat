from typing import Callable, Literal, NotRequired, Optional, Unpack

import pandas as pd
from lib.dependency_trees import (
    DependencyKwargs,
    DependentObject,
    topological_sort_dependency_tree,
)
from lib.pydantic_validator import PydanticValidatorMixin
from lib.util import combine_lists_of_dicts
from typing_extensions import TypedDict

from .html_table import BaseHTMLTable
from .util import QueryArgs, QuerySet


def validate_url_arguments(url: str) -> int:
    """
    Validate bracket configuration in a format string.
    """

    open = False
    total = 0
    for char in url:
        if char == "}":
            if not open:
                raise Exception(
                    "Invalid format of brackets {}. Closing brackets must be preceded by an opening bracket ."
                )

            open = False
            total += 1

        elif char == "{":
            if open:
                raise Exception(
                    "Invalid format of brackets {}. Opening brackets must be closed before a new open bracket can appear."
                )

            open = True

    if open:
        raise Exception(
            "Invalid format of brackets {}. All opening brackets must be closed by closing brackets."
        )

    return total


class WebPageKwargs(TypedDict):
    html_tables: NotRequired[Optional[dict[str, "BaseHTMLTable"]]]
    default_query_set: NotRequired[Optional[QuerySet]]
    extract_tables: NotRequired[Callable[[str], list[pd.DataFrame]]]


class WebPageDependencyKwargs(DependencyKwargs):
    table_name: str
    query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]]


class BaseWebPage(
    DependentObject["BaseWebPage", "WebPageDependencyKwargs"],
    PydanticValidatorMixin,
):
    """
    Base class for a web page to be scraped.

    Args:
        name: A name for the web page, used in aligning the dependency tree.
        base_download_url: A string for the url of the webpage to ping. Accepts template strings to be used with query sets.

    Keyword Args
        html_tables: Name-table pairing of html tables that should be extract from the webpage
        default_query_set: If the query set does not depend on other data, specify a default query set
        extract_tables: Override the extract_tables function for how tables should be parsed from the webpage. Default is pd.read_html(url, extract_links="body").

    """

    def __init__(
        self,
        *,
        name: str,
        base_download_url: str,
        **kwargs: Unpack[WebPageKwargs],
    ):
        super().__init__(name=name, validator=WebPageDependencyKwargs)

        # constants specified in intantiation
        self._base_download_url: str = base_download_url
        self._html_tables: dict[str, BaseHTMLTable] = kwargs.get("html_tables") or {}
        self._default_query_set: Optional[QuerySet] = (
            kwargs.get("default_query_set") or []
        )
        self._extract_tables = kwargs.get(
            "extract_tables", lambda url: pd.read_html(url, extract_links="body")
        )

        self.nested_web_pages: list["BaseWebPage"] = []

        # whether the current staged data has been pulled from cache or downloaded
        self.data_source: Literal["cached", "downloaded"] = "downloaded"

        # set whether or not the page depends on a dynamic query set
        self.static: bool = not validate_url_arguments(self.base_download_url)

    def __str__(self):
        return self.name

    @property
    def base_download_url(self) -> str:
        """
        Public getter funcction for the _base_download_url.
        """
        return self._base_download_url

    @property
    def html_tables(self) -> dict[str, BaseHTMLTable]:
        """
        Public getter function for the _html_tables.
        """
        return self._html_tables

    @property
    def query_set(self) -> Optional[QuerySet]:
        """
        Get the query set. If it relies on dependences, extract it.
        """

        if self.static:
            return None

        elif self.dependencies:
            query_set_extractions = []

            for dependency in self.dependencies:
                # source_table = dependency.source
                # TODO: verify these links are accurate in configure
                dependency_data = dependency.source._html_tables[
                    dependency.meta.table_name
                ].data

                if dependency_data.empty:
                    raise Exception(
                        f"Dataset {self.name} processed before dependency {dependency.source.name}."
                    )

                query_set_extractions.append(
                    dependency.meta.query_set_provider(dependency_data)
                )

            return combine_lists_of_dicts(*query_set_extractions)

        elif self._default_query_set:
            return self._default_query_set

        else:
            raise Exception(
                "Must specify a default query set if no dependencies are provided."
            )

    def get_download_url(self, *, query_args: QueryArgs) -> str:
        """
        Get the download url for the web page by formatting the given query.
        """
        return self.base_download_url.format(**query_args)

    def add_table(self, *, table: BaseHTMLTable) -> None:
        """
        Add a table to download from the web page.
        """
        self._html_tables[table.name] = table

    def add_nested_web_page(self, *, web_page: "BaseWebPage") -> None:
        """
        Add a nested web page to the current web page.
        """
        self.nested_web_pages.append(web_page)

    def configure(self) -> None:
        """
        Configure the web page tables by sorting dependencies.
        """
        for table in self.html_tables.values():
            for dependency in table.serializer.dependencies.values():
                table.add_dependency(source=self.html_tables[dependency])

        sorted = topological_sort_dependency_tree(dependency_tree=self._html_tables)  # type: ignore

        html_tables: dict[str, BaseHTMLTable] = {}

        for table_name in sorted:
            html_tables[table_name] = self._html_tables[table_name]

        self._html_tables = html_tables

        self._configured = True

    def is_configured(self) -> bool:
        """
        Returns whether or not the web page has been configured (call .configure() to
        configure the web page)
        """
        return self._configured

    def load_cached_data(self, *, query_args: Optional[QueryArgs] = None) -> None:
        """
        Get any existing data for the given query args in the existing table configuration.
        """
        for table_name, table in self._html_tables.items():
            table.data = table.cached_data(query_args=query_args)

            if not table.data.empty:
                table.data_source = "cached"
            else:
                table.data_source = "downloaded"

    def extract_tables(self, *, url: str) -> list[pd.DataFrame]:
        """
        Extract all tables for the html web page.
        """
        try:
            return self._extract_tables(url)
        except Exception as e:
            raise Exception(f"Error downloading data from {url}. {e}")
