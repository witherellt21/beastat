from playhouse.shortcuts import model_to_dict
from sql_app.register.base import BaseTable
from sql_app.models.game import Game
from sql_app.serializers.game import GameSerializer
from sql_app.database import DB
from typing import Optional, Literal, overload
from datetime import datetime
import uuid
import pandas as pd


class GameTable(BaseTable):
    MODEL_CLASS = Game
    SERIALIZER_CLASS = GameSerializer
    PKS: list[str] = ["date_time", "home", "away"]

    @overload
    def filter_by_datetime(
        self, *, min_datetime: datetime, as_df: Literal[True]
    ) -> pd.DataFrame: ...

    @overload
    def filter_by_datetime(
        self, *, min_datetime: datetime, as_df: Literal[False]
    ) -> list[GameSerializer]: ...

    def insert_record(self, *, data: dict) -> Optional[GameSerializer]:
        """
        Insert a row into the database.
        """
        validated_data: GameSerializer = GameSerializer(
            id=uuid.uuid4(), **data, timestamp=datetime.now()
        )

        result: Game = self.model_class.create(**validated_data.model_dump())

        if result:
            return validated_data
        else:
            return None

    def filter_by_datetime(
        self, *, min_datetime: datetime, as_df: bool = False
    ) -> list[GameSerializer] | pd.DataFrame:
        records = Game.select().where(Game.date_time > min_datetime)

        # Serialize rows and convert to desired output type
        serialized_objects = []
        for record in records:
            if as_df:
                serialized_objects.append(model_to_dict(record, recurse=False))
            else:
                serialized = self.read_serializer_class(**model_to_dict(record))
                serialized_objects.append(serialized)

        return pd.DataFrame(serialized_objects) if as_df else serialized_objects


Games = GameTable(DB)
