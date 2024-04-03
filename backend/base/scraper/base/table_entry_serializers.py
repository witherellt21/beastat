import traceback
from datetime import datetime
from typing import Any, Callable, Generic, NotRequired, Optional, Type, TypeVar, Unpack

import pandas as pd
from base.util.dataset_helpers import filter_dataframe
from base.util.pydantic_validator import PydanticValidatorMixin
from pandera.typing import Series
from typing_extensions import TypedDict


def convert_minutes_to_float(time: str) -> float:
    if not isinstance(time, str):
        return time

    try:
        minutes, seconds = time.split(":")
        result = int(minutes) + round(int(seconds) / 60, ndigits=1)
        return result
    except Exception as e:
        print(time)
        print(time.split(":"))
        raise e


T = TypeVar("T")


class FieldKwargs(TypedDict):
    default: NotRequired[Any]


class BaseField(Generic[T]):

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
        **kwargs: Unpack[FieldKwargs],
    ):
        self.type = type
        self.field_name = field_name

        self.null = null
        self.replace_values = replace_values
        self.filters = filters
        self.default = kwargs.get("default", None)
        self.required = "default" not in kwargs

        self._from_column = from_column

        if not self.required and self.default == None and not self.null:
            raise ValueError("Must set null to True if default is None.")

        self.cache = cache

    @property
    def from_column(self):
        return self._from_column or self.field_name

    def bind(self, field_name: str):
        self.field_name = self.field_name or field_name

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        try:
            if not self.required:
                dataframe[self.field_name] = (
                    self.default() if callable(self.default) else self.default
                )

            if self.replace_values:
                dataframe = dataframe.replace({self.field_name: self.replace_values})

            if not self.null:
                dataframe = dataframe.dropna(subset=[self.field_name])

            if self.type in [str, int, float, object, "category"]:
                dataframe[self.field_name] = dataframe[self.field_name].astype(
                    self.type
                )

            if self.filters:
                dataframe = filter_dataframe(
                    dataframe=dataframe,
                    filters=[
                        lambda dataset: filter(dataset[self.field_name])
                        for filter in self.filters
                    ],
                )

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
        function: Callable[[pd.DataFrame], pd.Series],
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
        dataframe[self.field_name] = self.function(dataframe)

        return super().execute(dataframe)


# required fields are fields that cant be null
# transformation fields require a transformation then can be validated using their inner type
#
# from peewee import Model


class BaseTableEntrySerializer(PydanticValidatorMixin):

    def __init__(self):
        """
        Sets up store of field types.
        """
        self.__datetime_fields__: dict[str, str] = {}
        self.__required_fields__: dict[str, Type] = {}
        self.__non_required_fields__: dict[str, BaseField] = {}
        self.__nullable_fields__: dict[str, Type] = {}
        self.__non_nullable_fields__: dict[str, Type] = {}
        self.__transformations__: dict[str, TransformationField] = {}
        self.__column_types__: dict[str, Type] = {}
        self.__replace_values__: dict[str, Type] = {}
        self.__rename_columns__: dict[str, str] = {}
        self.__html_save_fields__: dict[str, str] = {}
        self.__query_arg_fields__: dict[str, str] = {}

        self.__filters__: list[Callable[[pd.DataFrame], pd.Series[bool]]] = []

        for field_name, field in self.__class__.get_fields().items():

            field.bind(field_name)

            # Nullability of field
            if not field.null:
                self.__non_nullable_fields__[field_name] = field.type
            else:
                self.__nullable_fields__[field_name] = field.type

            # Whether field should be saved
            if not field.cache:
                continue

            # Whether the field is required to be provided, or if it has default
            if field.required:
                self.__required_fields__[field_name] = field.type
            else:
                self.__non_required_fields__[field_name] = field

            # If the field is a Datetime type
            if isinstance(field, DatetimeField):
                self.__datetime_fields__[field_name] = field.format
                continue

            # If the field is a transformation
            if isinstance(field, TransformationField):
                self.__transformations__[field_name] = field

            # If the field is pulled from HTML
            if isinstance(field, HTMLSaveField):
                self.__html_save_fields__[field.from_column] = field_name

            # If the field is a rename of an existing field
            if isinstance(field, RenameField):
                self.__rename_columns__[field_name] = field.from_column

            if isinstance(field, QueryArgField):
                self.__query_arg_fields__[field_name] = field.from_column

            # If the field has filters
            if field.filters:
                self.__filters__.extend(
                    lambda dataset: filter(dataset[field_name])
                    for filter in field.filters
                )

            # Add all fields that are being cached to the column types, except datetime
            self.__column_types__[field_name] = field.type

    @property
    def datetime_fields(self):
        return self.__datetime_fields__

    @property
    def required_fields(self):
        return self.__required_fields__

    @property
    def non_required_fields(self):
        return self.__non_required_fields__

    @property
    def nullable_fields(self):
        return self.__nullable_fields__

    @property
    def non_nullable_fields(self):
        return self.__non_nullable_fields__

    @property
    def transformations(self):
        return self.__transformations__

    @property
    def filters(self):
        return self.__filters__

    @property
    def html_save_fields(self):
        return self.__html_save_fields__

    @property
    def rename_columns(self):
        return self.__rename_columns__

    @property
    def replace(self):
        return self.__replace_values__

    @property
    def query_arg_fields(self):
        return self.__query_arg_fields__

    @classmethod
    def get_fields(cls) -> dict[str, BaseField]:
        return {
            key: value
            for key, value in vars(cls).items()
            if isinstance(value, BaseField)
        }

    @classmethod
    def get_required_fields(cls):
        required = []
        for field_name, field in cls.get_fields().items():
            if not field.null:
                required.append(field_name)

        return required

    @classmethod
    def get_non_required_fields(cls):
        non_required = []
        for field_name, field in cls.get_fields().items():
            if field.null:
                non_required.append(field_name)

        return non_required

    @classmethod
    def get_transformation_fields(cls):
        pass

    @classmethod
    def get_datetime_fields(cls):
        not_required = []
        for field, annotation in cls.__annotations__.items():
            if hasattr(annotation, "__args__") and type(None) in annotation.__args__:
                not_required.append(field)

        return not_required


if __name__ == "__main__":
    fields = BaseTableEntrySerializer.get_fields()
    fields = BaseTableEntrySerializer.get_required_fields()
