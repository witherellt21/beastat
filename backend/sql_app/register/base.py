import peewee

from datetime import datetime
from playhouse.shortcuts import model_to_dict
from pydantic import BaseModel as BaseSerializer
from typing import Any
from typing import Optional
from sql_app.models.base import BaseModel

import pandas as pd


class BaseTable:

    MODEL_CLASS: BaseModel = None
    SERIALIZER_CLASS = None
    READ_SERIALIZER_CLASS = None
    PKS: str = ["id"]

    def __init__(self, db: peewee.Database):
        if not self.model_class:
            raise Exception("Must specify the MODEL_CLASS class attribute.")
        if not self.serializer_class:
            raise Exception("Must specify the SERIALIZER_CLASS class attribute.")

        self.db = db
        self.db.create_tables([self.model_class])

    @property
    def serializer_class(self) -> BaseSerializer:
        return self.__class__.SERIALIZER_CLASS

    @property
    def read_serializer_class(self) -> BaseSerializer:
        return self.__class__.READ_SERIALIZER_CLASS or self.serializer_class

    @property
    def model_class(self) -> BaseModel:
        return self.__class__.MODEL_CLASS

    def get_all_records(self, *, as_df=False) -> "list[BaseSerializer] | pd.DataFrame":
        records = []
        for record in self.model_class.select():
            serialized = self.read_serializer_class(**model_to_dict(record))
            records.append(serialized.dict() if as_df else serialized)

        return pd.DataFrame(records) if as_df else records

    def get_record(self, query: dict = {}) -> Optional[BaseSerializer]:
        try:
            db_row: self.model_class = self.model_class.get(
                *[
                    getattr(self.model_class, field) == value
                    for field, value in query.items()
                ]
            )

            return self.serializer_class(**model_to_dict(db_row))

        except peewee.DoesNotExist as e:
            return None

    def filter_records(
        self,
        *,
        query: dict = {},
        as_df: bool = False,
    ) -> "list[BaseSerializer] | pd.DataFrame":
        """
        Return all rows matching the search query.
        """
        records: list[BaseModel] = self.model_class.select().where(
            *[getattr(self.model_class, key) == value for key, value in query.items()]
        )

        # Serialize rows and convert to desired output type
        serialized_objects = []
        for record in records:
            serialized = self.serializer_class(**model_to_dict(record))
            serialized_objects.append(serialized.dict() if as_df else serialized)

        return pd.DataFrame(serialized_objects) if as_df else serialized_objects

    def insert_record(self, *, data: dict) -> Optional[BaseSerializer]:
        """
        Insert a row into the database.
        """
        validated_data: BaseSerializer = self.serializer_class(
            **data, timestamp=datetime.now()
        )

        result: BaseModel = self.model_class.create(**validated_data.model_dump())

        if result:
            return validated_data
        else:
            return None

    def update_record(self, *, data: dict, **kwargs) -> Optional[BaseSerializer]:
        """
        Update a record in the database.
        """
        id_fields = kwargs.get("id_fields", self.__class__.PKS)

        validated_data: BaseSerializer = self.serializer_class(
            **data, timestamp=datetime.now()
        )

        result: Optional[BaseModel] = (
            self.model_class.update(**validated_data.model_dump())
            .where(
                *[
                    getattr(self.model_class, id_field) == data.get(id_field)
                    for id_field in id_fields
                ]
            )
            .execute()
        )

        if result:
            return validated_data
        else:
            return None

    def update_or_insert_record(
        self, *, data: dict, **kwargs
    ) -> Optional[BaseSerializer]:
        id_fields = kwargs.get("id_fields", self.__class__.PKS)

        try:
            existing_row: BaseModel = self.model_class.get(
                *[
                    getattr(self.model_class, id_field) == data.get(id_field)
                    for id_field in id_fields
                ]
            )

        except peewee.DoesNotExist as e:
            existing_row = None

        if existing_row:
            return self.update_record(data=data, id_fields=id_fields)

        else:
            return self.insert_record(data=data)

    def delete_record(self, **kwargs) -> BaseModel:
        query = kwargs.get("query", self.__class__.PKS)

        try:
            delete_query = self.model_class.delete().where(
                *[
                    getattr(self.model_class, key) == query.get(key)
                    for key, value in query.items()
                ]
            )

            return delete_query.execute()
        except peewee.DoesNotExist as e:
            print(
                f"Could not delete record for table {self.model_class} with query {query}."
            )

    def get_column_values(self, *, column: str) -> "list[Any]":
        values = [value[column] for value in self.model_class.select().dicts()]
        return values
