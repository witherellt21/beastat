import traceback
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
    default: NotRequired[Union[str, int, float, Callable[..., str]]]


class BaseField(Generic[T]):
    """
    Base class for a an HTMLTable field.
    """

    def __init__(
        self,
        *,
        type: Type,
        null: bool = False,
        replace_values: dict[Any, Any] = {},
        filters: list[Callable[[Any], Series[bool]]] = [],
        cache: bool = True,
        field_name: str = "",
        from_column: Optional[str] = None,
        to_columns: Optional[str] = None,
        depends_on: Optional[str] = None,
        **kwargs: Unpack[FieldKwargs],
    ):
        self.type = type
        self.field_name = field_name

        self.null = null
        self.replace_values = replace_values
        self.filters = filters
        self.default = kwargs.get("default", None)
        self.required = "default" not in kwargs
        self.depends_on = depends_on

        self._from_column = from_column
        self._to_columns = to_columns

        if not self.required and self.default == None and not self.null:
            raise ValueError("Must set null to True if default is None.")

        self.cache = cache

    @property
    def from_column(self):
        return self._from_column or self.field_name

    @property
    def to_columns(self):
        return self._to_columns or [self.field_name]

    def bind(self, field_name: str):
        self.field_name = self.field_name or field_name

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        try:
            # print(self.field_name, dataframe)

            if self.required:
                for field_name in self.to_columns:
                    if self.replace_values:
                        dataframe = dataframe.replace({field_name: self.replace_values})

                if not self.null:
                    dataframe = dataframe.dropna(subset=self.to_columns)

                # if self.field_name == "winner":
                #     dataframe = dataframe.replace({self.field_name: None})

                if self.type in [str, int, float, object, "category"]:

                    # TODO: REMOVE
                    # if self.field_name != "winner":
                    # print(dataframe)

                    dataframe[self.to_columns] = dataframe[self.to_columns].astype(
                        self.type
                    )

                for field_name in self.to_columns:
                    if self.filters:
                        dataframe = filter_dataframe(
                            dataframe=dataframe,
                            filters=[
                                lambda dataset: filter(dataset[field_name])
                                for filter in self.filters
                            ],
                        )

            else:
                func = lambda x: (
                    self.type(self.default())
                    if callable(self.default)
                    else self.default
                )
                dataframe[self.field_name] = dataframe.iloc[:, 0].apply(func)

            return dataframe
        except Exception as e:
            raise Exception(
                f"Failed getting value for {self.field_name}. {traceback.format_exc()}"
            )


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
        dataframe[self.field_name] = pd.to_datetime(
            dataframe[self.from_column], format=self.format
        )

        return super().execute(dataframe)


class QueryArgField(BaseField[str]):
    def __init__(self, from_column: Optional[str] = None, *args, **kwargs):
        super().__init__(type=str, *args, **kwargs)

        self._from_column = from_column

    @property
    def from_column(self):
        return self._from_column or self.field_name


class HTMLSaveField(BaseField[str]):
    def __init__(self, from_column: str, *args, **kwargs):
        super().__init__(type=str, *args, **kwargs)

        self._from_column = from_column


class RenameField(BaseField[T]):
    def __init__(self, from_column: str, *args, type: Type, **kwargs):
        super().__init__(type=type, *args, **kwargs)

        self._from_column = from_column

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe = dataframe.rename(columns={self.from_column: self.field_name})

        return super().execute(dataframe)


class TransformationField(BaseField[Generic[T]]):

    def __init__(
        self,
        type: Type,
        function: Callable[..., pd.Series] | Callable[..., Any],
        from_columns: Optional[list[str]] = None,
        to_columns: Optional[list[str]] = None,
        **kwargs,
    ):
        super().__init__(type=type, **kwargs)

        self._from_columns = from_columns
        self._to_columns = to_columns

        self.function = function

    @property
    def from_columns(self):
        return self._from_columns or [self.field_name]

    @property
    def to_columns(self):
        return self._to_columns or [self.field_name]

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:

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
                f"Error applying {self.function} to {from_columns} for {self.field_name}: {e}"
            )

        return super().execute(dataframe)


class AugmentationField(BaseField[Generic[T]]):

    def __init__(
        self,
        type: Type,
        function: Callable[[pd.DataFrame], pd.Series | pd.DataFrame],
        from_columns: Optional[list[str]] = None,
        to_columns: Optional[list[str]] = None,
        **kwargs,
    ):
        super().__init__(type=type, **kwargs)

        self._from_columns = from_columns
        self._to_columns = to_columns

        self.function = function

    @property
    def from_columns(self):
        return self._from_columns or [self.field_name]

    @property
    def to_columns(self):
        return self._to_columns or [self.field_name]

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        result = self.function(dataframe)

        if isinstance(result, pd.DataFrame):
            new_data = result.to_dict(orient="list")

            for key, value in new_data.items():
                dataframe[key] = value

        else:
            dataframe[self.to_columns] = result

        return super().execute(dataframe)
