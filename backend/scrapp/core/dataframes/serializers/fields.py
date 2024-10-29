from datetime import datetime
from typing import (
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

import pandas as pd
from lib.dataframes import filter_dataframe
from pandera.typing import Series
from typing_extensions import TypedDict

T = TypeVar("T")


class FieldKwargs(TypedDict):
    default: NotRequired[
        Union[str, int, float, None, Callable[..., Union[str, int, float, None]]]
    ]


class Dependency:
    def __init__(self):
        self.dependency = None
        self.__confirmed = False

    def is_confirmed(self):
        return self.__confirmed

    def confirm(self):
        self.__confirmed = True


class BaseField(Generic[T]):
    """
    Base class for a an HTMLTable field.
    """

    def __init__(
        self,
        type: Type,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        from_column: Optional[str | tuple[str]] = None,
        to_columns: Optional[list[str]] = None,
        post_validated: bool = False,
        **kwargs: Unpack[FieldKwargs],
    ):
        self.type = type
        self.field_name = field_name

        self.null = null
        self.replace_values = replace_values
        self.filters = filters
        self.default = kwargs.get("default", None)
        self.required = "default" not in kwargs
        self.post_validated = post_validated
        self.fill_none = []

        # Fix from_column to a list that can be scanned for existing column
        if isinstance(from_column, str):
            from_column = (from_column,)

        self._from_column: Optional[tuple[str]] = from_column

        self._to_columns = to_columns

        if not self.required and self.default == None and not self.null:
            raise ValueError("Must set null to True if default is None.")

        self.cache = cache

    @property
    def from_column(self) -> tuple[str]:
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
                        f"Cannot resolve column {self.field_name}. None of the source columns {self._from_column} were found in the source dataframe."
                    )

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
                self.type(self.default()) if callable(self.default) else self.default
            )

            dataframe[self.field_name] = dataframe.iloc[:, 0].apply(func)

        return dataframe


class CharField(BaseField[str]):

    def __init__(self, *args, **kwargs):
        super().__init__(type=str, *args, **kwargs)


class IntegerField(BaseField[int]):

    def __init__(self, *args, **kwargs):
        super().__init__(type=int, *args, **kwargs)


class FloatField(BaseField[float]):

    def __init__(self, *args, **kwargs):
        super().__init__(type=float, *args, **kwargs)


class ListField(BaseField[list[T]]):
    def __init__(self, type: Type, *args, **kwargs):
        super().__init__(type=list[type], *args, **kwargs)


class DatetimeField(BaseField[datetime]):

    def __init__(self, format: str = "%Y/%m/%d", *args, **kwargs):
        super().__init__(type=datetime, *args, **kwargs)

        self.format = format

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        column_found = False
        for column in self.from_column:

            if column not in dataframe.columns:
                continue

            column_found = True

            dataframe[self.field_name] = pd.to_datetime(
                dataframe[self.from_column], format=self.format
            )

            self._from_column = None

        if not column_found:
            raise Exception(
                f"Cannot resolve column {self.field_name}. None of the source columns {self.from_column} were found in the source dataframe."
            )

        return super().execute(dataframe)


class StaticField(BaseField[str]):
    def __init__(self, from_column: Optional[str] = None, **kwargs):
        super().__init__(str, from_column=from_column, **kwargs)


class TransformationField(BaseField[Generic[T]]):

    def __init__(
        self,
        type: Type,
        function: Callable[..., pd.Series] | Callable[..., Any],
        from_columns: Optional[list[str]] = None,
        to_columns: Optional[list[str]] = None,
        **kwargs,
    ):
        super().__init__(type=type, to_columns=to_columns, **kwargs)

        self._from_columns = from_columns
        self._to_columns = to_columns

        self.function = function

    @property
    def from_columns(self) -> list[str]:
        return self._from_columns or [self.field_name]

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        for column in self.from_columns:
            if column not in dataframe.columns:
                raise Exception(
                    f"{self.field_name} refers to a missing column: {column}."
                )
        from_columns = (
            self.from_columns[0] if len(self.from_columns) == 1 else self.from_columns
        )
        to_columns = (
            self.to_columns[0] if len(self.to_columns) == 1 else self.to_columns
        )

        try:
            if type(from_columns) == list:
                dataframe[to_columns] = dataframe[from_columns].apply(
                    self.function, axis=1
                )
            else:
                dataframe[to_columns] = dataframe[from_columns].apply(self.function)
        except Exception as e:
            raise Exception(
                f"Error applying {self.function} to columns `{self.from_columns}` for field `{self.field_name}`: {e}"
            )

        return super().execute(dataframe)


class AugmentationField(BaseField[Generic[T]]):

    def __init__(
        self,
        type: Type,
        function: Callable[[pd.DataFrame], pd.Series | pd.DataFrame],
        to_columns: Optional[list[str]] = None,
        **kwargs,
    ):
        super().__init__(type=type, to_columns=to_columns, **kwargs)
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
