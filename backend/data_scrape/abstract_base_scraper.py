import time
from typing import Optional
from typing import TypedDict
from typing import Unpack
from typing import Type
from typing import Any


import numpy as np
import pandas as pd
from pandas._typing import Dtype

from abc import ABC
from abc import abstractmethod, abstractproperty
from collections.abc import Callable
from global_implementations import constants
from helpers.dataset_helpers import augment_dataframe
from helpers.dataset_helpers import filter_dataframe
from helpers.dataset_helpers import reorder_columns
from helpers.http_helpers import format_pandas_http_request
from urllib.error import HTTPError
from pydantic.fields import FieldInfo

from sql_app.register.base import BaseTable
import threading
import traceback
import logging

# DEFAULT_LOG_FORMATTER = logging.Formatter(
#     "[ %(levelname)s ] [ %(asctime)s ] [ %(threadName)s ]  %(message)s",
#     "%Y-%m-%d %H:%M:%S",
# )

DEFAULT_LOG_FORMATTER = logging.Formatter(
    "[{levelname:^10}] [ {asctime} ] [{threadName:^20}]  {message}",
    "%I:%M:%S %p",
    style="{",
)

STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(DEFAULT_LOG_FORMATTER)


def get_column_types_for_table(
    *, table: BaseTable, ignore_columns: list[str]
) -> dict[str, Dtype]:
    table_columns: dict[str, FieldInfo] = (
        table.table_entry_serializer_class.model_fields
    )
    table_types: dict[str, Any] = {k: v.annotation for k, v in table_columns.items()}

    column_types: dict[str, Dtype] = {}
    for column, dtype in table_types.items():
        if column in ignore_columns:
            continue
        else:
            union_args: Optional[list[Type]] = getattr(dtype, "__args__", None)
            column_types[column] = union_args[0] if union_args else dtype

    return column_types


class ScraperKwargs(TypedDict, total=False):
    table: BaseTable
    column_types: dict[str, Dtype]
    datetime_columns: dict[str, str]
    query_save_columns: dict[str, str] | list[str]
    refresh_rate: int


