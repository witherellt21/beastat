import os
import time

import numpy as np
import pandas as pd


from abc import ABC, abstractmethod
from collections.abc import Callable
from global_implementations import constants
from helpers.dataset_helpers import augment_dataframe
from helpers.dataset_helpers import filter_dataframe
from helpers.http_helpers import format_pandas_http_request
from helpers.string_helpers import construct_file_path
from urllib.error import HTTPError

class AbstractBaseDataset(ABC):

    _DEFAULT_ERROR_MSG: str = "There was an error."
    _exception_msgs: dict[str: str] = {
        "load_data": _DEFAULT_ERROR_MSG,
        "download_data": _DEFAULT_ERROR_MSG
    }

    BASE_SAVE_DIR: str = os.path.join(".", "saved_tables")
    COLUMN_TYPES: dict[str: str] = {}
    DATETIME_COLUMNS: dict[str: str] = {}
    DESIRED_COLUMNS: list[str] = []
    STAT_AUGMENTATIONS: dict[str: str] = {}
    FILTERS: list[Callable] = []
    RENAME_COLUMNS: dict[str:str] = {}

    def __init__(self, *, player_id: str):
        self.player_id: str = player_id
        self.player_initial: str = player_id[0]

        self.data: pd.DataFrame = pd.DataFrame()

    @property
    @abstractmethod
    def download_url(self) -> str:
        pass

    @property
    @abstractmethod
    def save_path(self) -> str:
        """
        The subpath to save your table in. 
        
        **All tables will be saved in a 'saved_tables' folder at project root unless the full_save_path property is overriden.
        """
        pass

    @abstractmethod
    def select_dataset_from_html_tables(self, *, datasets: list[pd.DataFrame]) -> pd.DataFrame:
        """
        Operation to perform after fetching tables from html to get the desired dataset.
        """
        pass

    @property
    def full_save_path(self) -> str:
        return os.path.join(self.__class__.BASE_SAVE_DIR, self.save_path)

    @property
    def save_file(self) -> str:
        return os.path.join(self.full_save_path, f"{self.player_id}.csv")

    def generate_exception_msg(self, *, exception_type: str) -> str:
        return f"{self.__class__._exception_msgs.get(exception_type, self.__class__._DEFAULT_ERROR_MSG)} {{ id = {self.player_id} }}"

    def get_data(self, *, pre_augment: bool = False) -> pd.DataFrame:
        if self.is_cached():
            data: pd.DataFrame = self.load_data()
        else:
            data = self.download_data()
            time.sleep(5)

            if data.empty:
                return self.data

            data: pd.DataFrame = self.clean(data=data)

            if pre_augment:
                data: pd.DataFrame = augment_dataframe(dataframe=data, augmentations=self.__class__.STAT_AUGMENTATIONS)
                
                # Apply any filters to the dataset
                data: pd.DataFrame = filter_dataframe(dataframe=data, filters=self.__class__.FILTERS)

        self.data = self.configure_data(data=data, pre_augment=pre_augment)
        
        self.cache_data(data=self.data)

        return self.data

    def load_data(self):
        try:
            data: pd.DataFrame = pd.read_csv(self.save_file)
            # print(f"Data loaded from {self.save_file}.")

        except:
            raise Exception(self.generate_exception_msg(exception_type="load_data"))

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
                raise Exception(self.generate_exception_msg(exception_type="download_data"))
            
        return self.select_dataset_from_html_tables(datasets=datasets)

    def clean(self, *, data: pd.DataFrame) -> pd.DataFrame:
        """
        Change data values to interpretable values.
        """
        return data.replace(constants.NAN_VALUES, np.nan, regex=True)
        
    def is_cached(self):
        """
        Check if the dataset is already saved in the save path.
        """
        return os.path.exists(self.save_file)

    def cache_data(self, *, data: pd.DataFrame) -> None:
        """
        Save the dataset to the save path.
        """
        if not os.path.exists(self.full_save_path):
            construct_file_path(self.full_save_path)

        data.to_csv(self.save_file)

    def configure_data(self, *, data: pd.DataFrame, pre_augment: bool = False) -> pd.DataFrame:
        """
        Manipulate the dataset column types, add columns, slice columns. 

        **Override this for anything you want to be done to the dataset AFTER saving.
        """
        # Convert the columns to the desired types
        data: pd.DataFrame = data.astype(self.__class__.COLUMN_TYPES)

        # Convert datetime columns appropriately
        for key, dt_format in self.__class__.DATETIME_COLUMNS.items():
            data[key] = pd.to_datetime(data[key], format=dt_format)

        if not pre_augment:
            # Add additional columns to augment the dataset and clean the unnecessary ones out
            data: pd.DataFrame = augment_dataframe(dataframe=data, augmentations=self.__class__.STAT_AUGMENTATIONS)

        data: pd.DataFrame = data.rename(columns=self.__class__.RENAME_COLUMNS)

        return data
    
    def select_data(self, *, data: pd.DataFrame):
        # Clean the dataset for only the desired columns
        data: pd.DataFrame = data[self.__class__.DESIRED_COLUMNS]
