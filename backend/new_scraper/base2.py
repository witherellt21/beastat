import logging
import threading
from collections.abc import Callable
from functools import reduce
from time import sleep
from typing import Any, Literal, Optional, OrderedDict, Type, TypeAlias, overload

import numpy as np
import pandas as pd
from global_implementations import constants
from new_scraper.abstract_scraper import AbstractDatasetConfig, AbstractScraper
from pandas._typing import Dtype
from pydantic.fields import FieldInfo
from scraper.util.dataset_helpers import augment_dataframe, filter_dataframe
from sql_app.register.base import BaseTable

QueryArgs: TypeAlias = dict[str, Any]
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
        self.staged_data: pd.DataFrame = pd.DataFrame()
        self.data_source: Literal["cached", "downloaded"] = "downloaded"

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

    def is_cached(self, *, query: Optional[QueryArgs] = None) -> bool:
        return False

    def cached_data(self, *, query: Optional[QueryArgs] = None) -> pd.DataFrame:
        return pd.DataFrame()

    def get_download_url(self, *, query_args: QueryArgs) -> str:
        return self.base_download_url.format(**query_args)

    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
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

        data = data.replace(constants.NAN_VALUES, np.nan, regex=True)

        # Rename columns to desired names
        data = data.rename(columns=self.__class__.RENAME_COLUMNS)

        # Replace row values with desired row values
        data = data.replace(self.__class__.RENAME_VALUES)

        # print(self.data["Rk"])
        # print("Rk" in self.data.columns)

        data = data.dropna(subset=self.__class__.REQUIRED_FIELDS)

        # print(self.data)

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


class Dependency2:
    def __init__(
        self,
        *,
        source: BaseHTMLDatasetConfig,
        query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]],
    ) -> None:
        self.source: BaseHTMLDatasetConfig = source
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


class Inheritance2:
    def __init__(
        self,
        *,
        source: BaseHTMLDatasetConfig,
        inheritance_function: Callable[
            [pd.DataFrame], pd.DataFrame
        ] = lambda dataframe: dataframe,
    ) -> None:
        self.source: BaseHTMLDatasetConfig = source
        self.inheritance_function: Callable[[pd.DataFrame], pd.DataFrame] = (
            inheritance_function
        )


class NestedDataset:
    def __init__(
        self,
        dataset_config: "DatasetScrapeConfig",
        query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]],
    ) -> None:
        self.dataset_config = dataset_config
        self.query_set_provider = query_set_provider


class DatasetScrapeConfig:
    def __init__(
        self,
        *,
        dataset: BaseHTMLDatasetConfig,
        nested_datasets: Optional[list["DatasetScrapeConfig"]] = None,
        dependencies: Optional[list[Dependency2]] = None,
        inheritances: Optional[list[Inheritance2]] = None,
    ) -> None:
        self.dataset: BaseHTMLDatasetConfig = dataset

        self.dependencies: list[Dependency2] = dependencies or []
        self.inheritances: list[Inheritance2] = inheritances or []
        self.nested_datasets: list["DatasetScrapeConfig"] = nested_datasets or []

    def add_dependency(
        self,
        *,
        source: BaseHTMLDatasetConfig,
        query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]],
    ):
        self.dependencies.append(
            Dependency2(source=source, query_set_provider=query_set_provider)
        )

    def add_nested_dataset(
        self,
        *,
        dataset_config: "DatasetScrapeConfig",
        # query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]],
    ):
        self.nested_datasets.append(dataset_config)
        # self.nested_datasets.append(
        #     NestedDataset(
        #         dataset_config=dataset_config, query_set_provider=query_set_provider
        #     )
        # )


# class NestedDataset:
#     def __init__(
#         self,
#         dataset: "Dataset",
#         query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]],
#     ) -> None:
#         self.dataset = dataset
#         self.query_set_provider = query_set_provider


