import logging
import time
from collections import deque
from datetime import datetime
from typing import Any, Callable, Literal, NotRequired, Optional, Union, Unpack

import pandas as pd
from lib.dependency_trees import DependencyKwargs, DependentObject
from lib.pydantic_validator import PydanticValidatorMixin
from scrapp.core.exceptions import ColumnDoesNotExist, StageEmpty
from scrapp.tables.base_table import AdvancedQuery
from scrapp.utils.string_formatting import generate_inline_list
from typing_extensions import TypedDict

from .configurable import Configurable
from .extractors import href_table_extractor
from .html_table import DataframeController, DataframeControllerInheritance
from .util import QueryArgs, QuerySet

DEFAULT_LOG_FORMATTER = logging.Formatter(
    "{message}",
    "%I:%M:%S %p",
    style="{",
)
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(DEFAULT_LOG_FORMATTER)


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
    default_query_set: NotRequired[Optional[QuerySet]]
    extract_tables: NotRequired[Callable[[str], list[pd.DataFrame]]]
    # query_cached_condition: NotRequired[]


class WebPageDependencyKwargs(DependencyKwargs):
    table_name: str
    query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]]


class AdvancedQueryDict(TypedDict):
    greater_than: NotRequired[dict[str, Union[int, float, datetime]]]
    less_than: NotRequired[dict[str, Union[int, float, datetime]]]
    equal_to: NotRequired[dict[str, Any]]
    in_: NotRequired[dict[str, list[Any]]]
    startswith: NotRequired[dict[str, str]]


class CachedQueryConfig(TypedDict):
    from_args: list[str]
    query: AdvancedQueryDict


# class TableInheritance(TypedDict):
#     web_page: "BaseWebPage"
#     source_table: DataframeController
#     fields: list[str]


class TableInheritance(DataframeControllerInheritance):
    """
    Gets inherited data from a source controller.
    """

    def __init__(
        self,
        web_page: "BaseWebPage",
        source_table: DataframeController,
        fields: list[str],
        on_keys: dict[str, str],
    ) -> None:
        source = source_table.data

        for field in fields:
            if field not in source.data_fields:
                raise ColumnDoesNotExist(field, source.data_fields)

        self.web_page = web_page
        self.source_table: "DataframeController" = source_table

        super().__init__(source, fields, on_keys=on_keys)


# class TableConfig(TypedDict):
#     table: DataframeController
#     identifier: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]]
#     stale_condition: Callable[[], bool] | AdvancedQuery | CachedQueryConfig | None
#     inheritances: list[TableInheritance]
# dependencies: list[TableInheritance]


# class NestedWebPage(TypedDict):
#     web_page: "BaseWebPage"
#     query_set_provider: Callable[["BaseWebPage"], list[dict[str, str]]]


class WebTableConfig:

    def __init__(
        self,
        table: DataframeController,
        identifier: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]],
        stale_condition: Callable[[], bool] | AdvancedQuery | CachedQueryConfig | None,
        inheritances: list[TableInheritance],
        # dependencies: list[]
    ):
        self.table = table
        self.identifier = identifier
        self.stale_condition = stale_condition
        self.inheritances = inheritances

    # def perform_inheritance(self, inheritance):
    def has_staged_data(self):
        return not self.table.data.stage.empty

    def savable(self):
        return all(
            [dependency.source.is_cached() for dependency in self.table.dependencies]
        )

    def local_inheritances(self, source_page: "BaseWebPage"):
        for inheritance in self.inheritances:
            if inheritance.web_page == source_page:
                yield inheritance

    def external_inheritances(self, source_page: "BaseWebPage"):
        for inheritance in self.inheritances:
            if inheritance.web_page != source_page:
                yield inheritance

    def perform_cached_inheritances(self):
        for inheritance in self.inheritances:
            if (
                not inheritance.source_table.data.commits.empty
                or inheritance.web_page.is_cached()
            ):
                # inherit the data into the target table
                data = inheritance.perform()
                data = self.table.serializer.post_validate(data)
                self.table.data.update(data)


class RateLock:

    def __init__(self, rate: int):
        self.__rate = rate

        # Ensures we are ready to download upon creation
        self.__last_execute_time = time.time() - rate

    @property
    def rate(self):
        return self.__rate

    def set_rate(self, value):
        self.__rate = value

    def reset(self):
        self.__last_execute_time = time.time()

    def acquire(self):
        """
        Wait for the lock to be open.
        """
        wait = max(self.__last_execute_time - time.time() + self.__rate, 0)

        if wait > 0:
            time.sleep(wait)


