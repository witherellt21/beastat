from typing import Callable, Type

import pandas as pd
from lib.pydantic_validator import PydanticValidatorMixin

from .fields import (
    BaseField,
    DatetimeField,
    HTMLSaveField,
    QueryArgField,
    RenameField,
    TransformationField,
)


class BaseHTMLTableSerializer(PydanticValidatorMixin):
    """
    Base class for a serializing an HTMLTable into savable types.
    """

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
        self.__dependencies__: dict[str, str] = {}

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

            if field.depends_on:
                self.dependencies[field_name] = field.depends_on

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

        # print(self.query_arg_fields)

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

    @property
    def dependencies(self):
        return self.__dependencies__

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
    fields = BaseHTMLTableSerializer.get_fields()
    fields = BaseHTMLTableSerializer.get_required_fields()
