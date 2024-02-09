import peewee

from datetime import datetime
from playhouse.shortcuts import model_to_dict
from pydantic import BaseModel as BaseSerializer
from typing import Any
from typing import Optional
from sql_app.models.base import BaseModel


class BaseTable:

    MODEL_CLASS: BaseModel = None
    SERIALIZER_CLASS = None
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
    def model_class(self) -> BaseModel:
        return self.__class__.MODEL_CLASS

    def get_all_records(self) -> "list[BaseModel]":
        records = []
        for record in self.model_class.select():
            records.append(self.serializer_class(**model_to_dict(record)).dict())

        return records

    def get_record(self, *, id: str, **kwargs) -> BaseModel:
        id_field = kwargs.get("id_field", self.__class__.PKS[0])

        try:
            db_row: self.model_class = self.model_class.get(
                getattr(self.model_class, id_field) == id
            )
            return_data: dict[str:Any] = model_to_dict(db_row)
            # return_data["colleges"] = [college.name for college in player_info.colleges]
            return self.serializer_class(**return_data)
        except Exception as e:
            print(e)
            return None

    def insert_record(self, *, data: dict) -> Optional[BaseSerializer]:
        """
        Insert a row into the database.
        """
        validated_data: BaseSerializer = self.serializer_class(
            **data, timestamp=datetime.now()
        )

        entry = validated_data.model_dump()
        result = self.model_class.create(**entry)

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

        entry: dict = validated_data.model_dump()

        result: Optional[BaseModel] = (
            self.model_class.update(**entry)
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

    def update_or_insert_record(self, *, data: dict, **kwargs) -> BaseSerializer:
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

    def get_column_values(self, *, column: str):
        values = [value[column] for value in self.model_class.select().dicts()]
        return values
