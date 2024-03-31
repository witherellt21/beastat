from typing import Any, Callable, Literal, NotRequired, Optional, Unpack

import numpy as np
import pandas as pd
from base.scraper.base.util import QueryArgs
from base.scraper.pydantic_validator import PydanticValidatorMixin
from base.scraper.util.dependency_tree_helpers import DependencyKwargs, DependentObject
from base.sql_app.register.base_table import BaseTable
from base.util.dataset_helpers import augment_dataframe, filter_dataframe
from typing_extensions import TypedDict


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


class TableConfigArgs(TypedDict):
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

    # cache_generator
    cached_query_generator: NotRequired[Callable[[Optional[QueryArgs]], pd.DataFrame]]


class TableConfig(
    DependentObject["TableConfig", DependencyKwargs], PydanticValidatorMixin
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
    CACHED_QUERY_GENERATOR: Callable[[Optional[QueryArgs]], pd.DataFrame] = (
        lambda x: pd.DataFrame()
    )

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
        self.datetime_columns = kwargs.get(
            "datetime_columns", self.__class__.DATETIME_COLUMNS
        )
        self.stat_augmentations = kwargs.get(
            "stat_augmentations", self.__class__.STAT_AUGMENTATIONS
        )
        self.filters = kwargs.get("filters", self.__class__.FILTERS)
        self.rename_columns = kwargs.get(
            "rename_columns", self.__class__.RENAME_COLUMNS
        )
        self.rename_values = kwargs.get("rename_values", self.__class__.RENAME_VALUES)
        self.nan_values = kwargs.get("nan_values", self.__class__.NAN_VALUES)
        self.transformations = kwargs.get(
            "transformations", self.__class__.TRANSFORMATIONS
        )
        self.required_fields = kwargs.get(
            "required_fields", self.__class__.REQUIRED_FIELDS
        )
        self.query_save_columns = kwargs.get(
            "query_save_columns", self.__class__.QUERY_SAVE_COLUMNS
        )
        self.href_save_map = kwargs.get("href_save_map", self.__class__.HREF_SAVE_MAP)

        print(kwargs)
        self.cached_query_generator = kwargs.get(
            "cached_query_generator", self.__class__.CACHED_QUERY_GENERATOR
        )

        # If we still don't have column types, get them from the table
        ignore_columns = (
            list(self.datetime_columns.keys())
            + list(self.stat_augmentations.keys())
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
        if query_args == None:
            return pd.DataFrame()

        return self.cached_query_generator(query_args)

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
            if column in self.href_save_map:
                data[self.href_save_map[column]] = data[column].apply(lambda x: x[1])
            data[column] = data[column].apply(lambda x: x[0] if type(x) == tuple else x)

        data = data.replace(self.nan_values, np.nan, regex=True)

        # Rename columns to desired names
        data = data.rename(columns=self.rename_columns)

        # Replace row values with desired row values
        data = data.replace(self.rename_values)

        # Drop rows with nan where field is required
        data = data.dropna(subset=self.required_fields)

        # Apply all transformations to the dataset
        for column, transformation in self.transformations.items():
            if type(column) == tuple:
                from_column, to_column = column
            else:
                from_column = to_column = column

            data[to_column] = data[from_column].apply(transformation)

        data = data.dropna(subset=self.required_fields)

        # Convert the columns to the desired types
        if self.column_types:
            try:
                data = data.astype(self.column_types)
            except pd.errors.IntCastingNaNError as e:
                # self.logger.warning(e)
                print(e)

        # Convert datetime columns appropriately
        for key, dt_format in self.datetime_columns.items():
            data[key] = pd.to_datetime(data[key], format=dt_format)

        # Add additional columns to augment the dataset and clean the unnecessary ones out
        data = augment_dataframe(dataframe=data, augmentations=self.stat_augmentations)

        # Apply any filters to the dataset
        data = filter_dataframe(dataframe=data, filters=self.filters)

        data = data.dropna(subset=self.required_fields)

        data = data[self.desired_columns]
        if self.primary_key in list(data.columns):
            data = data.set_index(self.primary_key)

        return data
