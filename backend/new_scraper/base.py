from collections.abc import Callable
import threading
from typing import Any, Iterable, Mapping, Optional, Type

import pandas as pd
from pandas._typing import Dtype

from new_scraper.abstract_scraper import AbstractDatasetConfig, AbstractScraper
from scraper.util.dataset_helpers import augment_dataframe, filter_dataframe
from sql_app.register.base import BaseTable
from typing import TypeAlias, NamedTuple
from pydantic.fields import FieldInfo

QueryArgs: TypeAlias = dict[str, str]
QuerySet: TypeAlias = list[QueryArgs]


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


class TableConfig:
    # This could maybe come from the table itself, then overriden by this
    COLUMN_TYPES: Optional[dict[str, Dtype]] = None
    DATETIME_COLUMNS: dict[str, str] = {}

    # Adds column labled by key using a synctatic string or a callable function with argument that accepts the full dataset.
    STAT_AUGMENTATIONS: dict[str, str | Callable[[pd.DataFrame], pd.Series]] = {}

    # Select specific rows from the dataset based on callable filter functions
    FILTERS: list[Callable] = []
    RENAME_COLUMNS: dict[str, str] = {}

    # Rename values by key to the specified value
    # RENAME_VALUES = {}

    # TABLE: Optional[BaseTable] = None

    # A function to tranform a specific column (key) on a dataset by a callable function (value) uses apply method
    TRANSFORMATIONS: dict[str | tuple[str, str], Callable[[Any], Any]] = {}
    # DATA_TRANSFORMATIONS: list[Callable[[pd.DataFrame], pd.DataFrame]] = []
    # QUERY_SAVE_COLUMNS: dict[str, str] | list[str] = []
    # COLUMN_ORDERING: list[str] = []

    HREF_SAVE_MAP: dict[str, str] = {}
    # REQUIRED_COLUMNS: list[str] = []

    # REFRESH_RATE: int = 5
    # LOG_LEVEL = logging.WARNING

    def __init__(
        self,
        *,
        identification_function: Callable[[pd.DataFrame], bool],
        sql_table: BaseTable,
    ):
        self.identification_function = identification_function
        self.sql_table = sql_table

        self.primary_key: str = self.sql_table.model_class._meta.primary_key.name  # type: ignore

        self.datetime_columns: dict[str, str] = self.__class__.DATETIME_COLUMNS

        self.column_types = get_column_types_for_table(
            table=self.sql_table,
            ignore_columns=list(self.__class__.DATETIME_COLUMNS.keys()),
        )

        # self.column_types: dict[str, Dtype] = kwargs.get(
        #     "column_types", self.__class__.COLUMN_TYPES
        # )


class DatasetLinkage:
    def __init__(self):
        self.query_set = []


class BaseHTMLDatasetConfig:
    def __init__(
        self,
        *,
        table_configs: list[TableConfig] = [],
        query_set: Optional[QuerySet] = None,
    ):
        self.table_configs: list[TableConfig] = table_configs
        self.query_set: Optional[QuerySet] = query_set
        # self.dataset_links:
        self.data = None

        self.linked_datasets = []

    @property
    def base_download_url(self):
        raise NotImplementedError(
            "Must specify a base download url property in your subclass."
        )

    # def get_query_set(self):
    #     return super().get_query_set()

    def get_download_url(self, *, query_args: QueryArgs) -> str:
        return self.base_download_url.format(**query_args)

    def add_table_config(self, table_config: TableConfig):
        self.table_configs.append(table_config)

    # def extract_dataset_from_html_tables(self, *, html_tables: list[pd.DataFrame]) -> pd.DataFrame:


LinkFunction: TypeAlias = Callable[[pd.DataFrame], QuerySet]
DatasetLink: TypeAlias = dict[TableConfig, tuple[BaseHTMLDatasetConfig, LinkFunction]]


