import logging
import sys
import time
from datetime import datetime
from typing import Any, Callable, Literal, NotRequired, Optional, Union, Unpack

import pandas as pd
from fastapi import dependencies
from lib.dependency_trees import (
    DependencyKwargs,
    DependentObject,
    topological_sort_dependency_tree,
)
from lib.pydantic_validator import PydanticValidatorMixin
from lib.util import combine_lists_of_dicts
from scrapp.core.exceptions import StageEmpty
from scrapp.scraper.html_table.data_state_manager import DataStateManager
from scrapp.tables.base_table import AdvancedQuery
from scrapp.utils.string_formatting import generate_bulleted_list, generate_inline_list
from typing_extensions import TypedDict

from .configurable import Configurable
from .html_table import DataframeController
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
    html_tables: NotRequired[Optional[dict[str, "TableConfig"]]]
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


class TableInheritance(TypedDict):
    source: DataframeController
    fields: list[str]


class TableConfig(TypedDict):
    table: DataframeController
    identifier: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]]
    stale_condition: Callable[[], bool] | AdvancedQuery | CachedQueryConfig | None
    inheritances: list[TableInheritance]
    dependencies: list[TableInheritance]


class NestedWebPage(TypedDict):
    web_page: "BaseWebPage"
    query_set_provider: Callable[["BaseWebPage"], list[dict[str, str]]]


