import datetime
from typing import Any, Optional, Union

import pandas as pd
import peewee
from core.sql_app.register import AdvancedQuery, BaseTable
from playhouse.shortcuts import model_to_dict
from pydantic import BaseModel

from .models import Game, Gamelog
from .player import PlayerTable
from .serializers import GamelogReadSerializer, GamelogSerializer


class GamelogQuery(BaseModel):
    greater_than: dict[str, Union[int, float, datetime.datetime]] = {}
    less_than: dict[str, Union[int, float, datetime.datetime]] = {}
    equal_to: dict[str, Any] = {}


class GamelogTable(BaseTable):
    MODEL_CLASS = Gamelog
    SERIALIZER_CLASS = GamelogSerializer
    READ_SERIALIZER_CLASS = GamelogReadSerializer
    PKS = ["player_id", "game_id"]

    DEPENDENCIES = [PlayerTable]

    def average_column(self, player_id, column: str, limit: int = 10) -> int:
        last_10_played_in = (
            self.model_class.select(getattr(self.model_class, column))
            .where(Gamelog.MP != None, Gamelog.player == player_id)
            .order_by(Gamelog.game.Date.desc())
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
        query: Optional[AdvancedQuery] = None,
        columns: list[str] = [],
        confuse: bool = False,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        search = self.model_class.select()

        # print(query.in_.items())

        if query:
            search = search.join(Game, on=(Gamelog.game == Game.id)).where(
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
                # Game.date_time > datetime.datetime(year=2024, day=1, month=5),
            )

        if confuse:
            search = search.order_by(peewee.fn.Random())

        if limit is not None:
            search = search.limit(limit)

        rows = []
        for row in search:
            # print(model_to_dict(row, recurse=False))
            rows.append(model_to_dict(row, recurse=False))

        return pd.DataFrame(rows)