class AbstractBaseScraper(ABC, threading.Thread):
    """
    Required class attributes:
    - TABLE (can also be passed as init parameter 'table')

    Optional class attributes:
    - COLUMN_TYPES: overrides types derived from table
    - DATETIME_COLUMNS: overrides datetime columns derived from table
    - DESIRED_COLUMNS: "list[str]" = [] => overrides columns derived from table
    - STAT_AUGMENTATIONS: "dict[str: str]" = {}
    - TRANSFORMATIONS: "dict[str: Callable]" = {}
    - DATA_TRANSFORMATIONS: "list[Callable]" = []
    - QUERY_SAVE_COLUMNS: dict[str, str] | list[str] -> save query parameter 'value' to the dataset in column 'key'
    - REFRESH_RATE: int = 5
    - LOG_LEVEL = logging.INFO
    """

    _DEFAULT_ERROR_MSG: str = "There was an error."
    _exception_msgs: "dict[str, str]" = {
        "load_data": _DEFAULT_ERROR_MSG,
        "download_data": _DEFAULT_ERROR_MSG,
    }

    # This could maybe come from the table itself, then overriden by this
    COLUMN_TYPES: Optional[dict[str, Dtype]] = None
    DATETIME_COLUMNS: dict[str, str] = {}

    # Adds column labled by key using a synctatic string or a callable function with argument that accepts the full dataset.
    STAT_AUGMENTATIONS: dict[str, str | Callable[[pd.DataFrame], pd.Series]] = {}

    # Select specific rows from the dataset based on callable filter functions
    FILTERS: list[Callable] = []
    RENAME_COLUMNS: dict[str, str] = {}

    # Rename values by key to the specified value
    RENAME_VALUES = {}

    TABLE: Optional[BaseTable] = None

    # A function to tranform a specific column (key) on a dataset by a callable function (value) uses apply method
    TRANSFORMATIONS: dict[str | tuple[str, str], Callable[[Any], Any]] = {}
    DATA_TRANSFORMATIONS: list[Callable] = []

    QUERY_SAVE_COLUMNS: dict[str, str] | list[str] = []

    COLUMN_ORDERING: list[str] = []

    REFRESH_RATE: int = 5
    LOG_LEVEL = logging.INFO

    def __init__(self, **kwargs: Unpack[ScraperKwargs]):
        threading.Thread.__init__(self, name=self.__class__.__name__)
        self.RUNNING = False

        # If kwargs are passed containing information for these, override the class attribute.
        table: Optional[BaseTable] = kwargs.get("table", self.__class__.TABLE)

        if table == None:
            raise Exception(
                "Must specify a table for the scaper to save data to. Add the 'TABLE' class attribute or pass a table to the keyword 'table'."
            )

        self.table: BaseTable = table

        self.column_types: Optional[dict[str, Dtype]] = kwargs.get(
            "column_types", self.__class__.COLUMN_TYPES
        )
        self.datetime_columns: dict[str, str] = kwargs.get(
            "datetime_columns", self.__class__.DATETIME_COLUMNS
        )
        self.refresh_rate: int = kwargs.get("refresh_rate", self.__class__.REFRESH_RATE)

        query_save_columns: dict[str, str] | list[str] = kwargs.get(
            "query_save_columns", self.__class__.QUERY_SAVE_COLUMNS
        )

        self.query_save_columns: dict[str, str]

        if isinstance(query_save_columns, list):
            self.query_save_columns = {column: column for column in query_save_columns}
        else:
            self.query_save_columns = query_save_columns

        # If we still don't have column types, get them from the table
        if self.column_types is None:
            ignore_columns = list(self.__class__.STAT_AUGMENTATIONS.keys()) + list(
                self.__class__.DATETIME_COLUMNS.keys()
            )
            self.column_types = get_column_types_for_table(
                table=self.table,
                ignore_columns=ignore_columns,
            )

        # self.desired_columns = [
        #     key for key in table.table_entry_serializer_class.model_fields.keys()
        # ]
        self.desired_columns = list(
            table.table_entry_serializer_class.model_fields.keys()
        )

        # Configure our logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.__class__.LOG_LEVEL)
        self.logger.addHandler(STREAM_HANDLER)

        # Initialize as None to download immediately on first loop.
        self.last_download_time: Optional[float] = None

        # Get the number of arguments expected to be returned from identifiers.
        # args_expected: int = self.download_url.count("{}")
        # if args_expected:
        #     self.identifier_required = True
        # else:
        #     self.identifier_required = False

        # if self.identifier_required and not self.get_identifiers():
        #     raise NotImplementedError(
        #         "Please specify either a DEFAULT_IDENTIFIERS class attribute or override "
        #         "the get_identifiers() method for dynamic identifiers."
        #     )

    @abstractproperty
    def download_url(self) -> str:
        """
        Specify a format string as the base download url to receive keyword arguments.
        """
        raise NotImplementedError("Must override the abstract property 'download_url'.")

    @abstractmethod
    def select_dataset_from_html_tables(
        self, *, datasets: list[pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Operation to perform after fetching tables from html to get the desired dataset.
        """
        raise NotImplementedError(
            "Must override the abstract method 'select_dataset_from_html_tables'."
        )

    @abstractmethod
    def get_query_set(self) -> Optional[list[dict[str, str]]]:
        """
        Function returning a list of query parameters to add insert in the base download url for scraping.
        """
        raise NotImplementedError("Must override the abstract method 'get_query_set'.")

    def get_download_url(self, *, url_kwargs: dict[str, str] = {}) -> str:
        """
        Insert the given url keyword args into the base download url.
        """
        try:
            return self.download_url.format(**url_kwargs)

        except IndexError:
            raise Exception(
                (
                    "Not enough arguments to populate url. Make sure your download url has an equal number "
                    "of format placeholders '{{}}' as the length of your list return from 'format_url_args'."
                )
            )

    def run(self) -> None:
        consecutive_errors = 0

        self.RUNNING = True
        while self.RUNNING:
            try:
                query_set = self.get_query_set()
            except Exception as e:
                self.logger.error(traceback.format_exc())
                self.kill_process()
                break

            if query_set == None:
                self.get_data()
                time.sleep(0.1)

            else:
                for query in query_set:
                    if not self.RUNNING:
                        break

                    try:
                        self.get_data(query=query)
                        time.sleep(0.1)

                        consecutive_errors = 0

                    except Exception as e:
                        consecutive_errors += 1
                        self.logger.error(
                            f"Error occured in running thread for {self.__class__.__name__} ({consecutive_errors} in a row) ({query}): \n\n {traceback.format_exc()}.\n\n"
                        )

                        if consecutive_errors >= 10:
                            self.kill_process()

                        continue

    def kill_process(self, *args):
        """
        Kill the running thread and stop the scraper.
        """
        self.RUNNING = False
        self.logger.critical(f"PROCESS KILLED FOR {self.__class__.__name__}.")

    def generate_exception_msg(self, *, exception_type: str) -> str:
        """
        Generate an exception message based on the exception type specified.
        """
        return f"{self.__class__._exception_msgs.get(exception_type, self.__class__._DEFAULT_ERROR_MSG)}"

    def get_data(self, *, query: dict[str, str] = {}) -> Optional[pd.DataFrame]:
        """
        Get data according to the search query.
        """
        self.logger.debug(f"Getting data with query: {query}.")

        if self.is_cached(query=query):
            return None

        # Download the data for the given url parameters
        downloaded_dataset: Optional[pd.DataFrame] = self.download_data(query=query)

        # If there is no data in the downloaded data, return None.
        if downloaded_dataset is None or downloaded_dataset.empty:
            return None

        # Remove any weird data that shouldn't be there
        data: pd.DataFrame = self.clean(data=downloaded_dataset)

        # Add any of the query arguments to the dataframe if desired.
        for df_column, query_key in self.query_save_columns.items():
            if query_key in query:
                data[df_column] = query.get(query_key)
            else:
                self.logger.warning(f"Key {query_key} not found in the query: {query}.")

        # Configure the data
        data = self.configure_data(data=data)

        # Save the data
        self.cache_data(data=data)

        return data

    def download_data(self, *, query: dict[str, str] = {}) -> Optional[pd.DataFrame]:
        """
        Download data from Html. Will retry on too many request error.
        """
        self.logger.debug("Starting to download_data.")

        try:
            if self.last_download_time:
                wait = max(self.last_download_time - time.time() + self.refresh_rate, 0)
            else:
                wait = 0

            if wait:
                time.sleep(wait)

            url: str = self.get_download_url(url_kwargs=query)
            http_response: str = format_pandas_http_request(url=url)
            datasets = self.scrape_data(url=http_response)
            self.last_download_time = time.time()

            if not datasets:
                return None

            self.logger.info("Data download successful for %s", query)

        except HTTPError as http_error:

            if http_error.code == 404:
                self.logger.error(
                    "There might be an error in your download_url %s", url
                )

                return None

            if http_error.code == 429:
                self.logger.error(
                    f"{http_error}. Could not download data for {self.__class__.__name__} with kwargs {query}. Trying again..."
                )
                time.sleep(45)

                return self.download_data(query=query)

            else:
                raise Exception(
                    self.generate_exception_msg(exception_type="download_data")
                )

        return self.select_dataset_from_html_tables(datasets=datasets)

    def scrape_data(self, *, url: str) -> Optional[list[pd.DataFrame]]:
        """
        Scrape data from URL to a datframe. Override this for non table based downloads.
        """
        try:
            datasets: list[pd.DataFrame] = pd.read_html(url)
        except ValueError as e:
            self.logger.warning(f"{e} at url: {url}")
            return None

        return datasets

    def clean(self, *, data: pd.DataFrame) -> pd.DataFrame:
        """
        Change data values to interpretable values.
        """
        self.logger.debug("Cleaning data.")

        return data.replace(constants.NAN_VALUES, np.nan, regex=True)

    def cache_data(self, *, data: pd.DataFrame) -> None:
        """
        Save the dataset to the database.
        """
        self.logger.debug("Saving data to database.")

        data = data.fillna(np.nan).replace([np.nan], [None])

        row_dicts = data.to_dict(orient="records")
        for row in row_dicts:
            self.table.update_or_insert_record(data=row)

        self.logger.debug(f"\n{data}")

    def is_cached(self, *, query: dict[str, str] = {}) -> bool:
        return False

    def configure_data(self, *, data: pd.DataFrame) -> pd.DataFrame:
        """
        Manipulate the dataset column types, add columns, slice columns.

        **Override this for anything you want to be done to the dataset AFTER saving.
        """
        self.logger.debug("Configuring data.")

        # Rename columns to desired names
        data = data.rename(columns=self.__class__.RENAME_COLUMNS)

        # Replace row values with desired row values
        data = data.replace(self.__class__.RENAME_VALUES)

        # Apply all transformations to the dataset
        for column, transformation in self.__class__.TRANSFORMATIONS.items():
            if type(column) == tuple:
                from_column, to_column = column
            else:
                from_column = to_column = column

            data[to_column] = data[from_column].apply(transformation)

        for transformation_function in self.__class__.DATA_TRANSFORMATIONS:
            data = transformation_function(dataset=data)

        # Convert the columns to the desired types
        if self.column_types:
            try:
                data = data.astype(self.column_types)
            except pd.errors.IntCastingNaNError:
                self.logger.debug(data["weight"].value_counts())

        # Convert datetime columns appropriately
        for key, dt_format in self.__class__.DATETIME_COLUMNS.items():
            data[key] = pd.to_datetime(data[key], format=dt_format)

        # Add additional columns to augment the dataset and clean the unnecessary ones out
        data = augment_dataframe(
            dataframe=data, augmentations=self.__class__.STAT_AUGMENTATIONS
        )

        # Apply any filters to the dataset
        data = filter_dataframe(dataframe=data, filters=self.__class__.FILTERS)

        data = reorder_columns(
            dataframe=data, column_order=self.__class__.COLUMN_ORDERING
        )

        data = data[self.desired_columns]

        return data
