from typing import Any, Callable, Type

import numpy as np
import pandas as pd
from fastapi import dependencies
from lib.pydantic_validator import PydanticValidatorMixin
from pydantic import conint
from scrapp.core.dataframes.util import safe_concat, safe_set_column

from .fields import (
    BaseField,
    DatetimeField,
    Dependency,
    HTMLSaveField,
    StaticField,
    TransformationField,
)


class BaseDataframeValidator(PydanticValidatorMixin):
    """
    Base class for a serializing an HTMLTable into savable types.
    """

    __fields__: dict[str, BaseField] = {}
    __field_set__: set[str] = set()
    __post_validated_fields__: dict[str, BaseField] = {}
    __post_validation_set__: set[str] = set()
    # __dependencies__: list[BaseField] =

    NAN_VALUES: list[str] = []
    MULTI_INDEX_MAPPER: Callable[[tuple[str, str]], str] = "_".join

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.__fields__ = cls.__get_fields()
        cls.__field_set__ = set(cls.__fields__.keys())

        for field_name, field in cls.__fields__.items():
            # if field.dependencies:
            # for dependency in field.dependencies:
            # cls.__dependencies__[field_name] =

            # cls.__post_validated_fields__[field_name] = field

            if field.post_validated:
                cls.__post_validated_fields__[field_name] = field
                cls.__post_validation_set__.add(field_name)

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
        self.__static_fields__: dict[str, str] = {}
        # self.__dependencies__: dict[str, str] = {}
        self.__filters__: list[Callable[[pd.DataFrame], pd.Series[bool]]] = []

        self.multi_index_mapper = self.__class__.MULTI_INDEX_MAPPER
        self.nan_values = self.__class__.NAN_VALUES

        for field_name, field in self.__class__.__fields__.items():

            field.bind(field_name)

            # Nullability of field
            if not field.null:
                self.__non_nullable_fields__[field_name] = field.type
            else:
                self.__nullable_fields__[field_name] = field.type

            # Whether field should be saved
            if not field.cache:
                continue

            # if field.depends_on:
            #     self.dependencies[field_name] = field.depends_on

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
            # if isinstance(field, HTMLSaveField):
            #     self.__html_save_fields__[field.from_column] = field_name

            # if isinstance(field, StaticField):
            #     self.__static_fields__[field_name] = field.from_column

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
    def static_fields(self):
        return self.__static_fields__

    @property
    def fields(self) -> dict[str, BaseField]:
        return self.__fields__

    @property
    def post_validated_fields(self) -> dict[str, BaseField]:
        return self.__post_validated_fields__

    @classmethod
    def __get_fields(cls) -> dict[str, BaseField]:
        return {
            key: value
            for key, value in vars(cls).items()
            if isinstance(value, BaseField)
        }

    @classmethod
    def get_fields(cls) -> set[str]:
        return cls.__field_set__

    @classmethod
    def get_required_fields(cls):
        required = []
        for field_name, field in cls.__get_fields().items():
            if not field.null:
                required.append(field_name)

        return required

    @classmethod
    def get_post_validated_fields(cls):
        return cls.__post_validation_set__

    @classmethod
    def get_non_required_fields(cls):
        non_required = []
        for field_name, field in cls.__get_fields().items():
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

    def post_validate(self, df: pd.DataFrame):
        for name, field in self.post_validated_fields.items():
            try:
                df = field.execute(df)
            except Exception as e:
                raise Exception(f"Error executing field `{name}`: {e}.")

        return df

    def validate(self, df: pd.DataFrame, extra_columns: dict[str, Any]):
        # Add metadata from the extra_columns attribute
        for column_name, value in extra_columns.items():
            df = safe_set_column(df, column_name, value)

        # TODO: ADD support for multi-indexing
        # if the columns are multindexed, flatten them
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.map("_".join).str.strip("_")

        df = df.replace(self.nan_values, np.nan, regex=True)

        for name, field in self.fields.items():
            if field.post_validated:
                continue

            try:
                df = field.execute(df)
            except Exception as e:
                raise Exception(f"Error executing field `{name}`: {e}.")

        return df[
            [col for col, field in self.fields.items() if not field.post_validated]
        ]


if __name__ == "__main__":
    fields = BaseDataframeValidator.__get_fields()
    fields = BaseDataframeValidator.get_required_fields()