class Dataset:
    def __init__(
        self,
        *,
        table: BaseHTMLDatasetConfig,
        # dependencies: list[Dependency] = [],
        # dependencies: list[Dependency2] = [],
        # inheritances: list[Inheritance] = [],
        # inheritances: list[Inheritance2] = [],
    ) -> None:
        self.table: BaseHTMLDatasetConfig = table
        # self.dependencies: list[Dependency] = dependencies
        # self.dependencies: list[Dependency2] = dependencies
        # self.inheritances: list[Inheritance] = inheritances
        # self.inheritances: list[Inheritance2] = inheritances
        self.nested_datasets: list[NestedDataset] = []

    def add_nested_dataset(
        self,
        nested_dataset: "Dataset",
        query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]],
    ):
        self.nested_datasets.append(NestedDataset(nested_dataset, query_set_provider))


class BaseScraper(threading.Thread):

    def __init__(self, *, log_level: int = logging.INFO) -> None:
        threading.Thread.__init__(self, name=self.__class__.__name__)

        self.datasets: OrderedDict[str, DatasetScrapeConfig] = OrderedDict()
        self.RUNNING: Literal[False, True] = True

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        self.logger.addHandler(STREAM_HANDLER)

    def add_dataset(self, dataset_name, scraper_config: DatasetScrapeConfig):
        self.datasets[dataset_name] = scraper_config

    def download_data(self, *, url: str) -> list[pd.DataFrame]:
        return pd.read_html(url, extract_links="body")

    def save_data(self, dataset_config: DatasetScrapeConfig) -> None:
        """"""
        self.logger.info("Saving data to database.")

        data = (
            dataset_config.dataset.data
            if dataset_config.dataset.staged_data.empty
            else dataset_config.dataset.staged_data
        )

        dataset_config.dataset.staged_data = pd.DataFrame()

        data = data.fillna(np.nan).replace([np.nan], [None])

        # print(data)

        for index, row in data.iterrows():
            row_data = row.to_dict()
            row_data["id"] = index
            if index == None:
                self.logger.warning(row)
            dataset_config.dataset.sql_table.update_or_insert_record(data=row_data)

        self.logger.debug(f"\n{data}")

        for nested_config in dataset_config.nested_datasets:
            self.save_data(dataset_config=nested_config)

        # self.logger.debug(f"\n{data}")

    def download_and_process_query(
        self, *, config: BaseHTMLDatasetConfig, query_args: Optional[QueryArgs] = None
    ) -> pd.DataFrame:

        if query_args:
            url = config.get_download_url(query_args=query_args)
        else:
            url = config.base_download_url

        cached_data = config.cached_data(query=query_args)
        if not cached_data.empty:
            config.data_source = "cached"
            return cached_data

        else:
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
            try:
                data = config.clean_data(data=data)
            except Exception as e:
                raise Exception(f"{config.__class__.__name__}: {e}")

            return data

    # def process_data(
    #     self, config: BaseHTMLDatasetConfig, query_set: QuerySet
    # ) -> pd.DataFrame:
    #     self.logger.info(
    #         f"Processing data for {config.__class__.__name__}. Query set length: {len(query_set)}"
    #     )
    #     idx = 0
    #     n = len(query_set)

    #     data: pd.DataFrame = pd.DataFrame()
    #     for query in query_set:
    #         data = pd.concat(
    #             [data, self.download_and_process_query(config=config, query_args=query)]
    #         )

    #         idx += 1
    #         self.logger.info(
    #             f"{config.__class__.__name__} query set {round(idx/n * 100, 2)}% complete."
    #         )

    #     return data

    def perform_single_pass(
        self, dataset_config: DatasetScrapeConfig, query_args: QueryArgs
    ):
        dataset_config.dataset.data = self.download_and_process_query(
            config=dataset_config.dataset, query_args=query_args
        )

        for nested_dataset in dataset_config.nested_datasets:
            # if self.RUNNING == False:
            #     break

            query_set_extractions = []
            for dependency in nested_dataset.dependencies:
                if self.RUNNING == False:
                    break

                dependency_data = dependency.source.data

                if dependency_data.empty:
                    raise Exception(
                        f"Dataset {nested_dataset.dataset.__class__.__name__} processed before dependency {dependency.source.__class__.__name__}."
                    )

                query_set_extractions.append(
                    dependency.query_set_provider(dependency_data)
                )

            query_set = combine_lists_of_dicts(*query_set_extractions)

            self.process_dataset(dataset_config=nested_dataset, query_set=query_set)

    @overload
    def resolve_inheritances(
        self, *, dataset_config: DatasetScrapeConfig, confirm_update: Literal[True]
    ) -> bool: ...

    @overload
    def resolve_inheritances(
        self, *, dataset_config: DatasetScrapeConfig, confirm_update: Literal[False]
    ) -> None: ...

    @overload
    def resolve_inheritances(self, *, dataset_config: DatasetScrapeConfig) -> None: ...

    def resolve_inheritances(
        self, *, dataset_config: DatasetScrapeConfig, confirm_update: bool = False
    ) -> Optional[bool]:
        if confirm_update:
            data = dataset_config.dataset.data.copy()
            self.logger.debug(f"Starting data: \n\n{data}")

        for inheritance in dataset_config.inheritances:
            if not inheritance.source.staged_data.empty:
                inherited_data = inheritance.inheritance_function(
                    inheritance.source.staged_data
                )

                dataset_config.dataset.data.update(inherited_data)

        if confirm_update:
            self.logger.debug(f"Ending data: \n\n{dataset_config.dataset.data}")
            return not data.equals(dataset_config.dataset.data)

    def process_dataset(self, dataset_config: DatasetScrapeConfig, query_set: QuerySet):
        full_data = pd.DataFrame()
        ready_for_save: bool = all(
            [
                dependency.source.data_source == "cached"
                for dependency in dataset_config.dependencies
            ]
        )

        idx = 0
        n = len(query_set)

        # print(dataset_config.dataset.data_source)
        # self.logger.debug(
        #     f"{dataset_config.dataset.__class__.__name__}: {ready_for_save}"
        # )
        self.logger.info(f"Beginning download of query set: {query_set}")
        for query in query_set:
            if self.RUNNING == False:
                break

            self.perform_single_pass(dataset_config=dataset_config, query_args=query)

            data_was_updated = self.resolve_inheritances(
                dataset_config=dataset_config, confirm_update=True
            )

            self.logger.info(
                f"{dataset_config.dataset.__class__.__name__}: {ready_for_save} : {data_was_updated} : {dataset_config.dataset.data_source == 'cached'}"
            )

            if dataset_config.dataset.data_source == "cached" and not data_was_updated:
                pass
            elif dataset_config.dependencies and not ready_for_save:
                full_data = pd.concat([full_data, dataset_config.dataset.data])
            else:
                self.save_data(dataset_config=dataset_config)

            idx += 1
            self.logger.info(
                f"{dataset_config.dataset.__class__.__name__} query set {round(idx/n * 100, 2)}% complete."
            )

        dataset_config.dataset.staged_data = pd.concat(
            [dataset_config.dataset.staged_data, full_data]
        )
        # self.logger.debug(f"Ready for back pass: {dataset_config.dataset.staged_data}")

    def forward_pass(self):
        for dataset_name, dataset_info in self.datasets.items():
            if self.RUNNING == False:
                break

            query_set = dataset_info.dataset.query_set

            if not query_set:
                raise Exception("Must specify a query set.")

            # query_set = query_set[16:17]

            self.process_dataset(dataset_info, query_set=query_set)

    def run(self):
        self.logger.info("Starting Scraper...")
        # this will include gamelog dataset
        while self.RUNNING:
            self.forward_pass()
            # self.resolve_inheritances_and_save()
