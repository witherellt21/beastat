from sql_app.register.base import BaseTable
from sql_app.models.game import Game
from sql_app.serializers.game import GameSerializer
from sql_app.database import DB
from typing import Optional
from datetime import datetime
import uuid


class GameTable(BaseTable):
    MODEL_CLASS = Game
    SERIALIZER_CLASS = GameSerializer
    PKS: list[str] = ["date_time", "home", "away"]

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


Games = GameTable(DB)
