import logging
import threading
import traceback
from collections.abc import Callable
from functools import reduce
from time import sleep, time
from typing import Any, Literal, NotRequired, Optional, Type, TypeAlias, Union, Unpack

import numpy as np
import pandas as pd

# from nbastats.manage import TableConfigArgs
# from base.scraper.base import (
#     DatasetConfigKwargs,
#     QueryArgs,
#     QuerySet,
#     ScraperKwargs,
#     TableConfigArgs,
# )
from base.scraper.pydantic_validator import PydanticValidatorMixin
from base.scraper.util.dependency_tree_helpers import (
    DependencyKwargs,
    DependentObject,
    topological_sort_dependency_tree,
)
from base.sql_app.register import BaseTable
from base.util.dataset_helpers import augment_dataframe, filter_dataframe
from click import Option
from fastapi import dependencies
from pandas._typing import Dtype
from pydantic.fields import FieldInfo
from typing_extensions import TypedDict

DEFAULT_LOG_FORMATTER = logging.Formatter(
    "[{levelname:^10}] [ {asctime} ] [{threadName:^20}]  {message}",
    "%I:%M:%S %p",
    style="{",
)

STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(DEFAULT_LOG_FORMATTER)

QueryArgs: TypeAlias = dict[str, Any]
QuerySet: TypeAlias = list[QueryArgs]


class TableConfigArgs(TypedDict):
    # identification_function: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]]
    # sql_table: BaseTable

    datetime_columns: NotRequired[dict[str, str]]

    # Adds column labled by key using a synctatic string or a callable function with argument that accepts the full dataset.
    stat_augmentations: NotRequired[
        dict[str, str | Callable[[pd.DataFrame], pd.Series]]
    ]

    # Select specific rows from the dataset based on callable filter functions
    filters: NotRequired[list[Callable]]
    rename_columns: NotRequired[dict[str, str]]
    rename_values: NotRequired[dict[str, dict[Any, Any]]]
    nan_values: NotRequired[list[str]]

    # A function to tranform a specific column (key) on a dataset by a callable function (value) uses apply method
    transformations: NotRequired[dict[str | tuple[str, str], Callable[[Any], Any]]]
    required_fields: NotRequired[list[str]]
    query_save_columns: NotRequired[dict[str, str]]
    href_save_map: NotRequired[dict[str, str]]


class DatasetConfigKwargs(TypedDict):
    # base_download_url: str
    # name: str
    # dependencies: NotRequired[list[str]]
    table_configs: NotRequired[Optional[dict[str, "TableConfig"]]]
    default_query_set: NotRequired[Optional[QuerySet]]


class ScraperKwargs(TypedDict):
    datasets: NotRequired[dict[str, "BaseHTMLDatasetConfig"]]
    log_level: NotRequired[int]
    download_rate: NotRequired[int]
    active: NotRequired[bool]
    align: NotRequired[Union[Literal["nested"], Literal["inline"]]]


def combine_lists_of_dicts(*lists):
    # Combine the lists of dictionaries
    combined_list = [
        reduce(lambda d1, d2: {**d1, **d2}, dicts) for dicts in zip(*lists)
    ]
    return combined_list


class TableInheritance:
    def __init__(
        self,
        *,
        source: "TableConfig",
        inheritance_function: Callable[
            [pd.DataFrame], pd.DataFrame
        ] = lambda dataframe: dataframe,
    ) -> None:
        self.source: "TableConfig" = source
        self.inheritance_function: Callable[[pd.DataFrame], pd.DataFrame] = (
            inheritance_function
        )

    def __str__(self):
        return f"{self.source.name} : {self.inheritance_function}"


