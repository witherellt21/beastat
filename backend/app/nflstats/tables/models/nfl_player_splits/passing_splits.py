from datetime import datetime

from peewee import CharField, DateTimeField, FloatField, ForeignKeyField, IntegerField
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable

from ..nfl_player import NFLPlayer, NFLPlayerReadSerializer
from ..nfl_team import NFLTeam, NFLTeamReadSerializer
from .base_split import NFLPlayerBaseInfoSerializer


class NFLPassingSplit(BaseModel):
    player = ForeignKeyField(NFLPlayer, backref="defensive_splits")
    season = IntegerField()
    age = IntegerField()
    team = ForeignKeyField(NFLTeam, backref="defensive_splits")
    pos = CharField()
    gp = IntegerField()
    gs = IntegerField()

    wins = IntegerField()
    losses = IntegerField()
    ties = IntegerField()
    comp = IntegerField()
    att = IntegerField()
    comp_perc = FloatField()
    yds = IntegerField()
    tds = IntegerField()
    td_perc = FloatField()
    ints = IntegerField()
    int_perc = FloatField()
    fds = IntegerField()
    succ_rate = FloatField()
    long = IntegerField()
    yds_per_att = FloatField()
    yds_per_att_adj = FloatField()
    yds_per_comp = FloatField()
    yds_per_gp = FloatField()
    rating = FloatField()
    qbr = FloatField()
    sacks = IntegerField()
    sack_yds = IntegerField()
    sack_perc = FloatField()
    yds_per_att_net = FloatField()
    yds_per_att_net_adj = FloatField()
    cbs = IntegerField()
    gwds = IntegerField()
    value = IntegerField()
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        indexes = ((("player_id", "season", "team_id"), True),)


class NFLPassingSplitSerializer(NFLPlayerBaseInfoSerializer):
    gs: int

    wins: int
    losses: int
    ties: int
    comp: int
    att: int
    comp_perc: float
    yds: int
    tds: int
    td_perc: float
    ints: int
    int_perc: float
    fds: int
    succ_rate: float
    long: int
    yds_per_att: float
    yds_per_att_adj: float
    yds_per_comp: float
    yds_per_gp: float
    rating: float
    qbr: float
    sacks: int
    sack_yds: int
    sack_perc: float
    yds_per_att_net: float
    yds_per_att_net_adj: float
    cbs: int
    gwds: int
    value: int


class NFLPassingSplitReadSerializer(NFLPassingSplitSerializer):
    _team_id: str
    team: NFLTeamReadSerializer

    _player_id: str
    player: NFLPlayerReadSerializer


class NFLPassingSplitsTable(BaseTable):
    MODEL_CLASS = NFLPassingSplit
    SERIALIZER_CLASS = NFLPassingSplitSerializer
    READ_SERIALIZER_CLASS = NFLPassingSplitReadSerializer
    PKS = ["player_id", "season", "team_id"]
