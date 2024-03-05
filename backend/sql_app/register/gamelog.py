import peewee
import pandas as pd
from pydantic import BaseModel
from sql_app.models.gamelog import Gamelog
from sql_app.models.player_info import Player
from sql_app.serializers.gamelog import GamelogSerializer, GamelogReadSerializer
from sql_app.database import DB
from sql_app.register.base import BaseTable
from playhouse.shortcuts import model_to_dict
from typing import TypedDict, Any
from numbers import Number


class GamelogQuery(BaseModel):
    greater_than: dict[str, int | float] = {}
    less_than: dict[str, int | float] = {}
    equal_to: dict[str, Any] = {}


class GamelogTable(BaseTable):
    MODEL_CLASS = Gamelog
    SERIALIZER_CLASS = GamelogSerializer
    READ_SERIALIZER_CLASS = GamelogReadSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = GamelogSerializer
    PKS = ["player_id", "Date"]

    DEPENDENCIES = [Player]

    def average_column(self, player_id, column: str, limit: int = 10) -> int:
        last_10_played_in = (
            self.model_class.select(getattr(self.model_class, column))
            .where(Gamelog.MP != None, Gamelog.player == player_id)
            .order_by(Gamelog.Date.desc())
            .limit(limit)
        )
        average_mp = last_10_played_in.select_from(
            peewee.fn.AVG(last_10_played_in.c.MP).alias("average")
        )
        res = average_mp.execute()

        return res[0].average

    def count_records(
        self,
        *,
        query: GamelogQuery = GamelogQuery(),
    ) -> int:
        """
        Return all rows matching the search query.
        """
        # start = time.time()
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

        # Serialize rows and convert to desired output type
        return count

    def func(self, player_id):
        # query = Gamelog.select().where(
        #     Gamelog.player == player_id, Gamelog.MP > 30, Gamelog.MP < 30.2
        # )

        for obj in query:
            print(model_to_dict(obj))

        return None


# try:
Gamelogs = GamelogTable(DB)
# except peewee.OperationalError as e:
#     print("Unable to connect to database for Gamelog.")
