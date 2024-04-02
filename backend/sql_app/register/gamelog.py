import datetime
import peewee
import pandas as pd
from pydantic import BaseModel
from typing import Optional
from sql_app.models.gamelog import Gamelog
from sql_app.models.player_info import Player
from sql_app.serializers.gamelog import GamelogSerializer, GamelogReadSerializer
from sql_app.database import DB
from sql_app.register.base import BaseTable
from playhouse.shortcuts import model_to_dict
from typing import TypedDict, Any, Union
from numbers import Number


class GamelogQuery(BaseModel):
    greater_than: dict[str, Union[int, float, datetime.datetime]] = {}
    less_than: dict[str, Union[int, float, datetime.datetime]] = {}
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

    def filter_records_advanced(
        self,
        query: Optional[GamelogQuery] = None,
        columns: list[str] = [],
        confuse: bool = False,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        search = self.model_class.select()

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
            )

        if confuse:
            search = search.order_by(peewee.fn.Random())

        if limit is not None:
            search = search.limit(limit)

        rows = []
        for row in search:
            rows.append(model_to_dict(row, recurse=False))

        return pd.DataFrame(rows)


# try:
Gamelogs = GamelogTable(DB)
# except peewee.OperationalError as e:
#     print("Unable to connect to database for Gamelog.")