class TableConfig(
    DependentObject["TableConfig", "DependencyKwargs"], PydanticValidatorMixin
):
    # This could maybe come from the table itself, then overriden by this
    DATETIME_COLUMNS: dict[str, str] = {}

    # Adds column labled by key using a synctatic string or a callable function with argument that accepts the full dataset.
    STAT_AUGMENTATIONS: dict[str, str | Callable[[pd.DataFrame], pd.Series]] = {}

    # Select specific rows from the dataset based on callable filter functions
    FILTERS: list[Callable] = []
    RENAME_COLUMNS: dict[str, str] = {}
    RENAME_VALUES: dict[str, dict[Any, Any]] = {}
    NAN_VALUES: list[str] = []

    # A function to tranform a specific column (key) on a dataset by a callable function (value) uses apply method
    TRANSFORMATIONS: dict[str | tuple[str, str], Callable[[Any], Any]] = {}

    REQUIRED_FIELDS: list[str] = []
    QUERY_SAVE_COLUMNS: dict[str, str] = {}

    HREF_SAVE_MAP: dict[str, str] = {}

    def __init__(
        self,
        identification_function: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]],
        sql_table: BaseTable,
        name: str,
        **kwargs: Unpack[TableConfigArgs],
    ):
        super().__init__(name=name, validator=DependencyKwargs)

        self._sql_table = sql_table
        self._identification_function = identification_function

        # extract info from the given dataset
        self.primary_key: str = self._sql_table.model_class._meta.primary_key.name  # type: ignore
        self.datetime_columns: dict[str, str] = self.__class__.DATETIME_COLUMNS

        # If we still don't have column types, get them from the table
        ignore_columns = (
            list(self.__class__.DATETIME_COLUMNS.keys())
            + list(self.__class__.STAT_AUGMENTATIONS.keys())
            + [self.primary_key]
        )
        self.column_types = self._sql_table.get_column_types(
            ignore_columns=ignore_columns,
        )

        self.desired_columns = list(
            sql_table.table_entry_serializer_class.model_fields.keys()
        )

        self.data = pd.DataFrame()
        self.staged_data = pd.DataFrame()
        self.data_source: Literal["cached", "downloaded"] = "downloaded"

        self.inheritances: list[TableInheritance] = []

    def cached_data(self, *, query_args: Optional[QueryArgs] = None) -> pd.DataFrame:
        return pd.DataFrame()

    def add_inheritance(
        self,
        *,
        source: "TableConfig",
        inheritance_function: Callable[[pd.DataFrame], pd.DataFrame],
    ):
        self.inheritances.append(
            TableInheritance(source=source, inheritance_function=inheritance_function)
        )

    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Manipulate the dataset column types, add columns, slice columns.

        **Override this for anything you want to be done to the dataset AFTER saving.
        """
        if data.empty:
            return pd.DataFrame()

        for column in data.columns:
            if column in self.__class__.HREF_SAVE_MAP:
                data[self.__class__.HREF_SAVE_MAP[column]] = data[column].apply(
                    lambda x: x[1]
                )
            data[column] = data[column].apply(lambda x: x[0] if type(x) == tuple else x)

        data = data.replace(self.__class__.NAN_VALUES, np.nan, regex=True)

        # Rename columns to desired names
        data = data.rename(columns=self.__class__.RENAME_COLUMNS)

        # Replace row values with desired row values
        data = data.replace(self.__class__.RENAME_VALUES)

        # Drop rows with nan where field is required
        data = data.dropna(subset=self.__class__.REQUIRED_FIELDS)

        # Apply all transformations to the dataset
        for column, transformation in self.__class__.TRANSFORMATIONS.items():
            if type(column) == tuple:
                from_column, to_column = column
            else:
                from_column = to_column = column

            data[to_column] = data[from_column].apply(transformation)

        data = data.dropna(subset=self.__class__.REQUIRED_FIELDS)

        # Convert the columns to the desired types
        if self.column_types:
            try:
                data = data.astype(self.column_types)
            except pd.errors.IntCastingNaNError as e:
                # self.logger.warning(e)
                print(e)

        # Convert datetime columns appropriately
        for key, dt_format in self.__class__.DATETIME_COLUMNS.items():
            data[key] = pd.to_datetime(data[key], format=dt_format)

        # Add additional columns to augment the dataset and clean the unnecessary ones out
        data = augment_dataframe(
            dataframe=data, augmentations=self.__class__.STAT_AUGMENTATIONS
        )

        # Apply any filters to the dataset
        data = filter_dataframe(dataframe=data, filters=self.__class__.FILTERS)

        data = data.dropna(subset=self.__class__.REQUIRED_FIELDS)

        data = data[self.desired_columns]
        if self.primary_key in list(data.columns):
            data = data.set_index(self.primary_key)

        return data


class DatasetConfigDependencyKwargs(DependencyKwargs):
    table_name: str
    query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]]


class BaseHTMLDatasetConfig(
    DependentObject["BaseHTMLDatasetConfig", "DatasetConfigDependencyKwargs"],
    PydanticValidatorMixin,
):

    def __init__(
        self,
        *,
        name: str,
        base_download_url: str,
        **kwargs: Unpack[DatasetConfigKwargs],
    ):
        super().__init__(name=name, validator=DatasetConfigDependencyKwargs)

        self._base_download_url: str = base_download_url

        # constants specified in intantiation
        self._table_configs: dict[str, TableConfig] = kwargs.get("table_configs") or {}
        self._default_query_set: Optional[QuerySet] = (
            kwargs.get("default_query_set") or []
        )
        self.nested_datasets: list["BaseHTMLDatasetConfig"] = []

        self.data_source: Literal["cached", "downloaded"] = "downloaded"

        args_expected: int = self.base_download_url.count("{}")

        if args_expected:
            self.static = False
        else:
            self.static = True

    def __str__(self):
        return self.name

    @property
    def base_download_url(self) -> str:
        return self._base_download_url
        # raise NotImplementedError(
        #     "Must specify a base download url property in your subclass."
        # )

    @property
    def name(self) -> str:
        return self._name

    def add_table_config(self, *, table_config: TableConfig):
        self._table_configs[table_config.name] = table_config

    def add_nested_dataset(
        self,
        *,
        dataset: "BaseHTMLDatasetConfig",
    ):
        self.nested_datasets.append(dataset)

    @property
    def query_set(self) -> Optional[QuerySet]:
        if self.dependencies:
            query_set_extractions = []
            for dependency in self.dependencies:
                # source_table = dependency.source
                # TODO: verify these links are accurate in configure
                dependency_data = dependency.source._table_configs[
                    dependency.meta.table_name
                ].data

                if dependency_data.empty:
                    raise Exception(
                        f"Dataset {self.__class__.__name__} processed before dependency {dependency.source.__class__.__name__}."
                    )

                query_set_extractions.append(
                    dependency.meta.query_set_provider(dependency_data)
                )

            return combine_lists_of_dicts(*query_set_extractions)

        elif self._default_query_set:
            return self._default_query_set

        elif self.static:
            return None

        else:
            raise Exception(
                "Must specify a default query set if no dependencies are provided."
            )

    def _configure(self):
        sorted = topological_sort_dependency_tree(dependency_tree=self._table_configs)  # type: ignore

        table_configs: dict[str, TableConfig] = {}

        for table_name in sorted:
            table_configs[table_name] = self._table_configs[table_name]

        self._table_configs = table_configs

        self._configured = True

    def _get_download_url(self, *, query_args: QueryArgs) -> str:
        return self.base_download_url.format(**query_args)

    def load_data_from_cache(self, *, query_args: Optional[QueryArgs] = None) -> None:
        for table_name, table_config in self._table_configs.items():
            table_config.data = table_config.cached_data(query_args=query_args)

            if not table_config.data.empty:
                table_config.data_source = "cached"
            else:
                table_config.data_source = "downloaded"

    def extract_tables(self, url: str) -> list[pd.DataFrame]:
        return pd.read_html(url, extract_links="body")


# class DatasetDependency:
#     def __init__(
#         self,
#         *,
#         source: "BaseHTMLDatasetConfig",
#         table_name: str,
#         query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]],
#     ) -> None:
#         self.source: "BaseHTMLDatasetConfig" = source
#         self.table_name: str = table_name
#         self.query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]] = (
#             query_set_provider
#         )


class BaseScraper(threading.Thread):

    def __init__(self, *, name: str, **kwargs: Unpack[ScraperKwargs]) -> None:
        threading.Thread.__init__(self, name=name)

        self._dataset_configs: dict[str, BaseHTMLDatasetConfig] = (
            kwargs.get("datasets") or {}
        )
        self._configured: bool = False

        self.RUNNING: Literal[False, True] = kwargs.get("active", True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(kwargs.get("log_level", logging.INFO))
        self.logger.addHandler(STREAM_HANDLER)

        self.download_rate = kwargs.get("download_rate", 5)
        self.last_download_time = time()

        self.alignment = kwargs.get("align", "inline")

    def set_log_level(self, log_level: int):
        self.logger.setLevel(log_level)

    def add_dataset_config(self, dataset_config: BaseHTMLDatasetConfig):
        """
        Add a dataset configuration to the scraper.
        """
        self._dataset_configs[dataset_config.name] = dataset_config

    def configure(self):
        """
        Configure the dataset_configurations based on dependency tree.
        Must be run before the datascraper starts.
        """
        sorted = topological_sort_dependency_tree(dependency_tree=self._dataset_configs)  # type: ignore

        dataset_configs: dict[str, BaseHTMLDatasetConfig] = {}

        for dataset_name in sorted:
            self._dataset_configs[dataset_name]._configure()

        if self.alignment == "nested":
            current_config = dataset_configs[sorted[0]] = self._dataset_configs[
                sorted[0]
            ]
            for dataset_name in sorted[1:]:
                nested_config = self._dataset_configs[dataset_name]
                current_config.add_nested_dataset(dataset=nested_config)
                current_config = nested_config

        else:
            for dataset_name in sorted:
                dataset_configs[dataset_name] = self._dataset_configs[dataset_name]

        self._dataset_configs = dataset_configs

        self._configured = True

    def identify_table(
        self, table_config: TableConfig, tables: list[pd.DataFrame]
    ) -> Optional[pd.DataFrame]:
        data = table_config._identification_function(tables)
        # data = next(
        #     (table for table in tables if table_config._identification_function(table)),
        #     None,
        # )
        return data

    def download_and_process_query(
        self, *, config: BaseHTMLDatasetConfig, query_args: Optional[QueryArgs] = None
    ) -> None:

        # get the download url from the query args
        url = (
            config._get_download_url(query_args=query_args)
            if query_args
            else config.base_download_url
        )

        # if this specific query is already save in the database, fetch that instead
        config.load_data_from_cache(query_args=query_args)
        if all(
            [
                table_config.data_source == "cached"
                for table_config in config._table_configs.values()
            ]
        ):
            config.data_source = "cached"

        else:
            config.data_source = "downloaded"

            # self.logger.info(f"Downloading data for {config.name}.")
            if self.last_download_time:
                wait = max(self.last_download_time - time() + self.download_rate, 0)
            else:
                wait = 0

            if wait:
                sleep(wait)

            tables = config.extract_tables(url=url)
            self.last_download_time = time()

            # find the table matching the identification function. Error if not found
            for table_name, table_config in config._table_configs.items():
                data = self.identify_table(table_config=table_config, tables=tables)

                if data is None:
                    raise ValueError("No matching table found.")

                # Add any of the query arguments to the dataframe if desired.
                for (
                    df_column,
                    query_key,
                ) in table_config.__class__.QUERY_SAVE_COLUMNS.items():
                    if query_args and query_key in query_args:
                        data[df_column] = query_args[query_key]

                # Apply each cleaning function
                try:
                    table_config.data = table_config._clean_data(data=data)
                    # table_config.data_source = "downloaded"
                    self.logger.info(f"Downloaded data for {table_config.name}.")
                except Exception as e:
                    raise Exception(f"{config.__class__.__name__}: {e}")

                # return data

    def save_data(self, dataset_config: BaseHTMLDatasetConfig) -> None:
        """
        Save the data for the dataset and any nested datasets.
        """
        self.logger.info("Saving data to database.")

        # Use staging if there is backed up data that needs to be saved that was
        # waiting for a dependency
        for table_config in dataset_config._table_configs.values():
            if table_config.data_source != "cached":
                self.save_table(table_config=table_config)

        # recurse into nested datatsets
        for nested_config in dataset_config.nested_datasets:
            self.save_data(dataset_config=nested_config)

    def save_table(self, table_config: TableConfig) -> None:
        """
        Save the data for the dataset and any nested datasets.
        """
        self.logger.info(f"Saving data for table {table_config.name}.")

        # Use staging if there is backed up data that needs to be saved that was
        # waiting for a dependency
        data = (
            table_config.data
            if table_config.staged_data.empty
            else table_config.staged_data
        )

        # reset the staged data as we have successfully downloaded
        table_config.staged_data = pd.DataFrame()

        data = data.fillna(np.nan).replace([np.nan], [None])

        for index, row in data.iterrows():
            row_data = row.to_dict()
            row_data["id"] = index
            if index == None:
                self.logger.warning(row)
            table_config._sql_table.update_or_insert_record(data=row_data)

        self.logger.debug(f"\n{data}")

    def perform_single_pass(
        self, dataset_config: BaseHTMLDatasetConfig, query_args: Optional[QueryArgs]
    ):
        """
        Perform a single pass through of a dataset using specific query args and
        nesting inside nested datasets.
        """
        self.download_and_process_query(config=dataset_config, query_args=query_args)

        for nested_dataset in dataset_config.nested_datasets:
            self.process_dataset(
                dataset_config=nested_dataset, query_set=nested_dataset.query_set
            )

    def resolve_inheritances(
        self, *, dataset_config: BaseHTMLDatasetConfig, set_data_source: bool = True
    ) -> Optional[bool]:
        """
        Backwards resolve any inherited fields after all dependencies have been exhausted.
        Specify confirm_update as True to return a boolean designating where there was any
        update performed on the dataset configuration.
        """
        for table_name, table_config in dataset_config._table_configs.items():
            if set_data_source:
                data = table_config.data.copy()

            for inheritance in table_config.inheritances:
                if not inheritance.source.staged_data.empty:
                    inherited_data = inheritance.inheritance_function(
                        inheritance.source.staged_data
                    )

                    table_config.data.update(inherited_data)

            if set_data_source:
                if not data.equals(table_config.data):
                    dataset_config.data_source = "downloaded"
                    table_config.data_source = "downloaded"

    def process_dataset(
        self, dataset_config: BaseHTMLDatasetConfig, query_set: Optional[QuerySet]
    ):
        """
        Process an entire dataset by iterating through its query set and
        performing a single pass, resolving inheritances, and then saving
        all data (including nested dataset functionality).
        """

        if query_set is None:
            if dataset_config.static:
                ready_for_save: bool = all(
                    [
                        dependency.source.data_source == "cached"
                        for dependency in dataset_config.dependencies
                    ]
                )

                self.perform_single_pass(dataset_config=dataset_config, query_args=None)

                self.resolve_inheritances(
                    dataset_config=dataset_config, set_data_source=True
                )

                self.logger.info(
                    f"{dataset_config.name}: Ready for save = {ready_for_save} : Is already saved = {dataset_config.data_source == 'cached'}"
                )

                if dataset_config.dependencies and not ready_for_save:
                    for table_config in dataset_config._table_configs.values():
                        table_config.staged_data = pd.concat(
                            [table_config.staged_data, table_config.data]
                        )

                elif dataset_config.data_source != "cached":
                    self.save_data(dataset_config=dataset_config)

                else:
                    self.logger.info(
                        f"No new data to save for dataset: {dataset_config.name}."
                    )
        else:
            ready_for_save: bool = all(
                [
                    dependency.source.data_source == "cached"
                    for dependency in dataset_config.dependencies
                ]
            )

            idx, n = 0, len(query_set)

            self.logger.info(f"1 - Beginning download of query set: {query_set}")
            for query in query_set:
                if self.RUNNING == False:
                    break

                self.perform_single_pass(
                    dataset_config=dataset_config, query_args=query
                )

                self.resolve_inheritances(
                    dataset_config=dataset_config, set_data_source=True
                )

                self.logger.info(
                    f"{dataset_config.name}: Ready for save = {ready_for_save} : Is already saved = {dataset_config.data_source == 'cached'}"
                )

                if dataset_config.dependencies and not ready_for_save:
                    for table_config in dataset_config._table_configs.values():
                        table_config.staged_data = pd.concat(
                            [table_config.staged_data, table_config.data]
                        )

                elif dataset_config.data_source != "cached":
                    self.save_data(dataset_config=dataset_config)

                else:
                    self.logger.info(
                        f"No new data to save for dataset: {dataset_config.name}."
                    )

                idx += 1
                self.logger.info(
                    f"3 - {dataset_config.__class__.__name__} query set {round(idx/n * 100, 2)}% complete."
                )

    def execute(self):
        """
        Make a forward pass downloading and saving each dataset in
        the scraper's configuration. To add more datasets, use the 'add_dataset'
        method.
        """
        if not self._dataset_configs:
            raise Exception(
                "No datasets defined - to add datasets, use the 'add_dataset' method."
            )

        for dataset_name, dataset_info in self._dataset_configs.items():
            if self.RUNNING == False:
                break

            dataset_info._configure()

            query_set = dataset_info.query_set

            self.process_dataset(dataset_info, query_set=query_set)

    def kill_process(self, *args):
        """
        Kill the running thread and stop the scraper.
        """
        self.RUNNING = False
        self.logger.critical(f"PROCESS KILLED FOR {self.__class__.__name__}.")

    def run(self):

        if not self._configured:
            raise Exception(
                "Must call '.configure()' on the scraper before running it."
            )

        self.logger.info(f"Starting {self.name}...")

        consecutive_failures: int = 0

        # this will include gamelog dataset
        while self.RUNNING:
            if consecutive_failures >= 10:
                self.kill_process()

            try:
                self.execute()
                consecutive_failures = 0
            except Exception as e:
                self.logger.warning(traceback.format_exc())
                consecutive_failures += 1