class BaseWebPage(
    DependentObject["BaseWebPage", "WebPageDependencyKwargs"],
    Configurable,
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
        log_level: int = logging.INFO,
        download_rate: int = 5,
        query_cached_condition: Literal["all", "any"] = "any",
        **kwargs: Unpack[WebPageKwargs],
    ):
        super().__init__(name=name, validator=WebPageDependencyKwargs)
        Configurable.__init__(self)

        # constants specified in intantiation
        self._base_download_url: str = base_download_url
        self.__table_configs: dict[str, WebTableConfig] = {}
        self.__tables: list[DataframeController] = [
            config.table for config in self.__table_configs.values()
        ]
        self.query_cached_condition = query_cached_condition

        self._default_query_set: Optional[QuerySet] = (
            kwargs.get("default_query_set") or []
        )
        self._extract_tables = kwargs.get("extract_tables", href_table_extractor)
        self.download_lock = RateLock(download_rate)

        self.nested_web_pages: list["NestedWebPage"] = []

        # whether the current staged data has been pulled from cache or downloaded
        self.data_source: Literal["cached", "downloaded"] = "downloaded"

        # set whether or not the page depends on a dynamic query set
        self.static: bool = not validate_url_arguments(self.base_download_url)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.logger.addHandler(STREAM_HANDLER)

    def __str__(self):
        return self.name

    @property
    def base_download_url(self) -> str:
        """
        Public getter funcction for the _base_download_url.
        """
        return self._base_download_url

    @base_download_url.setter
    def base_download_url(self, url: str) -> None:
        """
        Public getter funcction for the _base_download_url.
        """
        self._base_download_url = url

    @property
    def table_configs(self) -> dict[str, WebTableConfig]:
        """
        Public getter function for the _html_tables.
        """
        return self.__table_configs

    def bind_scraper(self, scraper):
        self.scraper = scraper

        self.logger = scraper.logger

    @property
    def download_rate(self):
        return self.download_lock.rate

    @download_rate.setter
    def download_rate(self, value: int):
        self.download_lock.set_rate(value)

    def get_download_url(self, *, query_args: QueryArgs) -> str:
        """
        Get the download url for the web page by formatting the given query.
        """
        return self.base_download_url.format(**query_args)

    def add_table(
        self,
        table: DataframeController,
        *,
        identification_function: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]],
        stale_condition: Callable[[], bool] | AdvancedQuery | CachedQueryConfig | None,
        inheritances: Optional[list[TableInheritance]] = None,
        # dependencies: list[TableInheritance] = [],
    ) -> None:
        """
        Add a table to download from the web page.
        """
        self.__table_configs[table.name] = WebTableConfig(
            table, identification_function, stale_condition, inheritances or []
        )

        self.__tables.append(table)

    def add_table_inheritance(
        self,
        table: str,
        source_table: str | DataframeController,
        fields: list[str],
        web_page: Optional["BaseWebPage"] = None,
        *,
        on_keys: dict[str, str] = {},
    ):
        """
        Add an inheritance to the web page. Inheritances take data from another table
        (possibly another web page).

        If the inherited table is one of this web page:
            perform the inheritance to pull data across tables
        If the inherited table is from another web page:
            if that web page is a subpage of the current page:
                create the queryset
                process it for queryset
            if the web page is an indpendent page:
                process the web page

            perfrom the inheritance


        """
        web_page = web_page or self

        if isinstance(source_table, str):
            source = web_page.table_configs[source_table].table

        elif isinstance(source_table, DataframeController):
            source = source_table

        else:
            raise Exception(
                "'source_table' must be a string matching the name of a table on the web page or a DataframeController"
            )

        # on_keys = on_keys or self.__table_configs[table].table.data.primary_keys
        # if not on_keys:
        #     on_keys = {
        #         key: key for key in self.__table_configs[table].table.data.primary_keys
        #     }

        # else:

        on_keys.update(
            {
                key: key
                for key in self.__table_configs[table].table.data.primary_keys
                if key not in on_keys.values()
            }
        )

        self.__table_configs[table].inheritances.append(
            TableInheritance(web_page, source, fields, on_keys=on_keys)
        )

        # if isinstance(table, DataframeController):
        #     table.add_inheritance(source, fields)
        # else:
        #     self.__table_configs[table]["table"].add_inheritance(source, fields)

    def add_dependency(
        self,
        *,
        source: "BaseWebPage",
        table_name: str,
        query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]],
    ):
        # Lets find a way to confirm the dependency exists
        meta_data = {"table_name": table_name, "query_set_provider": query_set_provider}

        return super().add_dependency(source=source, meta_data=meta_data)

    def add_nested_web_page(
        self,
        web_page: "NestedWebPage",
    ) -> None:
        """
        Add a nested web page to the current web page.
        """
        web_page.bind(self)

        self.nested_web_pages.append(web_page)

    def configure(self) -> None:
        """
        Configure the web page tables by sorting dependencies.
        """
        # Add dependencies to our table based on the serializers dependencies
        # for table in self.__html_tables.values():
        #     for dependency in table.serializer.dependencies.values():
        #         table.add_dependency(source=self.html_tables[dependency])

        # sorted = topological_sort_dependency_tree(dependency_tree=self.__table_configs)  # type: ignore

        # html_tables: dict[str, DataframeController] = {}

        # for table_name in sorted:
        #     html_tables[table_name] = self.__table_configs[table_name]

        # self.__table_configs = html_tables

        for config in self.__table_configs.values():
            for inheritance in config.inheritances:
                if inheritance.web_page != self and not inheritance.web_page.configured:
                    inheritance.web_page.configure()

        for web_page in self.nested_web_pages:
            web_page.configure()

        super().configure()

    def load_cached_data(self, *, query_args: Optional[QueryArgs] = None) -> None:
        """
        Get any existing data for the given query args in the existing table configuration.
        """
        # data_source = "cached"
        any_cached = False
        all_cached = True

        # For each table in the configuration, load its data from cache
        # If all tables successfully load their data from cache, set
        # the web page's data source to 'cached'
        for config in self.__table_configs.values():
            stale_condition = config.stale_condition

            if isinstance(stale_condition, dict):
                from_args = stale_condition["from_args"]

                query = {}

                for condition, args in stale_condition["query"].items():
                    query[condition] = {}
                    for key, value in args.items():  # type: ignore
                        if value in from_args:
                            value = query_args[value]  # type: ignore

                        query[condition][key] = value

                query = AdvancedQuery(**query)

                config.table.load_from_cache(query)

            elif stale_condition is None or isinstance(stale_condition, AdvancedQuery):
                config.table.load_from_cache(stale_condition)

            elif callable(stale_condition):
                stale_condition()

            if config.table.status == "downloaded":
                all_cached = False

            elif config.table.status == "cached":
                any_cached = True

        # A check to determine whether tables should be fetched from the
        # web page for the given query based on if 'any' or 'all' of the
        # tables have been cached
        if self.query_cached_condition == "all" and all_cached:
            data_source = "cached"

        elif self.query_cached_condition == "any" and any_cached:
            for table in self.__tables:
                table.status = "cached"

            data_source = "cached"

        else:
            data_source = "downloaded"

        self.data_source = data_source

    def extract_tables(self, *, url: str) -> list[pd.DataFrame]:
        """
        Extract all tables for the html web page.
        """
        try:
            return self._extract_tables(url)
        except Exception as e:
            raise Exception(f"Error downloading data from {url}. {e}")

    def download_query(self, query_args: Optional[QueryArgs] = None):
        query_args = query_args or {}

        self.load_cached_data(query_args=query_args)

        # No reason to download if the data is already cached
        if self.data_source == "cached":
            self.logger.debug(f"--- Web page {self.name} pulled from cache.")
            return

        # get the download url from the query args
        url = (
            self.get_download_url(query_args=query_args)
            if query_args
            else self.base_download_url
        )

        self.download_lock.acquire()

        try:
            tables = self.extract_tables(url=url)
        finally:
            self.download_lock.reset()

        # find the table matching the identification function. Error if not found
        for config in self.__table_configs.values():
            # TODO: Fix the order of how the datasource is set so that this makes
            # more sense. Maybe make it a boolean saying whether or not the
            # data in the data manager is from cache or not
            if config.table.status == "downloaded":
                data = config.identifier(tables)

                if data is None:
                    # TODO: Temporary solution that shouldn't have to be set here
                    # config["table"].data_source = "cached"
                    self.logger.debug(f"--- {config.table.name}: Not found.")
                    continue

                config.table.preprocess(data, additional_fields=query_args)

                self.logger.debug(f"-> {config.table.name}: Downloaded.")

            else:
                self.logger.debug(f"-> {config.table.name}: Pulled from cache.")

        return tables

    def clear_cache(self) -> None:
        """
        Clear all staged changes for the tables.
        """
        for table in self.__tables:
            table.data.reset()
            table.data.unstage()

    def is_cached(self):
        return self.data_source == "cached"

    def save_page(self) -> None:
        """
        Recursively save all savable tables on the page and any externally inherited
        pages.
        """
        for config in self.__table_configs.values():
            if config.savable() and not config.table.is_cached():
                try:
                    config.table.save()
                    self.logger.info(
                        f"-> Saved data to database for table {config.table.name}.\n"
                    )
                except StageEmpty:
                    pass

            for inheritance in config.external_inheritances(self):
                inheritance.web_page.save_page()

    def forward_pass(self, query_args: Optional[QueryArgs]):
        """
        Perform a single pass through of a dataset using specific query args and
        nesting inside nested web pages.
        """
        # Downloads the data for the specific query
        self.download_query(query_args=query_args)

        # if self.data_source
        if self.is_cached():
            pass

        else:

            # if self.nested_web_pages:
            #     self.logger.debug(
            #         f"\nNested web pages: {generate_bulleted_list(self.nested_web_pages)}\n"
            #     )

            nested_configs: list[WebTableConfig] = []

            # create a queue of table configs that have data to be saved
            queue = deque(
                [val for val in self.__table_configs.values() if val.has_staged_data()]
            )
            while queue:
                config = queue.popleft()

                config.perform_cached_inheritances()

                for inheritance in config.local_inheritances(self):
                    if not inheritance.is_ready():
                        queue.append(config)
                        continue

                # if the configuration does not have external inheritances
                if not next(config.external_inheritances(self), None):
                    config.table.data.commit()

                    if config.savable():
                        saved_data = config.table.save(persist_data=True)
                else:
                    nested_configs.append(config)

            # for table, inheritances in unsaved_configs.items():
            for config in nested_configs:
                for inheritance in config.external_inheritances(self):
                    inheritance.web_page.process(query_args=query_args)
                    data = inheritance.perform()
                    data = config.table.serializer.post_validate(data)
                    config.table.data.update(data)

                config.table.data.commit()

                if config.savable():
                    saved_data = config.table.save(persist_data=True)

            self.save_page()

            for web_page in self.nested_web_pages:
                web_page.process(query_args=query_args)

        self.clear_cache()

    def process_query(self, query: Optional[QueryArgs]):
        """
        Full process of web page by query, including a forward pass to get the data,
        resolving any inherited fields, and then saving if set to True.
        """
        self.check_configuration()

        self.logger.debug(
            f"* Query :: {generate_inline_list(query) if query else None}"
        )

        # Download web page query and process any nested web pages.
        saved_data = self.forward_pass(query_args=query)

    def process(self, _query_set: Optional[list[QueryArgs]] = None, **kwargs):
        """
        Process an entire web page by iterating through its query set and
        performing a single pass, resolving inheritances, and then saving
        all data (including nested dataset functionality).
        """
        # TODO Fix how query sets are provided
        if not _query_set:
            query_set = self._default_query_set or [None]
        else:
            query_set = _query_set

        self.logger.debug(
            f"Scanning web page `{self.name}` for {len(query_set)} queries."
        )

        idx, n = 0, len(query_set)
        for query in query_set:
            # if self.RUNNING == False:
            #     break
            self.logger.debug(
                f"\n---------------------------------------------------------\n"
            )

            self.process_query(query)
            idx += 1

            self.logger.debug(f"\n...{round(idx/n * 100, 2)}% ({self.name})")

            self.logger.debug(
                f"\n---------------------------------------------------------\n"
            )


