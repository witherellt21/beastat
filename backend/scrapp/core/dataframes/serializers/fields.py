import math
from datetime import datetime
from typing import (
    Annotated,
    Any,
    Callable,
    Generic,
    NotRequired,
    Optional,
    Type,
    TypeVar,
    Union,
    Unpack,
)

import numpy as np
import pandas as pd
from lib.dataframes import filter_dataframe
from pandera.typing import Series
from scrapp.core.exceptions import ColumnDoesNotExist
from typing_extensions import TypedDict

T = TypeVar("T")


class FieldKwargs(TypedDict):
    default: NotRequired[
        Union[
            str, np.int64, float, None, Callable[..., Union[str, np.int64, float, None]]
        ]
    ]
    groups: NotRequired[Annotated[Optional[tuple[str, ...]], None]]


class BaseField(Generic[T]):
    """
    Base class for a an HTMLTable field.
    """

    def __init__(
        self,
        type: Type[np.int64 | str | bool | float | None | datetime | list],
        *,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        from_column: Optional[str | tuple[str, ...]] = None,
        to_columns: Optional[list[str]] = None,
        post_validated: bool = False,
        **kwargs: Unpack[FieldKwargs],
    ):
        if type == int and null:
            type = np.int64

        self.type = type
        self.field_name = field_name
        self.null = null
        self.replace_values = replace_values
        self.filters = filters
        self.default = kwargs.get("default", None)
        self.required = "default" not in kwargs
        self.post_validated = post_validated
        self.fill_none = []
        # self.group = kwargs.
        self.groups: Optional[tuple[str, ...]] = kwargs.get("groups", None)

        # Fix from_column to a list that can be scanned for existing column
        if isinstance(from_column, str):
            from_column = (from_column,)

        self._from_column: Optional[tuple[str, ...]] = from_column

        self._to_columns = to_columns

        if not self.required and self.default == None and not self.null:
            raise ValueError("Must set null to True if default is None.")

        self.cache = cache

    @property
    def from_column(self) -> tuple[str, ...]:
        return self._from_column or (self.field_name,)

    @property
    def to_columns(self) -> list[str]:
        return self._to_columns or [self.field_name]

    def bind(self, field_name: str):
        self.field_name = self.field_name or field_name

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        try:
            # If data comes from a different column, rename the column if it exists
            if self._from_column:
                column_found = False

                for from_column in self.from_column:
                    if from_column not in dataframe:
                        continue
                    # raise Exception(
                    #     f"{self.field_name} refers to a missing column: {self._from_column}"
                    # )
                    column_found = True

                    # adds a new column using the from column for each to column
                    for to_column in self.to_columns:
                        dataframe.loc[:, [to_column]] = dataframe[from_column]

                if not column_found:
                    raise Exception(
                        f"Cannot resolve column {self.field_name}. None of the source columns {self._from_column} were found in the source dataframe with columns {dataframe.columns}."
                    )

            # TODO: I don't think we need this check
            for column in self.to_columns:
                if column not in dataframe.columns:
                    raise Exception(f"Column {column} does not exist in the dataframe.")

            # replaces values according to dictionary input for each output column
            if self.replace_values:
                for field_name in self.to_columns:
                    dataframe = dataframe.replace({field_name: self.replace_values})

            # drops nulls in each output column
            if not self.null:
                dataframe = dataframe.dropna(subset=self.to_columns)

            # sets the type for each output column
            if self.type in [str, int, float, object, "category"]:
                dataframe = dataframe.astype(
                    {column: self.type for column in self.to_columns}
                )

            # filters the dataframe using the provided filters for each output column
            if self.filters:
                for field_name in self.to_columns:
                    dataframe = filter_dataframe(
                        dataframe=dataframe,
                        filters=[
                            lambda dataset: filter(dataset[field_name])
                            for filter in self.filters
                        ],
                    )

        except Exception as e:
            if self.required:
                raise e

            func = lambda x: (
                self.type(self.default()) if callable(self.default) else self.default  # type: ignore
            )

            dataframe[self.field_name] = dataframe.iloc[:, 0].apply(func)  # type: ignore

        return dataframe


