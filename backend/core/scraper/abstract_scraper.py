import threading
from abc import ABC, abstractmethod

import pandas as pd
from core.sql_app import BaseTable


class AbstractDatasetConfig(ABC):
    def __init__(
        self, download_url: str, cleaning_functions: list, sql_table: BaseTable
    ):
        self.download_url = download_url
        self.cleaning_functions = cleaning_functions
        self.sql_table = sql_table

    @abstractmethod
    def get_query_set(self):
        """"""


class AbstractScraper(ABC, threading.Thread):
    """_summary_

    Args:
        ABC (_type_): _description_
        threading (_type_): _description_
    """

    @abstractmethod
    def add_dataset(self, config):
        """_summary_"""

    @abstractmethod
    def download_data(self, url: str) -> pd.DataFrame:
        """_summary_

        Args:
            url (str): _description_

        Returns:
            pd.DataFrame: _description_
        """

    @abstractmethod
    def clean_data(self, data: pd.DataFrame, cleaning_functions):
        """ """

    @abstractmethod
    def save_data(self, data: pd.DataFrame, sql_table: BaseTable):
        """"""

    @abstractmethod
    def run(self):
        """"""
