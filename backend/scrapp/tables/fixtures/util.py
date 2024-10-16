import json
from typing import Any

from pydantic import BaseModel
from scrapp.tables.table_schema import schema


class FixtureRecord(BaseModel):
    model: str
    fields: dict[str, Any]


def load_fixture(file_path: str) -> None:
    print("Loading fixture: {}".format(file_path))

    with open(file_path, "r") as file:
        data = json.load(file)

        if isinstance(data, list):
            for record in data:
                validated_data = FixtureRecord(**record)

                table = schema.table(validated_data.model)

                table.update_or_insert_record(data=validated_data.fields)