class CharField(BaseField[str]):

    def __init__(
        self,
        *,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        from_column: Optional[str | tuple[str, ...]] = None,
        to_columns: Optional[list[str]] = None,
        post_validated: bool = False,
        **kwargs: Unpack[FieldKwargs],
    ):
        super().__init__(
            str,
            null=null,
            replace_values=replace_values,
            filters=filters,
            cache=cache,
            field_name=field_name,
            from_column=from_column,
            to_columns=to_columns,
            post_validated=post_validated,
            **kwargs,
        )


class IntegerField(BaseField[int]):

    def __init__(
        self,
        *,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        from_column: Optional[str | tuple[str, ...]] = None,
        to_columns: Optional[list[str]] = None,
        post_validated: bool = False,
        **kwargs: Unpack[FieldKwargs],
    ):
        super().__init__(
            type=np.int64,
            null=null,
            replace_values=replace_values,
            filters=filters,
            cache=cache,
            field_name=field_name,
            from_column=from_column,
            to_columns=to_columns,
            post_validated=post_validated,
            **kwargs,
        )

    # def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:
    #     for field_name in self.to_columns:
    #         dataframe = dataframe


class FloatField(BaseField[float]):

    def __init__(
        self,
        *,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        from_column: Optional[str | tuple[str, ...]] = None,
        to_columns: Optional[list[str]] = None,
        post_validated: bool = False,
        **kwargs: Unpack[FieldKwargs],
    ):
        super().__init__(
            type=float,
            null=null,
            replace_values=replace_values,
            filters=filters,
            cache=cache,
            field_name=field_name,
            from_column=from_column,
            to_columns=to_columns,
            post_validated=post_validated,
            **kwargs,
        )


class BooleanField(BaseField[bool]):

    def __init__(
        self,
        *,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        from_column: Optional[str | tuple[str, ...]] = None,
        to_columns: Optional[list[str]] = None,
        post_validated: bool = False,
        **kwargs: Unpack[FieldKwargs],
    ):
        super().__init__(
            type=bool,
            null=null,
            replace_values=replace_values,
            filters=filters,
            cache=cache,
            field_name=field_name,
            from_column=from_column,
            to_columns=to_columns,
            post_validated=post_validated,
            **kwargs,
        )


class ListField(BaseField[list[T]]):
    def __init__(
        self,
        type: Type[np.int64 | str | bool | float | None | datetime],
        *,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        from_column: Optional[str | tuple[str, ...]] = None,
        to_columns: Optional[list[str]] = None,
        post_validated: bool = False,
        **kwargs: Unpack[FieldKwargs],
    ):
        super().__init__(
            type=list[type],
            null=null,
            replace_values=replace_values,
            filters=filters,
            cache=cache,
            field_name=field_name,
            from_column=from_column,
            to_columns=to_columns,
            post_validated=post_validated,
            **kwargs,
        )


class DatetimeField(BaseField[datetime]):

    def __init__(
        self,
        format: str = "%Y/%m/%d",
        *,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        from_column: Optional[str | tuple[str, ...]] = None,
        to_columns: Optional[list[str]] = None,
        post_validated: bool = False,
        **kwargs: Unpack[FieldKwargs],
    ):
        super().__init__(
            type=datetime,
            null=null,
            replace_values=replace_values,
            filters=filters,
            cache=cache,
            field_name=field_name,
            from_column=from_column,
            to_columns=to_columns,
            post_validated=post_validated,
            **kwargs,
        )

        self.format = format

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        column_found = False
        for column in self.from_column:

            if column not in dataframe.columns:
                continue

            column_found = True

            dataframe[self.field_name] = pd.to_datetime(
                dataframe[column], format=self.format
            )

        if not column_found:
            raise Exception(
                f"Cannot resolve column {self.field_name}. None of the source columns {self.from_column} were found in the source dataframe."
            )

        return super().execute(dataframe)


