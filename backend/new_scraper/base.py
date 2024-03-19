import logging
import threading
from ast import Call
from collections.abc import Callable
from ctypes import Union
from functools import reduce
from logging import config
from telnetlib import EC
from time import sleep
from typing import (
    Any,
    Iterable,
    Mapping,
    NamedTuple,
    Optional,
    OrderedDict,
    Self,
    Type,
    TypeAlias,
)

import numpy as np
import pandas as pd
from global_implementations import constants
from matplotlib import table
from new_scraper.abstract_scraper import AbstractDatasetConfig, AbstractScraper
from pandas._typing import Dtype
from pydantic.fields import FieldInfo
from scraper.util.dataset_helpers import augment_dataframe, filter_dataframe
from sql_app.register.base import BaseTable

QueryArgs: TypeAlias = dict[str, str]
QuerySet: TypeAlias = list[QueryArgs]

DEFAULT_LOG_FORMATTER = logging.Formatter(
    "[{levelname:^10}] [ {asctime} ] [{threadName:^20}]  {message}",
    "%I:%M:%S %p",
    style="{",
)

STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(DEFAULT_LOG_FORMATTER)


def combine_lists_of_dicts(*lists):
    # Combine the lists of dictionaries
    combined_list = [
        reduce(lambda d1, d2: {**d1, **d2}, dicts) for dicts in zip(*lists)
    ]
    return combined_list


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


class BaseHTMLDatasetConfig:
    # This could maybe come from the table itself, then overriden by this
    DATETIME_COLUMNS: dict[str, str] = {}

    # Adds column labled by key using a synctatic string or a callable function with argument that accepts the full dataset.
    STAT_AUGMENTATIONS: dict[str, str | Callable[[pd.DataFrame], pd.Series]] = {}

    # Select specific rows from the dataset based on callable filter functions
    FILTERS: list[Callable] = []
    RENAME_COLUMNS: dict[str, str] = {}
    RENAME_VALUES: dict[str, dict[Any, Any]] = {}

    # A function to tranform a specific column (key) on a dataset by a callable function (value) uses apply method
    TRANSFORMATIONS: dict[str | tuple[str, str], Callable[[Any], Any]] = {}

    REQUIRED_FIELDS: list[str] = []
    QUERY_SAVE_COLUMNS: dict[str, str] = {}

    HREF_SAVE_MAP: dict[str, str] = {}

    def __init__(
        self,
        *,
        # table_configs: list[TableConfig] = [],
        identification_function: Callable[[pd.DataFrame], bool],
        sql_table: BaseTable,
        query_set: Optional[QuerySet] = None,
    ):
        # self.table_configs: list[TableConfig] = table_configs
        self.identification_function: Callable[[pd.DataFrame], bool] = (
            identification_function
        )
        self.sql_table = sql_table
        self.query_set: Optional[QuerySet] = query_set
        self.data: pd.DataFrame = pd.DataFrame()

        self.primary_key: str = self.sql_table.model_class._meta.primary_key.name  # type: ignore
        self.datetime_columns: dict[str, str] = self.__class__.DATETIME_COLUMNS

        # If we still don't have column types, get them from the table
        ignore_columns = (
            list(self.__class__.DATETIME_COLUMNS.keys())
            + list(self.__class__.STAT_AUGMENTATIONS.keys())
            + [self.primary_key]
        )
        self.column_types = get_column_types_for_table(
            table=self.sql_table,
            ignore_columns=ignore_columns,
        )

        self.desired_columns = list(
            sql_table.table_entry_serializer_class.model_fields.keys()
        )

    @property
    def base_download_url(self):
        raise NotImplementedError(
            "Must specify a base download url property in your subclass."
        )

    def get_download_url(self, *, query_args: QueryArgs) -> str:
        return self.base_download_url.format(**query_args)

    def clean_data(self) -> pd.DataFrame:
        """
        Manipulate the dataset column types, add columns, slice columns.

        **Override this for anything you want to be done to the dataset AFTER saving.
        """
        if self.data.empty:
            return pd.DataFrame()

        for column in self.data.columns:
            if column in self.__class__.HREF_SAVE_MAP:
                self.data[self.__class__.HREF_SAVE_MAP[column]] = self.data[
                    column
                ].apply(lambda x: x[1])
            self.data[column] = self.data[column].apply(
                lambda x: x[0] if type(x) == tuple else x
            )

        self.data = self.data.replace(constants.NAN_VALUES, np.nan, regex=True)

        # Rename columns to desired names
        self.data = self.data.rename(columns=self.__class__.RENAME_COLUMNS)

        # Replace row values with desired row values
        self.data = self.data.replace(self.__class__.RENAME_VALUES)

        # print(self.data["Rk"])
        # print("Rk" in self.data.columns)

        self.data = self.data.dropna(subset=self.__class__.REQUIRED_FIELDS)

        # Apply all transformations to the dataset
        for column, transformation in self.__class__.TRANSFORMATIONS.items():
            if type(column) == tuple:
                from_column, to_column = column
            else:
                from_column = to_column = column

            self.data[to_column] = self.data[from_column].apply(transformation)

        self.data = self.data.dropna(subset=self.__class__.REQUIRED_FIELDS)

        # Convert the columns to the desired types
        if self.column_types:
            try:
                self.data = self.data.astype(self.column_types)
            except pd.errors.IntCastingNaNError as e:
                # self.logger.warning(e)
                print(e)

        # Convert datetime columns appropriately
        for key, dt_format in self.__class__.DATETIME_COLUMNS.items():
            self.data[key] = pd.to_datetime(self.data[key], format=dt_format)

        # Add additional columns to augment the dataset and clean the unnecessary ones out
        self.data = augment_dataframe(
            dataframe=self.data, augmentations=self.__class__.STAT_AUGMENTATIONS
        )

        # Apply any filters to the dataset
        self.data = filter_dataframe(
            dataframe=self.data, filters=self.__class__.FILTERS
        )

        self.data = self.data.dropna(subset=self.__class__.REQUIRED_FIELDS)

        self.data = self.data[self.desired_columns]
        if self.primary_key in list(self.data.columns):
            self.data = self.data.set_index(self.primary_key)

        return self.data


