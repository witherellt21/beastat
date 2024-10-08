from typing import Callable, Literal, NotRequired, Optional, Unpack

import numpy as np
import pandas as pd
from core.sql_app import BaseTable
from lib.dependency_trees import DependencyKwargs, DependentObject
from lib.pydantic_validator import PydanticValidatorMixin
from typing_extensions import TypedDict

from .html_table_serializer import BaseHTMLTableSerializer
from .util import QueryArgs


class HTMLTableInheritance:
    def __init__(
        self,
        *,
        source: "BaseHTMLTable",
        inheritance_function: Callable[
            [pd.DataFrame], pd.DataFrame
        ] = lambda dataframe: dataframe,
    ) -> None:
        self.source: "BaseHTMLTable" = source
        self.inheritance_function: Callable[[pd.DataFrame], pd.DataFrame] = (
            inheritance_function
        )

    def __str__(self):
        return f"{self.source.name} : {self.inheritance_function}"


class HTMLTableArgs(TypedDict):
    # values that should be considered nan for the table
    nan_values: NotRequired[list[str]]

    # cache_generator
    cached_query_generator: NotRequired[Callable[[Optional[QueryArgs]], pd.DataFrame]]


class BaseHTMLTable(
    DependentObject["BaseHTMLTable", DependencyKwargs], PydanticValidatorMixin
):
    """
    Base class for an HTML-embedded table.
    """

    NAN_VALUES: list[str] = []
    CACHED_QUERY_GENERATOR: Callable[[Optional[QueryArgs]], pd.DataFrame] = (
        lambda x: pd.DataFrame()
    )

    def __init__(
        self,
        db_table: BaseTable,
        serializer: BaseHTMLTableSerializer,
        identification_function: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]],
        name: str,
        **kwargs: Unpack[HTMLTableArgs],
    ):
        super().__init__(name=name, validator=DependencyKwargs)

        # TODO: lets make identification function a part of the serializer

        self._db_table = db_table
        self._serializer = serializer
        self._identification_function = identification_function

        # # extract info from the given dataset
        self._cached_query_generator = kwargs.get(
            "cached_query_generator", self.__class__.CACHED_QUERY_GENERATOR
        )

        self._staged_data = pd.DataFrame()

        self.data = pd.DataFrame()
        self.nan_values = kwargs.get("nan_values", self.__class__.NAN_VALUES)
        self.primary_key: str = self._db_table.model_class._meta.primary_key.name  # type: ignore
        self.inheritances: list[HTMLTableInheritance] = []

        self.data_source: Literal["cached", "downloaded"] = "downloaded"

    @property
    def db_table(self):
        return self._db_table

    @property
    def serializer(self):
        return self._serializer

    def add_inheritance(
        self,
        *,
        source: "BaseHTMLTable",
        inheritance_function: Callable[[pd.DataFrame], pd.DataFrame],
    ):
        self.inheritances.append(
            HTMLTableInheritance(
                source=source, inheritance_function=inheritance_function
            )
        )

    def identify(self, tables: list[pd.DataFrame]):
        return self._identification_function(tables)

    def cached_data(self, *, query_args: Optional[QueryArgs] = None) -> pd.DataFrame:
        if query_args == None:
            return pd.DataFrame()

        return self._cached_query_generator(query_args)

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Manipulate the dataset column types, add columns, slice columns.

        **Override this for anything you want to be done to the dataset BEFORE saving.
        """
        if data.empty:
            return pd.DataFrame()

        for column in data.columns:
            if column in self.serializer.html_save_fields:
                data[self.serializer.html_save_fields[column]] = data[column].apply(
                    lambda x: x[1]
                )
            data[column] = data[column].apply(lambda x: x[0] if type(x) == tuple else x)

        data = data.replace(self.nan_values, np.nan, regex=True)

        for name, field in self.serializer.get_fields().items():

            try:
                data = field.execute(data)
            except Exception as e:
                raise Exception(f"Error executing {name} for table {self.name}: {e}.")

        if self.primary_key in list(data.columns):
            data = data.set_index(self.primary_key)

        return data

    def add_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add data to the stack.
        """
        self.data = pd.concat([self.data, data])

        return self.data

    def stage_changes(self) -> pd.DataFrame:
        self._staged_data = pd.concat([self._staged_data, self.data])
        self.data = pd.DataFrame()

        return self._staged_data

    def flush_changes(self) -> None:
        """
        Flush the changes from the stage.
        """
        self._staged_data = pd.DataFrame()

    def push(self) -> None:
        """
        Save the data for the dataset and any nested datasets.
        """
        # Use staging if there is backed up data that needs to be saved that was
        # waiting for a dependency
        data = self.stage_changes()

        # reset the staged data as we have successfully downloaded
        self.flush_changes()

        data = data.fillna(np.nan).replace([np.nan], [None])

        for index, row in data.iterrows():
            row_data = row.to_dict()
            row_data["id"] = index

            self._db_table.update_or_insert_record(data=row_data)
