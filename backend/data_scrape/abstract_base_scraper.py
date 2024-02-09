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


class AbstractBaseScraper(ABC):

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
    TRANSFORMATIONS = {}

    def __init__(self, *, player_id: str):
        if not self.__class__.TABLE:
            raise Exception("Must specify a table for the scaper to save data to.")

        self.player_id: str = player_id
        self.player_initial: str = player_id[0]

    @property
    @abstractmethod
    def download_url(self) -> str:
        pass

    @abstractmethod
    def select_dataset_from_html_tables(
        self, *, datasets: "list[pd.DataFrame]"
    ) -> pd.DataFrame:
        """
        Operation to perform after fetching tables from html to get the desired dataset.
        """
        pass

    @property
    def table(self) -> BaseTable:
        return self.__class__.TABLE

    def generate_exception_msg(self, *, exception_type: str) -> str:
        return f"{self.__class__._exception_msgs.get(exception_type, self.__class__._DEFAULT_ERROR_MSG)} {{ id = {self.player_id} }}"

    def get_data(self) -> None:
        # Download the data
        data = self.download_data()
        time.sleep(5)

        if data.empty:
            return

        # Remove any weird data that shouldn't be there
        data: pd.DataFrame = self.clean(data=data)

        # Configure the data
        data = self.configure_data(data=data)

        # Save the data
        self.cache_data(data=data)

        return data

    def download_data(self):
        """
        Download data from Html. Will retry on too many request error.
        """
        try:
            http_response: str = format_pandas_http_request(url=self.download_url)
            datasets: list[pd.DataFrame] = pd.read_html(http_response)
            print(f"Data downloaded from: {http_response}")

        except HTTPError as http_error:

            if http_error.code == 429:
                print(f"{http_error}. Could not download data for {self.player_id}.")
                time.sleep(45)

                return self.download_data()
            else:
                raise Exception(
                    self.generate_exception_msg(exception_type="download_data")
                )

        return self.select_dataset_from_html_tables(datasets=datasets)

    def clean(self, *, data: pd.DataFrame) -> pd.DataFrame:
        """
        Change data values to interpretable values.
        """
        return data.replace(constants.NAN_VALUES, np.nan, regex=True)

    def cache_data(self, *, data: pd.DataFrame) -> None:
        """
        Save the dataset to the database.
        """
        row_dicts = data.to_dict(orient="records")
        for row in row_dicts:
            self.table.update_or_insert_record(data=row)

        self.data = data

    def configure_data(self, *, data: pd.DataFrame) -> pd.DataFrame:
        """
        Manipulate the dataset column types, add columns, slice columns.

        **Override this for anything you want to be done to the dataset AFTER saving.
        """
        # Rename columns to desired names
        data: pd.DataFrame = data.rename(columns=self.__class__.RENAME_COLUMNS)

        # Drop unwanted columns
        data: pd.DataFrame = data.drop(columns=self.__class__.DROP_COLUMNS)

        # Apply all transformations to the dataset
        for column, transformation in self.__class__.TRANSFORMATIONS.items():
            data[column] = data[column].apply(transformation)

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
