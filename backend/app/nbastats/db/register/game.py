from datetime import datetime
from typing import Literal, overload

import pandas as pd
from core.db.tables import BaseTable
from playhouse.shortcuts import model_to_dict

from .models import Game, GameLine
from .serializers import (
    GameLineReadSerializer,
    GameLineSerializer,
    GameReadSerializer,
    GameSerializer,
)
from .team import TeamTable


class GameTable(BaseTable):
    MODEL_CLASS = Game
    SERIALIZER_CLASS = GameSerializer
    READ_SERIALIZER_CLASS = GameReadSerializer
    PKS: list[str] = ["date_time", "home_id", "away_id"]

    DEPENDENCIES = [TeamTable]

    @overload
    def filter_by_datetime(self, *, min_datetime: datetime) -> list[GameSerializer]: ...

    @overload
    def filter_by_datetime(
        self, *, min_datetime: datetime, as_df: Literal[True]
    ) -> pd.DataFrame: ...

    @overload
    def filter_by_datetime(
        self, *, min_datetime: datetime, as_df: Literal[False]
    ) -> list[GameSerializer]: ...

    # def insert_record(self, *, data: dict) -> Optional[GameSerializer]:
    #     """
    #     Insert a row into the database.
    #     """
    #     validated_data: GameSerializer = GameSerializer(
    #         id=uuid.uuid4(), **data, timestamp=datetime.now()
    #     )

    #     result: Game = self.model_class.create(**validated_data.model_dump())

    #     if result:
    #         return validated_data
    #     else:
    #         return None

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


class GameLineTable(BaseTable):
    MODEL_CLASS = GameLine
    SERIALIZER_CLASS = GameLineSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = GameLineSerializer
    READ_SERIALIZER_CLASS = GameLineReadSerializer
    PKS: list[str] = ["date_time", "home_id", "away_id"]

    DEPENDENCIES = [GameTable]
