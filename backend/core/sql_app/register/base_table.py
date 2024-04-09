import logging
from datetime import datetime
from typing import Any, Literal, Optional, Type, Union, overload

import pandas as pd
import peewee
from pandas._typing import Dtype
from peewee import Model
from playhouse.shortcuts import model_to_dict
from pydantic import BaseModel as BaseSerializer
from pydantic import GetCoreSchemaHandler
from pydantic.fields import FieldInfo
from pydantic_core import CoreSchema, core_schema

logger = logging.getLogger("main")


class AdvancedQuery(BaseSerializer):
    greater_than: dict[str, Union[int, float, datetime]] = {}
    less_than: dict[str, Union[int, float, datetime]] = {}
    equal_to: dict[str, Any] = {}
    in_: dict[str, list[Union[str, int, float, datetime]]] = {}


# def sort_dependencies(table: "Type[BaseTable]", models: ):
#     print(f"Creating table for {table.__name__}.")

#     dependencies = table.DEPENDENCIES
#     for dependency in dependencies:
#         sort_dependencies(dependency)

# table.db.create_tables([table.model_class])


class BaseTable:
    MODEL_CLASS: Type[Model]
    SERIALIZER_CLASS: Type[BaseSerializer]
    UPDATE_SERIALIZER_CLASS: Type[BaseSerializer]
    READ_SERIALIZER_CLASS: Optional[Type[BaseSerializer]] = None
    PKS: list[str] = ["id"]

    # DEPENDENCIES: list[Type[Model]] = []
    DEPENDENCIES: list[Type["BaseTable"]] = []

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
            # dependencies = self.__class__.DEPENDENCIES
            # for dependency in dependencies:
            #     dependency(self.db)
            self.db.create_tables([self.model_class])
        else:
            # logger.warning("DB not connected. Cannot perform operations on the table.")
            raise Exception("DB not connected. Cannot perform operations on the table.")
            # pass

    @classmethod
    def validate(cls, __input_value: Any, _: core_schema.ValidationInfo) -> "BaseTable":
        if not isinstance(__input_value, cls):
            raise ValueError(f"Expected BaseTable, received: {type(__input_value)}")
        return __input_value

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        # return core_schema.no_info_after_validator_function(cls, handler(BaseTable))
        return core_schema.with_info_plain_validator_function(cls.validate)

    @property
    def serializer_class(self) -> Type[BaseSerializer]:
        return self.__class__.SERIALIZER_CLASS

    @property
    def update_serializer_class(self) -> Type[BaseSerializer]:
        return self.__class__.UPDATE_SERIALIZER_CLASS

    @property
    def read_serializer_class(self) -> Type[BaseSerializer]:
        return self.__class__.READ_SERIALIZER_CLASS or self.serializer_class

    @property
    def model_class(self) -> Type[Model]:
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

    def get_foreign_relationships(self) -> list[str]:
        # return get_foreign_key_fields(self.model_class)
        foreign_keys = []

        for field_name, field in self.model_class._meta.fields.items():  # type: ignore
            if isinstance(field, peewee.ForeignKeyField):
                foreign_keys.append(field_name)

        return foreign_keys

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
        records: list[Model] = self.model_class.select().where(
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

    def filter_records_advanced(
        self,
        query: Optional[AdvancedQuery] = None,
        columns: list[str] = [],
        confuse: bool = False,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        search = self.model_class.select()

        # print(query.in_.items())

        if query:
            search = search.where(
                *[
                    getattr(self.model_class, key) == value
                    for key, value in query.equal_to.items()
                ],
                *[
                    getattr(self.model_class, key) > value
                    for key, value in query.greater_than.items()
                ],
                *[
                    getattr(self.model_class, key) < value
                    for key, value in query.less_than.items()
                ],
                *[
                    getattr(self.model_class, key) << value
                    for key, value in query.in_.items()
                ],
            )

        if confuse:
            search = search.order_by(peewee.fn.Random())

        if limit is not None:
            search = search.limit(limit)

        rows = []
        for row in search:
            rows.append(model_to_dict(row, recurse=False))

        return pd.DataFrame(rows)

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
        records: list[Model] = self.model_class.select().where(
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

        result: Model = self.model_class.create(**validated_data.model_dump())

        if result:
            return validated_data
        else:
            return None

    def partial_update(self, *, data: dict, **kwargs):
        id_fields = kwargs.get("id_fields", self.__class__.PKS)

        # current = self.get_record(
        #     query={key: value for key, value in data.items() if key in id_fields}
        # )

        # if not current:
        #     raise Exception(f"Record does not exist with primary key in {data}.")

        # print(data)
        # validated_data = current.model_copy(update=data)
        # print(validated_data)

        # existing_row: Optional[BaseModel]
        # try:
        #     existing_row = self.model_class.get(
        #         *[
        #             getattr(self.model_class, id_field) == data.get(id_field)
        #             for id_field in id_fields
        #         ]
        #     )

        # except peewee.DoesNotExist as e:
        #     raise Exception(f"Record does not exist with primary key in {data}.")

        for key, value in data.items():
            self.serializer_class.__pydantic_validator__.validate_assignment(
                self.serializer_class.model_construct(), key, value
            )
        # data = model_to_dict(existing_row)
        # validated_data = self.serializer_class(**model_to_dict(existing_row))
        # validated_data = validated_data.model_copy(update=data)

        result: Optional[Model] = (
            self.model_class.update(**data)
            .where(
                *[
                    getattr(self.model_class, id_field) == data.get(id_field)
                    for id_field in id_fields
                ]
            )
            .execute()
        )

        if result:
            return data
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

        update_dict = validated_data.model_dump()
        update_dict.pop("id")

        # print(data)
        # current = self.get_record(query=data)

        # if not current:
        #     raise Exception(f"Record does not exist with primary key in {data}.")

        # validated_data = current.model_copy(update=data)

        # temporary workaround for partial updates
        # for key, value in data.items():
        #     self.serializer_class.__pydantic_validator__.validate_assignment(
        #         self.serializer_class.model_construct(), key, value
        #     )

        result: Optional[Model] = (
            self.model_class.update(**update_dict)
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

        existing_row: Optional[Model]
        try:
            existing_row = self.model_class.get(
                *[
                    getattr(self.model_class, id_field) == data.get(id_field)
                    for id_field in id_fields
                ]
            )

        except peewee.DoesNotExist as e:
            existing_row = None

        data.pop("timestamp", None)
        if existing_row:
            return self.update_record(
                data={**data, "id": existing_row.id}, id_fields=id_fields  # type: ignore
            )

        else:
            return self.insert_record(data=data)

    def delete_record(self, **kwargs) -> Model:
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

    def count_records(
        self,
        *,
        query: Optional[AdvancedQuery] = None,
    ) -> int:
        """
        Return all rows matching the search query.
        """
        # start = time.time()
        if query:
            count = (
                self.model_class.select()
                .where(
                    *[
                        getattr(self.model_class, key) == value
                        for key, value in query.equal_to.items()
                    ],
                    *[
                        getattr(self.model_class, key) > value
                        for key, value in query.greater_than.items()
                    ],
                    *[
                        getattr(self.model_class, key) < value
                        for key, value in query.less_than.items()
                    ],
                )
                .count()
            )
        else:
            count = self.model_class.select().count()

        # Serialize rows and convert to desired output type
        return count
