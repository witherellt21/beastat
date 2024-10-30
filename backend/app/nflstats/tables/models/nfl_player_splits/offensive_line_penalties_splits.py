from datetime import datetime

from peewee import CharField, DateTimeField, FloatField, ForeignKeyField, IntegerField
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable

from ..nfl_player import NFLPlayer, NFLPlayerReadSerializer
from ..nfl_team import NFLTeam, NFLTeamReadSerializer
from .base_split import NFLPlayerBaseInfoSerializer


class NFLOffensivePenaltiesLineSplit(BaseModel):
    player = ForeignKeyField(NFLPlayer, backref="offensive_line_penalties_splits")
    season = IntegerField()
    age = IntegerField()
    team = ForeignKeyField(NFLTeam, backref="offensive_line_penalties_splits")
    pos = CharField()
    gp = IntegerField()
    gs = IntegerField()

    holding = IntegerField()
    false_start = IntegerField()
    voided = IntegerField()
    pen_tot = IntegerField()

    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        indexes = ((("player_id", "season", "team_id"), True),)


class NFLOffensiveLinePenaltiesSplitSerializer(NFLPlayerBaseInfoSerializer):
    gs: int

    holding: int
    false_start: int
    voided: int
    pen_tot: int


class NFLOffensiveLinePenaltiesSplitReadSerializer(
    NFLOffensiveLinePenaltiesSplitSerializer
):
    _team_id: str
    team: NFLTeamReadSerializer

    _player_id: str
    player: NFLPlayerReadSerializer


class NFLOffensiveLinePenaltiesSplitsTable(BaseTable):
    MODEL_CLASS = NFLOffensivePenaltiesLineSplit
    SERIALIZER_CLASS = NFLOffensiveLinePenaltiesSplitSerializer
    READ_SERIALIZER_CLASS = NFLOffensiveLinePenaltiesSplitReadSerializer
    PKS = ["player_id", "season", "team_id"]
