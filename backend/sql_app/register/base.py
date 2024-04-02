import time
import peewee
import logging

from datetime import datetime
from playhouse.shortcuts import model_to_dict
from pydantic import BaseModel as BaseSerializer
from typing import Any
from typing import Literal
from typing import Optional
from typing import overload
from typing import Type
from sql_app.models.base import BaseModel

import pandas as pd

from typing import TypeVar

# Serializer = TypeVar("Serializer", bound="BaseSerializer")
from abc import abstractmethod


logger = logging.getLogger("main")


class BaseTable:
    MODEL_CLASS: Type[BaseModel]
    SERIALIZER_CLASS: Type[BaseSerializer]
    UPDATE_SERIALIZER_CLASS: Type[BaseSerializer]
    TABLE_ENTRY_SERIALIZER_CLASS: Type[BaseSerializer]
    READ_SERIALIZER_CLASS: Optional[Type[BaseSerializer]] = None
    PKS: list[str] = ["id"]

    DEPENDENCIES: list[Type[BaseModel]] = []

    def __init__(self, db: peewee.Database):
        if not self.model_class:
            raise Exception("Must specify the MODEL_CLASS class attribute.")
        if not self.serializer_class:
            raise Exception("Must specify the SERIALIZER_CLASS class attribute.")

        self.db = db

        # self.model_class.Meta.db_table =
        # if self.db:
        if not self.db == None:
            print(f"Creating table for {self.__class__.__name__}.")
            dependencies = self.__class__.DEPENDENCIES
            self.db.create_tables([*dependencies, self.model_class])
        else:
            raise Exception("DB not connect. Cannot perform operations on the table.")

    @property
    def serializer_class(self) -> Type[BaseSerializer]:
        return self.__class__.SERIALIZER_CLASS

    @property
    def table_entry_serializer_class(self) -> Type[BaseSerializer]:
        return self.__class__.TABLE_ENTRY_SERIALIZER_CLASS

    @property
    def update_serializer_class(self) -> Type[BaseSerializer]:
        return self.__class__.UPDATE_SERIALIZER_CLASS

    @property
    def read_serializer_class(self) -> Type[BaseSerializer]:
        return self.__class__.READ_SERIALIZER_CLASS or self.serializer_class

    @property
    def model_class(self) -> Type[BaseModel]:
        return self.__class__.MODEL_CLASS

    @overload
    def get_all_records(self, *, as_df: Literal[True]) -> pd.DataFrame: ...

    @overload
    def get_all_records(self, *, as_df: Literal[False]) -> list[BaseSerializer]: ...

    @overload
    def get_all_records(
        self, *, as_df: Literal[True], confuse: bool
    ) -> pd.DataFrame: ...

    @overload
    def get_all_records(
        self, *, as_df: Literal[True], confuse: bool, limit: int
    ) -> pd.DataFrame: ...

    @overload
    def get_all_records(self) -> list[BaseSerializer]: ...

    @overload
    def filter_records(self, *, query: dict, as_df: Literal[True]) -> pd.DataFrame: ...

    @overload
    def filter_records(
        self, *, query: dict, as_df: Literal[False]
    ) -> list[BaseSerializer]: ...

    @overload
    def filter_records(
        self, *, query: dict, as_df: Literal[True], recurse=False
    ) -> pd.DataFrame: ...

    @overload
    def filter_records(self, *, query: dict) -> list[BaseSerializer]: ...

    def get_all_records(
        self, *, as_df=False, confuse: bool = False, limit: Optional[int] = None
    ) -> list[BaseSerializer] | pd.DataFrame:
        records = []

        query = self.model_class.select()

        if confuse:
            query = query.order_by(peewee.fn.Random())

        if limit is not None:
            query = query.limit(limit)

        for record in query:
            if as_df:
                records.append(model_to_dict(record, recurse=False))
            else:
                serialized = self.read_serializer_class(**model_to_dict(record))
                records.append(serialized)

        return pd.DataFrame(records) if as_df else records

    def get_record(self, query: dict = {}) -> Optional[BaseSerializer]:
        try:
            db_row = self.model_class.get(
                *[
                    getattr(self.model_class, field) == value
                    for field, value in query.items()
                ]
            )

            return self.read_serializer_class(**model_to_dict(db_row))

        except peewee.DoesNotExist as e:
            return None

    def get_or_create(self, *, data: dict[str, str] = {}) -> Optional[BaseSerializer]:
        validated_data: BaseSerializer = self.serializer_class(**data)

        try:
            model = self.model_class.get(**validated_data.model_dump())
        except peewee.DoesNotExist:
            print(validated_data)
            model, created = self.model_class.get_or_create(
                **validated_data.model_dump()
            )

        if model:
            return self.read_serializer_class(**model_to_dict(model))
        else:
            return None

    def filter_records(
        self, *, query: dict = {}, as_df: bool = False, recurse: bool = True
    ) -> list[BaseSerializer] | pd.DataFrame:
        """
        Return all rows matching the search query.
        """
        # start = time.time()
        records: list[BaseModel] = self.model_class.select().where(
            *[getattr(self.model_class, key) == value for key, value in query.items()]
        )
        # print(time.time() - start)

        # Serialize rows and convert to desired output type
        serialized_objects = []
        for record in records:
            if as_df:
                serialized_objects.append(model_to_dict(record, recurse=False))
            else:
                serialized = self.read_serializer_class(
                    **model_to_dict(record, recurse=recurse)
                )
                serialized_objects.append(
                    serialized.model_dump() if as_df else serialized
                )

        return pd.DataFrame(serialized_objects) if as_df else serialized_objects

    def filter_records_by_literal(
        self,
        *,
        query: dict = {},
        as_df: bool = False,
    ) -> list[BaseSerializer] | pd.DataFrame:
        """
        Return all rows matching the search query.
        """
        # start = time.time()
        records: list[BaseModel] = self.model_class.select().where(
            *[getattr(self.model_class, key) == value for key, value in query.items()]
        )
        # print(time.time() - start)

        # Serialize rows and convert to desired output type
        serialized_objects = []
        for record in records:
            # if as_df:
            # serialized_objects.append(model_to_dict(record, recurse=False))
            # else:
            serialized = self.read_serializer_class(**model_to_dict(record))
            serialized_objects.append(serialized.model_dump() if as_df else serialized)

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

        existing_row: Optional[BaseModel]
        try:
            existing_row = self.model_class.get(
                *[
                    getattr(self.model_class, id_field) == data.get(id_field)
                    for id_field in id_fields
                ]
            )

        except peewee.DoesNotExist as e:
            existing_row = None

        if existing_row:
            return self.update_record(
                data={**data, "id": existing_row.id}, id_fields=id_fields  # type: ignore
            )

        else:
            return self.insert_record(data=data)

    def delete_record(self, **kwargs) -> BaseModel:
        query = kwargs.get("query", self.__class__.PKS)

        delete_query = self.model_class.delete().where(
            *[
                getattr(self.model_class, key) == query.get(key)
                for key, value in query.items()
            ]
        )

        return delete_query.execute()

    def get_column_values(self, *, column: str) -> "list[Any]":
        values = [value[column] for value in self.model_class.select().dicts()]
        return values