class Dependency:
    def __init__(
        self,
        *,
        source_name: str,
        query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]],
    ) -> None:
        self.source_name: str = source_name
        self.query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]] = (
            query_set_provider
        )


class Inheritance:
    def __init__(
        self,
        *,
        source_name: str,
        inheritance_function: Callable[
            [pd.DataFrame], pd.DataFrame
        ] = lambda dataframe: dataframe,
    ) -> None:
        self.source_name: str = source_name
        self.inheritance_function: Callable[[pd.DataFrame], pd.DataFrame] = (
            inheritance_function
        )


class DatasetScrapeConfig:
    def __init__(
        self,
        *,
        config: BaseHTMLDatasetConfig,
        dependencies: list[Dependency] = [],
        inheritances: list[Inheritance] = [],
    ) -> None:
        self.config: BaseHTMLDatasetConfig = config
        self.dependencies: list[Dependency] = dependencies
        self.inheritances: list[Inheritance] = inheritances


class BaseScraper(threading.Thread):

    def __init__(self, *, log_level: int = logging.INFO) -> None:
        threading.Thread.__init__(self, name=self.__class__.__name__)

        self.datasets: OrderedDict[str, DatasetScrapeConfig] = OrderedDict()
        self.RUNNING = True

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        self.logger.addHandler(STREAM_HANDLER)

    def add_dataset(self, dataset_name, scraper_config: DatasetScrapeConfig):
        self.datasets[dataset_name] = scraper_config

    def download_data(self, *, url: str) -> list[pd.DataFrame]:
        return pd.read_html(url, extract_links="body")

    def save_data(self, config: BaseHTMLDatasetConfig) -> None:
        """"""
        self.logger.debug("Saving data to database.")

        data = config.data.fillna(np.nan).replace([np.nan], [None])

        for index, row in data.iterrows():
            row_data = row.to_dict()
            row_data["id"] = index
            if index == None:
                self.logger.warning(row)
            config.sql_table.update_or_insert_record(data=row_data)

        self.logger.debug(f"\n{data}")

    def download_and_process_query(
        self, *, config: BaseHTMLDatasetConfig, query_args: Optional[QueryArgs] = None
    ) -> pd.DataFrame:

        if query_args:
            url = config.get_download_url(query_args=query_args)
        else:
            url = config.base_download_url

        tables = self.download_data(url=url)
        sleep(5)

        data = next(
            (table for table in tables if config.identification_function(table)),
            None,
        )

        if data is None:
            raise ValueError("No matching table found.")

        # Add any of the query arguments to the dataframe if desired.
        for df_column, query_key in config.__class__.QUERY_SAVE_COLUMNS.items():
            if query_args and query_key in query_args:
                data[df_column] = query_args[query_key]

        # Apply each cleaning function
        # data = self.clean_data(data=data, config=config)
        config.data = data

        try:
            data = config.clean_data()
        except Exception as e:
            raise Exception(f"{config.__class__.__name__}: {e}")

        return data

    def process_data(
        self, config: BaseHTMLDatasetConfig, query_set: QuerySet
    ) -> pd.DataFrame:
        self.logger.info(
            f"Processing data for {config.__class__.__name__}. Query set length: {len(query_set)}"
        )
        idx = 0
        n = len(query_set)

        data: pd.DataFrame = pd.DataFrame()
        for query in query_set:
            data = pd.concat(
                [data, self.download_and_process_query(config=config, query_args=query)]
            )

            idx += 1
            self.logger.info(
                f"{config.__class__.__name__} query set {round(idx/n * 100, 2)}% complete."
            )
            return data

        return data

    def forward_pass(self):
        for dataset_name, dataset_info in self.datasets.items():
            if not dataset_info.dependencies:  # No forward dependencies
                # Scrape and clean data
                query_set = dataset_info.config.query_set

                if not query_set:
                    raise Exception(
                        f"Dataset {dataset_name} does not have a query set source so it must have a default query set."
                    )

                dataset_info.config.data = self.process_data(
                    config=dataset_info.config, query_set=query_set
                )

            else:  # has some forward dependencies so get the values from the dependency datasets
                query_set_extractions = []
                for dependency in dataset_info.dependencies:
                    dependency_data = self.datasets[dependency.source_name].config.data

                    if dependency_data.empty:
                        raise Exception(
                            f"Dataset {dataset_name} processed before dependency {dependency.source_name}."
                        )

                    query_set_extractions.append(
                        dependency.query_set_provider(dependency_data)
                    )

                query_set = combine_lists_of_dicts(*query_set_extractions)

                dataset_info.config.data = self.process_data(
                    config=dataset_info.config,
                    query_set=query_set,
                )

    def resolve_inheritances_and_save(self):
        """
        Iterate back through the datasets and resolve inherited fields.
        """
        for dataset_name, dataset_info in self.datasets.items():
            for inheritance in dataset_info.inheritances:

                inherited_data = inheritance.inheritance_function(
                    self.datasets[inheritance.source_name].config.data
                )

                dataset_info.config.data.update(inherited_data)

            self.save_data(dataset_info.config)

    def run(self):
        self.logger.info("Starting Scraper...")
        # this will include gamelog dataset
        while self.RUNNING:
            self.forward_pass()
            self.resolve_inheritances_and_save()
