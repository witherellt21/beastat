import time

import numpy as np
import pandas as pd


from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from global_implementations import constants
from helpers.dataset_helpers import augment_dataframe
from helpers.dataset_helpers import filter_dataframe
from helpers.http_helpers import format_pandas_http_request
from urllib.error import HTTPError

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


class AbstractBaseScraper(ABC, threading.Thread):

    _DEFAULT_ERROR_MSG: str = "There was an error."
    _exception_msgs: "dict[str: str]" = {
        "load_data": _DEFAULT_ERROR_MSG,
        "download_data": _DEFAULT_ERROR_MSG,
    }

    COLUMN_TYPES: "dict[str: str]" = {}
    DATETIME_COLUMNS: "dict[str: str]" = {}
    STAT_AUGMENTATIONS: "dict[str: str]" = {}
    FILTERS: "list[Callable]" = []
    RENAME_COLUMNS: "dict[str:str]" = {}
    TABLE: BaseTable = None
    DROP_COLUMNS: "list[str]" = []
    TRANSFORMATIONS: "dict[str: Callable]" = {}
    DATA_TRANSFORMATIONS: "list[Callable]" = []
    DEFAULT_IDENTIFIERS: "list[str]" = []
    SAVE_IDENTIFIER_AS: str = None

    REFRESH_RATE: int = 5
    LOG_LEVEL = logging.INFO

    def __init__(self):
        if not self.__class__.TABLE:
            raise Exception("Must specify a table for the scaper to save data to.")

        # self.player_id: str = player_id
        # self.player_initial: str = player_id[0]

        threading.Thread.__init__(self, name=self.__class__.__name__)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.__class__.LOG_LEVEL)
        self.logger.addHandler(STREAM_HANDLER)

        self.RUNNING = False
        self.idenifier = None
        # self.url_args = []

        args_expected = self.download_url.count("{}")
        if args_expected:
            self.identifier_required = True
        else:
            self.identifier_required = False

        if self.identifier_required and not self.get_identifiers():
            raise NotImplementedError(
                "Please specify either a DEFAULT_IDENTIFIERS class attribute or override "
                "the get_identifiers() method for dynamic identifiers."
            )

    @property
    @abstractmethod
    def download_url(self) -> str:
        raise NotImplementedError("Must override the abstract property 'download_url'.")

    @abstractmethod
    def select_dataset_from_html_tables(
        self, *, datasets: "list[pd.DataFrame]"
    ) -> pd.DataFrame:
        """
        Operation to perform after fetching tables from html to get the desired dataset.
        """
        raise NotImplementedError(
            "Must override the abstract method 'select_dataset_from_html_tables'."
        )

    @abstractmethod
    def format_url_args(self, *, identifier: str) -> "list[str]":
        raise NotImplementedError(
            "Must override the abstract method 'format_url_args'."
        )

    def get_download_url(self, *, url_args: list = []) -> str:
        try:
            return self.download_url.format(*url_args)

        except IndexError:
            raise Exception(
                (
                    "Not enough arguments to populate url. Make sure your download url has an equal number "
                    "of format placeholders '{{}}' as the length of your list return from 'format_url_args'."
                )
            )

    # @abstractmethod
    # def get_identifiers(self):
    #     pass
    @property
    def default_identifiers(self) -> "dict[str: list]":
        return self.__class__.DEFAULT_IDENTIFIERS

    @property
    def save_identifier_as(self) -> str:
        return self.__class__.SAVE_IDENTIFIER_AS

    @property
    def refresh_rate(self) -> int:
        return self.__class__.REFRESH_RATE

    def get_identifiers(self) -> "dict[str: list]":
        return self.default_identifiers

    @property
    def table(self) -> BaseTable:
        return self.__class__.TABLE

    def run(self) -> None:
        consecutive_errors = 0

        self.RUNNING = True
        while self.RUNNING:
            try:
                identifiers = self.get_identifiers()

                if identifiers:
                    for identifier in self.get_identifiers():
                        self.get_data(identifier=identifier)
                        time.sleep(0.1)
                else:
                    self.get_data()
                    time.sleep(0.1)

                consecutive_errors = 0

            except Exception as e:
                consecutive_errors += 1
                self.logger.error(
                    f"Error occured in running thread for {self.__class__.__name__} ({consecutive_errors} in a row): \n\n {traceback.format_exc()}.\n\n"
                )
                if consecutive_errors >= 10:
                    self.kill_process()

    def kill_process(self, *args):
        self.RUNNING = False
        self.logger.critical(f"PROCESS KILLED FOR {self.__class__.__name__}.")

    def generate_exception_msg(self, *, exception_type: str) -> str:
        return f"{self.__class__._exception_msgs.get(exception_type, self.__class__._DEFAULT_ERROR_MSG)} {{ id = {self.player_id} }}"

    def get_data(self, *, identifier: str = None) -> None:
        url_args: "list[str]" = (
            self.format_url_args(identifier=identifier) if identifier else []
        )

        # Download the data
        data = self.download_data(url_args=url_args)
        time.sleep(self.refresh_rate)

        if data.empty:
            return

        # Remove any weird data that shouldn't be there
        data: pd.DataFrame = self.clean(data=data)

        # Add the identifier to the data if set:
        if self.save_identifier_as:
            data[self.save_identifier_as] = identifier

        # Configure the data
        data = self.configure_data(data=data)

        # Save the data
        self.cache_data(data=data)

        return data

    def download_data(self, *, url_args: "list[str]" = []) -> pd.DataFrame:
        """
        Download data from Html. Will retry on too many request error.
        """
        self.logger.debug("Starting to download_data.")

        try:
            url: str = self.get_download_url(url_args=url_args)
            http_response: str = format_pandas_http_request(url=url)
            datasets: list[pd.DataFrame] = pd.read_html(http_response)
            self.logger.info("Data download successful for %s", url_args)

        except HTTPError as http_error:

            if http_error.code == 429:
                self.logger.error(
                    f"{http_error}. Could not download data for {self.__class__.__name__} with args {url_args}."
                )
                time.sleep(45)

                return self.download_data(url_args=url_args)
            else:
                raise Exception(
                    self.generate_exception_msg(exception_type="download_data")
                )

        return self.select_dataset_from_html_tables(datasets=datasets)

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

        row_dicts = data.to_dict(orient="records")
        for row in row_dicts:
            self.table.update_or_insert_record(data=row)

        self.data = data

    def configure_data(self, *, data: pd.DataFrame) -> pd.DataFrame:
        """
        Manipulate the dataset column types, add columns, slice columns.

        **Override this for anything you want to be done to the dataset AFTER saving.
        """
        self.logger.debug("Configuring data.")

        # Rename columns to desired names
        data: pd.DataFrame = data.rename(columns=self.__class__.RENAME_COLUMNS)

        # Drop unwanted columns
        data: pd.DataFrame = data.drop(columns=self.__class__.DROP_COLUMNS)

        # Apply all transformations to the dataset
        for column, transformation in self.__class__.TRANSFORMATIONS.items():
            data[column] = data[column].apply(transformation)

        for transformation_function in self.__class__.DATA_TRANSFORMATIONS:
            data = transformation_function(dataset=data)

        # Convert the columns to the desired types
        data: pd.DataFrame = data.astype(self.__class__.COLUMN_TYPES)

        # Convert datetime columns appropriately
        for key, dt_format in self.__class__.DATETIME_COLUMNS.items():
            data[key] = pd.to_datetime(data[key], format=dt_format)

        # Add additional columns to augment the dataset and clean the unnecessary ones out
        data: pd.DataFrame = augment_dataframe(
            dataframe=data, augmentations=self.__class__.STAT_AUGMENTATIONS
        )

        # Apply any filters to the dataset
        data: pd.DataFrame = filter_dataframe(
            dataframe=data, filters=self.__class__.FILTERS
        )

        return data