class NestedWebPage(BaseWebPage):

    def __init__(
        self,
        query: str,
        query_set_provider: Callable[["BaseWebPage"], list[dict[str, str]]],
        *,
        name: str,
        log_level: int = logging.INFO,
        query_cached_condition: Literal["all", "any"] = "any",
        source_page: Optional[BaseWebPage] = None,
        **kwargs: Unpack[WebPageKwargs],
    ):
        if source_page:
            # Create the base url from the sources base url and the sub url
            parent_endpoint = source_page._base_download_url.strip("/")
            base_download_url = "/".join([parent_endpoint, query])
        else:
            base_download_url = query

        self.__source_page = source_page
        self.query_set_provider = query_set_provider

        super().__init__(
            name=name,
            base_download_url=base_download_url,
            log_level=log_level,
            query_cached_condition=query_cached_condition,
            **kwargs,
        )

        # self.download_lock = source_page.download_lock

    @property
    def source_page(self) -> BaseWebPage:
        if self.__source_page is None:
            raise Exception(
                "Nested web pages must be binded to a source page before configuring."
            )

        return self.__source_page

    def bind(self, web_page: BaseWebPage):
        self.__source_page = web_page

    def configure(self) -> None:
        parent_endpoint = self.source_page._base_download_url.strip("/")
        self.base_download_url = "/".join([parent_endpoint, self.base_download_url])

        self.download_lock = self.source_page.download_lock

        return super().configure()

    def process(self, *, query_args: Optional[QueryArgs]):
        self.check_configuration()

        query_set = self.query_set_provider(self.source_page)

        for query in query_set:
            query.update(query_args or {})

        # TODO: this shouldn't be done here but will protect us against some
        # 429 errors
        super().process(query_set)