def href_table_extractor(url: str) -> list[pd.DataFrame]:
    """
    Base extractor that extracts links from the html
    """
    tables = pd.read_html(url, extract_links="body")

    for df in tables:
        for column in df.columns:

            # the columns are multi-indexed, append the _link identifier to the end
            # of the last value
            if isinstance(df.columns, pd.MultiIndex):
                link_column = (*column[:-1], f"{column[-1]}_link")

            # the column is singly-indexed
            else:
                link_column = f"{column}_link"

            column_split = df[column].apply(pd.Series)

            if len(column_split.columns) != 2:
                column_split[[1]] = pd.NA

            df[[column, link_column]] = column_split

            if df[link_column].isna().all():
                df.drop(link_column, axis=1, inplace=True)

    return tables


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
        self.__table_configs: dict[str, TableConfig] = kwargs.get("html_tables") or {}
        self.__tables: list[DataframeController] = [
            config["table"] for config in self.__table_configs.values()
        ]
        self.query_cached_condition = query_cached_condition

        self._default_query_set: Optional[QuerySet] = (
            kwargs.get("default_query_set") or []
        )
        self._extract_tables = kwargs.get("extract_tables", href_table_extractor)
        self.__download_rate = download_rate
        self.__last_download_time = time.time()

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
    def table_configs(self) -> dict[str, TableConfig]:
        """
        Public getter function for the _html_tables.
        """
        return self.__table_configs

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

                dependency_data = dependency.source.__table_configs[
                    dependency.meta.table_name
                ]["table"].data.stage

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

    # def set_logger(self, logger: logging.Logger):
    #     self.logger = logger
    def bind_scraper(self, scraper):
        self.scraper = scraper

        self.logger = scraper.logger

    @property
    def download_rate(self):
        return self.__download_rate

    @download_rate.setter
    def download_rate(self, value: int):
        self.__download_rate = value

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
        inheritances: list[TableInheritance] = [],
        dependencies: list[TableInheritance] = [],
    ) -> None:
        """
        Add a table to download from the web page.
        """
        # self.__table_configs[table.name] = {
        #     "table": table,
        #     "identification_function": identification_function,
        # }
        self.__table_configs[table.name] = {
            "table": table,
            "identifier": identification_function,
            "stale_condition": stale_condition,
            "inheritances": inheritances,
            "dependencies": dependencies,
        }

        self.__tables.append(table)

    def add_inheritance(
        self,
        table: str | DataframeController,
        source: DataStateManager,
        fields: list[str],
    ):
        if isinstance(table, DataframeController):
            table.add_inheritance(source, fields)
        else:
            self.__table_configs[table]["table"].add_inheritance(source, fields)

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
        *,
        web_page: "BaseWebPage",
        query_set_provider: Callable[["BaseWebPage"], list[dict[str, str]]],
        # dependencies: list[]
    ) -> None:
        """
        Add a nested web page to the current web page.
        """
        # parent_endpoint = self._base_download_url.rsplit(".", 1)[0]
        parent_endpoint = self._base_download_url

        if not web_page.base_download_url.startswith(parent_endpoint):
            web_page.base_download_url = parent_endpoint + web_page.base_download_url

        nested_page: NestedWebPage = {
            "web_page": web_page,
            "query_set_provider": query_set_provider,
        }

        self.nested_web_pages.append(nested_page)

    # def add_nested_web_page(self, name: str, url_extension: str, **kwargs) -> None:
    #     """
    #     Nested web pages get processed in a depth first way such that each query of the
    #     parent web page triggers the entire query set of its nested web page.
    #     """
    #     url = self._base_download_url.rsplit(".", 1)[0] + url_extension

    #     new_page = BaseWebPage(name=name, base_download_url=url, **kwargs)

    #     self.nested_web_pages.append(new_page)

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

        # self._configured = True
        # for table in self.__tables:
        #     # print(table.inheritances)
        #     print(table.name)
        #     for inheritance in table.inheritances:
        #         print(inheritance)
        for table in self.__tables:
            # print(config["inheritances"])
            # print(config)
            print(table.inheritances)

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
        for table in self.__table_configs.values():
            stale_condition = table["stale_condition"]

            if isinstance(stale_condition, dict):
                from_args = stale_condition["from_args"]

                for args in stale_condition["query"].values():
                    for key in args:  # type: ignore
                        if key in from_args:
                            args[key] = query_args[key]  # type: ignore

                query = AdvancedQuery(**stale_condition["query"])

                table["table"].load_from_cache(query)

            elif stale_condition is None or isinstance(stale_condition, AdvancedQuery):
                table["table"].load_from_cache(stale_condition)

            elif callable(stale_condition):
                stale_condition()

            if table["table"].status == "downloaded":
                all_cached = False

            elif table["table"].status == "cached":
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

    def acquire_download_lock(self):
        if self.__last_download_time:
            wait = max(
                self.__last_download_time - time.time() + self.__download_rate, 0
            )
        else:
            wait = 0

        if wait:
            time.sleep(wait)

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

        self.acquire_download_lock()

        try:
            tables = self.extract_tables(url=url)
        finally:
            self.__last_download_time = time.time()

        # find the table matching the identification function. Error if not found
        for config in self.__table_configs.values():
            # TODO: Fix the order of how the datasource is set so that this makes
            # more sense. Maybe make it a boolean saying whether or not the
            # data in the data manager is from cache or not
            if config["table"].status == "downloaded":
                data = config["identifier"](tables)

                if data is None:
                    # TODO: Temporary solution that shouldn't have to be set here
                    # config["table"].data_source = "cached"
                    self.logger.debug(f"-> {config['table'].name}: Not found.")
                    continue

                config["table"].preprocess(data, additional_fields=query_args)

                self.logger.debug(f"--- {config['table'].name}: Downloaded.")

            else:
                self.logger.debug(f"--- {config['table'].name}: Pulled from cache.")

        return tables

    def save(self) -> None:
        """
        Save the data for the web page and any nested web pages.
        """
        # self.logger.info(f"\n-> Saving data to database for web page {self.name}.\n")

        # Use staging if there is backed up data that needs to be saved that was
        # waiting for a dependency
        self.logger.info("\n")
        for config in self.__table_configs.values():
            if config["table"].status != "cached":
                # TODO: We should find another way to handle this
                try:
                    config["table"].data.commit()
                    config["table"].data.push()
                    self.logger.info(
                        f"-> Saved data to database for table {config['table'].name}.\n"
                    )
                except StageEmpty:
                    pass

        # recurse into nested datatsets
        # for nested_web_page in self.nested_web_pages:
        #     nested_web_page.save()

    def clear_cache(self) -> None:
        for table in self.__tables:
            table.data.reset()

    def ready_for_save(self, table: TableConfig) -> bool:
        for inheritance in table["inheritances"]:
            if inheritance["source"] not in self.__tables:
                return False

        for dependency in table["dependencies"]:
            if dependency["source"].status != "cached":
                return False

        return True

    def forward_pass(self, query_args: Optional[QueryArgs]):
        """
        Perform a single pass through of a dataset using specific query args and
        nesting inside nested web pages.
        """
        # Downloads the data for the specific query
        self.download_query(query_args=query_args)

        if self.nested_web_pages:
            self.logger.debug(
                f"\nNested web pages: {generate_bulleted_list(self.nested_web_pages)}\n"
            )

        unsaved_tables: list[TableConfig] = []
        for config in self.__table_configs.values():
            config["table"].attempt_save()

            if config["table"].status != "cached":
                unsaved_tables.append(config)

        # Processes each nested web page, which depend on the current web page.
        for nested_web_page in self.nested_web_pages:
            query_set = nested_web_page["query_set_provider"](self)

            if query_args:
                for query in query_set:
                    query.update(query_args)

            # TODO: this shouldn't be done here but will protect us against some
            # 429 errors
            self.acquire_download_lock()
            nested_web_page["web_page"].process(query_set)

        return unsaved_tables

    def resolve_inheritances(self, *, set_data_source: bool = True) -> Optional[bool]:
        """
        Backwards resolve any inherited fields after all dependencies have been exhausted.
        Specify confirm_update as True to return a boolean designating where there was any
        update performed on the dataset configuration.
        """
        for config in self.__table_configs.values():
            # if set_data_source:
            #     data = config["table"].data.copy()

            config["table"].postprocess()

            # print(config["table"].data)
            # print(data)
            # if set_data_source:
            #     if not data.equals(config["table"].data.copy()):
            #         self.data_source = "downloaded"
            #         config["table"].data_source = "downloaded"

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
        table_configs = self.forward_pass(query_args=query)

        # Pull any data from nested page tables
        unsaved_tables = []
        for config in table_configs:
            config["table"].attempt_save(raise_exception=True)

            if config["table"].status != "cached":
                unsaved_tables.append(config)

        self.clear_cache()

        # if not self.data_source == "cached":
        #     self.save()
        # else:
        #     self.clear_cache()

        # self.logger.debug(
        #     f"{self.name}: Ready for save = {ready_for_save} : Is already saved = {self.data_source == 'cached'}"
        # )

        # If web page has dependecies but they have not been downloaded yet
        # stage the changes for that table.
        # if self.dependencies and not ready_for_save:
        #     for table in self.__html_tables.values():
        #         table["table"].data.stage_changes()

        # # If the web page's data is not already saved,
        # # save the web page.
        # elif self.data_source != "cached":
        #     self.save()

        # # There is not data to save for the web page so don't do anything
        # else:
        #     self.logger.info(f"No new data to save for dataset: {self.name}.")

    def process(self, _query_set: Optional[list[QueryArgs]] = None):
        """
        Process an entire web page by iterating through its query set and
        performing a single pass, resolving inheritances, and then saving
        all data (including nested dataset functionality).
        """
        # ready_for_save: bool = all(
        #     [
        #         dependency.source.data_source == "cached"
        #         for dependency in self.dependencies
        #     ]
        # )

        # If we don't
        # if self.query_set is None and self.static:
        #     queries = [None]
        # elif self.query_set:
        #     queries = self.query_set

        # if self.static:
        #     query_set = [None]

        # elif self.dependencies:
        #     query_set_extractions = []

        #     for dependency in self.dependencies:
        #         # source_table = dependency.source
        #         # TODO: verify these links are accurate in configure
        #         dependency.source.process()

        #         # dependency_data = dependency.source.__table_configs[
        #         #     dependency.meta.table_name
        #         # ]["table"].data.stage
        #         # query_args = dependency.source
        #         # query_args = dependency.source.table_configs.
        #         source_table = next(
        #             (
        #                 n["table"].data
        #                 for n in dependency.source.table_configs
        #                 if n["table"].name == dependency.meta.table_name
        #             )
        #         )

        #         # query_args = dependency.meta.
        #         if source_table.stage.empty:

        #             raise Exception(
        #                 f"Dataset {self.name} processed before dependency {dependency.source.name}."
        #             )

        #         else:
        #             query_set_extractions.append(
        #                 dependency.meta.query_set_provider(source_table.stage)
        #             )

        #     query_set = combine_lists_of_dicts(*query_set_extractions)

        # elif self._default_query_set:
        #     query_set = self._default_query_set

        # else:
        # raise Exception(
        #     "Must specify a default query set if no dependencies are provided."
        # )
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


class HTMLTableConfig:
    # The controller that cleans and saves the input table.
    controller: DataframeController

    # The identifier function that will identify the desired table.
    identifier: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]]

    stale_condition: Callable[[], bool] | AdvancedQuery | CachedQueryConfig | None

    # A list of inheritances that describe where external data should come from to complete the table.
    inheritances: list[TableInheritance]

    # A list of dependencies that need to be saved before the desired table can be saved.
    dependencies: list[TableInheritance]
