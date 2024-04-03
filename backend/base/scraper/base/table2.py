from typing import Any, Callable, Literal, NotRequired, Optional, Unpack

import numpy as np
import pandas as pd
from base.scraper.base.util import QueryArgs
from base.scraper.util.dependency_tree_helpers import DependencyKwargs, DependentObject
from base.sql_app.register.base_table import BaseTable
from base.util.dataset_helpers import augment_dataframe, filter_dataframe
from base.util.pydantic_validator import PydanticValidatorMixin
from typing_extensions import TypedDict

from .table_entry_serializers import BaseTableEntrySerializer


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
    # values that should be considered nan for the table
    nan_values: NotRequired[list[str]]

    # serializer
    serializer: NotRequired[BaseTableEntrySerializer]

    # cache_generator
    cached_query_generator: NotRequired[Callable[[Optional[QueryArgs]], pd.DataFrame]]


class TableConfig(
    DependentObject["TableConfig", DependencyKwargs], PydanticValidatorMixin
):

    NAN_VALUES: list[str] = []

    CACHED_QUERY_GENERATOR: Callable[[Optional[QueryArgs]], pd.DataFrame] = (
        lambda x: pd.DataFrame()
    )

    def __init__(
        self,
        identification_function: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]],
        sql_table: BaseTable,
        name: str,
        table_serializer: BaseTableEntrySerializer,
        **kwargs: Unpack[TableConfigArgs],
    ):
        super().__init__(name=name, validator=DependencyKwargs)

        self._sql_table = sql_table
        self._identification_function = identification_function
        self._table_serializer = table_serializer

        self.primary_key: str = self._sql_table.model_class._meta.primary_key.name  # type: ignore

        # # extract info from the given dataset
        self.nan_values = kwargs.get("nan_values", self.__class__.NAN_VALUES)
        self.cached_query_generator = kwargs.get(
            "cached_query_generator", self.__class__.CACHED_QUERY_GENERATOR
        )

        self.data = pd.DataFrame()
        self.staged_data = pd.DataFrame()
        self.data_source: Literal["cached", "downloaded"] = "downloaded"

        self.inheritances: list[TableInheritance] = []

    @property
    def table_serializer(self):
        return self._table_serializer

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
            if column in self.table_serializer.html_save_fields:
                data[self.table_serializer.html_save_fields[column]] = data[
                    column
                ].apply(lambda x: x[1])
            data[column] = data[column].apply(lambda x: x[0] if type(x) == tuple else x)

        data = data.replace(self.nan_values, np.nan, regex=True)

        for name, field in self.table_serializer.get_fields().items():
            data = field.execute(data)

        if self.primary_key in list(data.columns):
            data = data.set_index(self.primary_key)

        return data
