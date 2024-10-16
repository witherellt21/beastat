import logging
import time
import traceback
from typing import Literal, NotRequired, Optional, Union, Unpack

from lib.dependency_trees import topological_sort_dependency_tree
from typing_extensions import TypedDict

from .util import QueryArgs, QuerySet, Thread
from .web_page import BaseWebPage

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

    def acquire_download_lock(self):
        if self.last_download_time:
            wait = max(self.last_download_time - time.time() + self.download_rate, 0)
        else:
            wait = 0

        if wait:
            time.sleep(wait)

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

    def download_web_page_query(
        self, *, web_page: BaseWebPage, query_args: Optional[QueryArgs] = None
    ) -> None:
        # if this specific query is already save in the database, fetch that instead
        web_page.load_cached_data(query_args=query_args)
        if all(
            [
                table_config.data_source == "cached"
                for table_config in web_page._html_tables.values()
            ]
        ):
            web_page.data_source = "cached"

        else:
            # get the download url from the query args
            url = (
                web_page.get_download_url(query_args=query_args)
                if query_args
                else web_page.base_download_url
            )

            self.acquire_download_lock()

            try:
                tables = web_page.extract_tables(url=url)
            except Exception as e:
                raise e
            finally:
                self.last_download_time = time.time()

            # find the table matching the identification function. Error if not found
            for table_name, table in web_page._html_tables.items():
                data = table.identify(tables=tables)

                if data is None:
                    self.logger.debug(f"-> {table_name}: Not found.")
                    continue

                # Add any of the query arguments to the dataframe if desired.
                for (
                    df_column,
                    query_key,
                ) in table.serializer.query_arg_fields.items():
                    if query_args and query_key in query_args:
                        data[df_column] = query_args[query_key]

                # Apply each cleaning function
                try:
                    data = table.clean(data=data)
                    table.add_data(data)

                    self.logger.info(f"-> {table.name}: Downloaded.")
                except Exception as e:
                    raise Exception(f"{table.name}: {traceback.format_exc()}")

    def save_web_page(self, web_page: BaseWebPage) -> None:
        """
        Save the data for the dataset and any nested web pages.
        """
        self.logger.info(f"Saving data to database for web page {web_page.name}.")

        # Use staging if there is backed up data that needs to be saved that was
        # waiting for a dependency
        for table in web_page._html_tables.values():
            if table.data_source != "cached":
                table.push()

        # recurse into nested datatsets
        for nested_web_page in web_page.nested_web_pages:
            self.save_web_page(web_page=nested_web_page)

    def forward_pass(self, web_page: BaseWebPage, query_args: Optional[QueryArgs]):
        """
        Perform a single pass through of a dataset using specific query args and
        nesting inside nested web pages.
        """
        # Downloads the data for the specific query
        self.download_web_page_query(web_page=web_page, query_args=query_args)

        if web_page.nested_web_pages:
            self.logger.debug(
                f"\nNested web pages: {format_dict_as_list(web_page.nested_web_pages)}\n"
            )

        # Processes each nested web page, which depend on the current web page.
        for nested_web_page in web_page.nested_web_pages:
            self.process_web_page(
                web_page=nested_web_page, query_set=nested_web_page.query_set
            )

    def resolve_inheritances(
        self, *, web_page: BaseWebPage, set_data_source: bool = True
    ) -> Optional[bool]:
        """
        Backwards resolve any inherited fields after all dependencies have been exhausted.
        Specify confirm_update as True to return a boolean designating where there was any
        update performed on the dataset configuration.
        """
        for table in web_page._html_tables.values():
            if set_data_source:
                data = table.data.copy()

            for inheritance in table.inheritances:
                if not inheritance.source.data.empty:
                    inherited_data = inheritance.inheritance_function(
                        inheritance.source.data
                    )

                    table.data.update(inherited_data)

                else:
                    raise Exception(
                        f"Inherited data source was empty for {table} retrieving data from {inheritance.source}."
                    )

            if set_data_source:
                if not data.equals(table.data):
                    web_page.data_source = "downloaded"
                    table.data_source = "downloaded"

    def process_web_page_query(
        self, web_page: BaseWebPage, query: Optional[QueryArgs], ready_for_save: bool
    ):
        """
        Full process of web page by query, including a forward pass to get the data,
        resolving any inherited fields, and then saving if set to True.
        """
        self.logger.debug(
            f"***\nQuery :: {format_dict_as_list_inline(query) if query else None}"
        )

        # Download web page query and process any nested web pages.
        self.forward_pass(web_page=web_page, query_args=query)

        self.resolve_inheritances(web_page=web_page, set_data_source=True)

        self.logger.debug(
            f"{web_page.name}: Ready for save = {ready_for_save} : Is already saved = {web_page.data_source == 'cached'}"
        )

        # If web page has dependecies but they have not been downloaded yet
        # stage the changes for that table.
        if web_page.dependencies and not ready_for_save:
            for table in web_page._html_tables.values():
                table.stage_changes()

        # If the web page's data is not already saved,
        # save the web page.
        elif web_page.data_source != "cached":
            self.save_web_page(web_page=web_page)

        # There is not data to save for the web page so don't do anything
        else:
            self.logger.info(f"No new data to save for dataset: {web_page.name}.")

    def process_web_page(self, web_page: BaseWebPage, query_set: Optional[QuerySet]):
        """
        Process an entire web page by iterating through its query set and
        performing a single pass, resolving inheritances, and then saving
        all data (including nested dataset functionality).
        """
        ready_for_save: bool = all(
            [
                dependency.source.data_source == "cached"
                for dependency in web_page.dependencies
            ]
        )

        if query_set is None and web_page.static:
            queries = [None]
        elif query_set:
            queries = query_set
        else:
            raise Exception("Unknown exception at process_web_page()")

        idx, n = 0, len(queries)

        self.logger.debug(
            f"\nScanning web page `{web_page.name}` for {len(queries)} queries.\n"
        )
        for query in queries:
            if self.RUNNING == False:
                break

            self.process_web_page_query(web_page, query, ready_for_save)

            idx += 1
            self.logger.debug(
                f"{web_page.name} query set {round(idx/n * 100, 2)}% complete."
            )

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

            self.process_web_page(web_page, query_set=web_page.query_set)

    def run(self):

        if not self.is_configured:
            raise Exception(
                "Must call '.configure()' on the scraper before running it."
            )

        super().run()