class StaticField(BaseField[str]):
    def __init__(
        self,
        type: Type[np.int64 | str | bool | float | None | datetime],
        *,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        from_column: Optional[str | tuple[str, ...]] = None,
        to_columns: Optional[list[str]] = None,
        post_validated: bool = False,
        **kwargs: Unpack[FieldKwargs],
    ):
        super().__init__(
            type,
            null=null,
            replace_values=replace_values,
            filters=filters,
            cache=cache,
            field_name=field_name,
            from_column=from_column,
            to_columns=to_columns,
            post_validated=post_validated,
            **kwargs,
        )


class TransformationField(BaseField[Generic[T]]):

    def __init__(
        self,
        type: Type[np.int64 | str | bool | float | None | datetime],
        function: Callable[..., pd.Series] | Callable[..., Any],
        from_columns: Optional[list[str]] = None,
        *,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        to_columns: Optional[list[str]] = None,
        post_validated: bool = False,
        **kwargs: Unpack[FieldKwargs],
    ):
        super().__init__(
            type=type,
            to_columns=to_columns,
            null=null,
            replace_values=replace_values,
            filters=filters,
            cache=cache,
            field_name=field_name,
            post_validated=post_validated,
            **kwargs,
        )

        self._from_columns = from_columns
        self._to_columns = to_columns

        self.function = function

    @property
    def from_columns(self) -> list[str]:
        return self._from_columns or [self.field_name]

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        for column in self.from_columns:
            if column not in dataframe.columns:
                if self.required:
                    raise ColumnDoesNotExist(column, dataframe.columns)

                func = lambda x: (
                    self.type(self.default()) if callable(self.default) else self.default  # type: ignore
                )

                dataframe[self.field_name] = dataframe.iloc[:, 0].apply(func)  # type: ignore

                return dataframe

        from_columns = (
            self.from_columns[0] if len(self.from_columns) == 1 else self.from_columns
        )
        to_columns = (
            self.to_columns[0] if len(self.to_columns) == 1 else self.to_columns
        )

        # Account for nan values to allow the function to do its work.
        # func = lambda val: safe_func(self.function, val)
        try:
            if type(from_columns) == list:
                dataframe[to_columns] = dataframe[from_columns].apply(
                    safe_func(self.function), axis=1
                )
            else:
                # TODO: fix fragmentation
                dataframe[to_columns] = dataframe[from_columns].apply(
                    safe_func(self.function)
                )
        except Exception as e:
            raise Exception(
                f"Error applying `{self.function.__name__}` to columns `{self.from_columns}` for field `{self.field_name}`: {e}"
            )

        return super().execute(dataframe)


def safe_func(func: Callable[..., Any]):
    """
    A wrapper for a function that handles nan's before applying the function.
    """

    def inner(val):
        if isinstance(val, float) and np.isnan(val):
            return val

        return func(val)

    return inner


class AugmentationField(BaseField[Generic[T]]):

    def __init__(
        self,
        type: Type[np.int64 | str | bool | float | None | datetime],
        function: Callable[[pd.DataFrame], pd.Series | pd.DataFrame],
        to_columns: Optional[list[str]] = None,
        *,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        from_column: Optional[str | tuple[str, ...]] = None,
        post_validated: bool = False,
        **kwargs: Unpack[FieldKwargs],
    ):
        super().__init__(
            type=type,
            to_columns=to_columns,
            null=null,
            replace_values=replace_values,
            filters=filters,
            cache=cache,
            field_name=field_name,
            from_column=from_column,
            post_validated=post_validated,
            **kwargs,
        )
        self.function = function

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:

        result = self.function(dataframe)

        # TODO: Does this make sense?
        if isinstance(result, pd.DataFrame):
            new_data = result.to_dict(orient="list")

            for key, value in new_data.items():
                dataframe[key] = value
        else:
            if len(self.to_columns) == 1:
                dataframe[self.to_columns[0]] = result
            else:
                dataframe[self.to_columns] = result

        return super().execute(dataframe)