class BaseScraper(threading.Thread):

    def __init__(self) -> None:
        self.datasets: list[BaseHTMLDatasetConfig] = []
        self.dataset_links: DatasetLink = {}
        self.RUNNING = True

        threading.Thread.__init__(self, name=self.__class__.__name__)

    def add_dataset(self, config: BaseHTMLDatasetConfig):
        self.datasets.append(config)

    def link_datasets(
        self,
        source: TableConfig,
        target: BaseHTMLDatasetConfig,
        link_function: LinkFunction,
    ):
        self.dataset_links[source] = (target, link_function)

    def download_data(self, *, url: str) -> list[pd.DataFrame]:
        return pd.read_html(url, extract_links="body")

    def clean_data(self, *, data: pd.DataFrame, config: TableConfig) -> pd.DataFrame:
        """
        Manipulate the dataset column types, add columns, slice columns.

        **Override this for anything you want to be done to the dataset AFTER saving.
        """
        # # self.logger.debug("Configuring data.")

        if config.__class__.HREF_SAVE_MAP:
            for column in data.columns:
                if column in config.__class__.HREF_SAVE_MAP:
                    data[config.__class__.HREF_SAVE_MAP[column]] = data[column].apply(
                        lambda x: x[1]
                    )
                data[column] = data[column].apply(lambda x: x[0])

        # Rename columns to desired names
        data = data.rename(columns=config.__class__.RENAME_COLUMNS)

        # Replace row values with desired row values
        # data = data.replace(config.__class__.RENAME_VALUES)

        # Apply all transformations to the dataset
        for column, transformation in config.__class__.TRANSFORMATIONS.items():
            if type(column) == tuple:
                from_column, to_column = column
            else:
                from_column = to_column = column

            data[to_column] = data[from_column].apply(transformation)

        # print(data)
        # print(data.columns)

        # for transformation_function in self.__class__.DATA_TRANSFORMATIONS:
        #     data = transformation_function(dataset=data)

        # data["weight"] = data["weight"].replace(to_replace="", value=0)

        # Convert the columns to the desired types
        if config.column_types:
            try:
                data = data.astype(config.column_types)
            except pd.errors.IntCastingNaNError as e:
                # self.logger.warning(e)
                print(e)

        # Convert datetime columns appropriately
        for key, dt_format in config.__class__.DATETIME_COLUMNS.items():
            data[key] = pd.to_datetime(data[key], format=dt_format)

        # Add additional columns to augment the dataset and clean the unnecessary ones out
        data = augment_dataframe(
            dataframe=data, augmentations=config.__class__.STAT_AUGMENTATIONS
        )

        # Apply any filters to the dataset
        data = filter_dataframe(dataframe=data, filters=config.__class__.FILTERS)

        # data = reorder_columns(
        #     dataframe=data, column_order=self.__class__.COLUMN_ORDERING
        # )

        # data = data.replace(to_replace="None", value=np.nan).dropna(
        #     subset=self.__class__.REQUIRED_COLUMNS
        # )

        # if self.primary_key in list(data.columns):
        #     data = data.set_index(self.primary_key)

        return data

    def save_data(self, data: pd.DataFrame, sql_table: BaseTable) -> None:
        """"""
        print(data)

    def download_and_process_data(
        self, *, config: BaseHTMLDatasetConfig, query_args: Optional[QueryArgs] = None
    ) -> None:
        if query_args:
            url = config.get_download_url(query_args=query_args)
        else:
            url = config.base_download_url

        print(url)
        tables = self.download_data(url=url)

        for table_config in config.table_configs:
            matched_table = next(
                (
                    table
                    for table in tables
                    if table_config.identification_function(table)
                ),
                None,
            )
            if matched_table is None:
                raise ValueError("No matching table found.")

            cleaned_data = matched_table

            # data = cleaned_data
            # Apply each cleaning function
            data = self.clean_data(data=cleaned_data, config=table_config)

            self.save_data(data, table_config.sql_table)

            # get query args from the current dataset and pass it to a linked dataset
            if table_config in self.dataset_links:
                linked_config, link_function = self.dataset_links[table_config]
                linked_query_set = link_function(data)

                for sub_query in linked_query_set:
                    self.download_and_process_data(
                        config=linked_config, query_args=sub_query
                    )
            else:
                # Handle the case where no table matches the config
                print(f"No matching table found for config, skipping.")

        # if config in self.dataset_links:
        #     linked_config, link_function = self.dataset_links[config]
        #     linked_query_set = link_function(data)

        #     for sub_query in linked_query_set:
        #         self.download_and_process_data(
        #             config=linked_config, query_args=sub_query
        #         )

    def run(self):
        print("RUNNING")
        for config in self.datasets:
            if config.query_set:
                for query_args in config.query_set:
                    self.download_and_process_data(config=config, query_args=query_args)
            else:
                self.download_and_process_data(config=config)
