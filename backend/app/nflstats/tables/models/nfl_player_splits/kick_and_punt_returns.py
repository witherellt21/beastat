from typing import Optional

from peewee import CharField, FloatField, ForeignKeyField, IntegerField
from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable

from ..nfl_team import NFLTeam, NFLTeamReadSerializer
from .base_split import NFLPlayerBaseInfoSerializer


class NFLKickAndPuntReturnSplit(BaseModel):
    player_id = CharField()
    season = IntegerField()
    age = IntegerField()
    team = ForeignKeyField(NFLTeam, backref="player_kick_and_punt_return_splits")
    pos = CharField()
    gp = IntegerField()
    pr = IntegerField()
    pr_yards = IntegerField()
    pr_tds = IntegerField()
    pr_long = IntegerField()
    pr_yards_avg = FloatField(null=True)
    kr = IntegerField()
    kr_yards = IntegerField()
    kr_tds = IntegerField()
    kr_long = IntegerField()
    kr_yards_avg = FloatField(null=True)

    class Meta:
        indexes = ((("player_id", "season"), True),)


class NFLKickAndPuntReturnSplitSerializer(NFLPlayerBaseInfoSerializer):
    pr: int
    pr_yards: int
    pr_tds: int
    pr_long: int
    pr_yards_avg: Optional[float]
    kr: int
    kr_yards: int
    kr_tds: int
    kr_long: int
    kr_yards_avg: Optional[float]


class NFLKickAndPuntReturnSplitReadSerializer(NFLKickAndPuntReturnSplitSerializer):
    _team_id: UUID4
    team: NFLTeamReadSerializer


class NFLKickAndPuntReturnSplitsTable(BaseTable):
    MODEL_CLASS = NFLKickAndPuntReturnSplit
    SERIALIZER_CLASS = NFLKickAndPuntReturnSplitSerializer
    READ_SERIALIZER_CLASS = NFLKickAndPuntReturnSplitReadSerializer
    PKS = ["player_id", "season"]
