from datetime import datetime

from peewee import CharField, DateTimeField, FloatField, ForeignKeyField, IntegerField
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable

from ..nfl_player import NFLPlayer, NFLPlayerReadSerializer
from ..nfl_team import NFLTeam, NFLTeamReadSerializer
from .base_split import NFLPlayerBaseInfoSerializer


class NFLDefensiveSplit(BaseModel):
    player = ForeignKeyField(NFLPlayer, backref="defensive_splits")
    season = IntegerField()
    age = IntegerField()
    team = ForeignKeyField(NFLTeam, backref="defensive_splits")
    pos = CharField()
    gp = IntegerField()
    gs = IntegerField()

    ints = IntegerField()
    int_yds = IntegerField()
    int_tds = IntegerField()
    int_long = IntegerField()
    passes_def = IntegerField()

    fumb_forced = IntegerField()
    fumb = IntegerField()
    fumb_rec = IntegerField()
    fumb_yds = IntegerField()
    fumb_tds = IntegerField()

    sack = FloatField()

    tack = IntegerField()
    tack_solo = IntegerField()
    tack_ast = IntegerField()
    tack_fl = IntegerField()
    tack_qb = IntegerField()

    safety = IntegerField()
    value = IntegerField()
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        indexes = ((("player_id", "season", "team_id"), True),)


class NFLDefensiveSplitSerializer(NFLPlayerBaseInfoSerializer):
    gs: int

    ints: int
    int_yds: int
    int_tds: int
    int_long: int
    passes_def: int

    fumb_forced: int
    fumb: int
    fumb_rec: int
    fumb_yds: int
    fumb_tds: int

    sack: float

    tack: int
    tack_solo: int
    tack_ast: int
    tack_fl: int
    tack_qb: int

    safety: int
    value: int


class NFLDefensiveSplitReadSerializer(NFLDefensiveSplitSerializer):
    _team_id: str
    team: NFLTeamReadSerializer

    _player_id: str
    player: NFLPlayerReadSerializer


class NFLDefensiveSplitsTable(BaseTable):
    MODEL_CLASS = NFLDefensiveSplit
    SERIALIZER_CLASS = NFLDefensiveSplitSerializer
    READ_SERIALIZER_CLASS = NFLDefensiveSplitReadSerializer
    PKS = ["player_id", "season", "team_id"]
