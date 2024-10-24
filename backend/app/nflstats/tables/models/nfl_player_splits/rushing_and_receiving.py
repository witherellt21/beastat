from typing import Optional

from peewee import CharField, FloatField, ForeignKeyField, IntegerField
from pydantic import UUID4
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable

from ..nfl_player import NFLPlayer, NFLPlayerReadSerializer
from ..nfl_team import NFLTeam, NFLTeamReadSerializer
from .base_split import NFLPlayerBaseInfoSerializer


class NFLRushingAndReceivingSplit(BaseModel):
    player = ForeignKeyField(NFLPlayer, backref="kick_and_punt_return_splits")
    season = IntegerField()
    age = IntegerField()
    team = ForeignKeyField(NFLTeam, backref="player_rushing_and_receiving_splits")
    pos = CharField()
    gp = IntegerField()
    gs = IntegerField()

    rush = IntegerField()
    rush_yds = IntegerField()
    rush_tds = IntegerField()
    rush_fds = IntegerField(null=True)
    rush_succ_perc = FloatField(null=True)
    rush_long = IntegerField(null=True)
    yds_per_carry = FloatField(null=True)
    rush_yds_per_game = FloatField()
    rush_per_game = FloatField()

    targets = IntegerField(null=True)
    rec = IntegerField()
    rec_yds = IntegerField()
    yds_per_rec = FloatField(null=True)
    rec_tds = IntegerField()
    rec_fds = IntegerField(null=True)
    rec_succ_perc = FloatField(null=True)
    rec_long = IntegerField(null=True)
    rec_per_game = FloatField()
    rec_yds_per_game = FloatField()
    catch_perc = FloatField(null=True)
    yds_per_target = FloatField(null=True)


class NFLRushingAndReceivingSplitSerializer(NFLPlayerBaseInfoSerializer):
    gs: int

    rush: int
    rush_yds: int
    rush_tds: int
    rush_fds: Optional[int]
    rush_succ_perc: Optional[float]
    rush_long: Optional[int]
    yds_per_carry: Optional[float]
    rush_yds_per_game: float
    rush_per_game: float

    targets: Optional[int]
    rec: int
    rec_yds: int
    yds_per_rec: Optional[float]
    rec_tds: int
    rec_fds: Optional[int]
    rec_succ_perc: Optional[float]
    rec_long: Optional[int]
    rec_per_game: float
    rec_yds_per_game: float
    catch_perc: Optional[float]
    yds_per_target: Optional[float]


class NFLRushingAndReceivingSplitReadSerializer(NFLRushingAndReceivingSplitSerializer):
    _team_id: UUID4
    team: NFLTeamReadSerializer

    _player_id: str
    player: NFLPlayerReadSerializer


class NFLRushingAndReceivingSplitsTable(BaseTable):
    MODEL_CLASS = NFLRushingAndReceivingSplit
    SERIALIZER_CLASS = NFLRushingAndReceivingSplitSerializer
    READ_SERIALIZER_CLASS = NFLRushingAndReceivingSplitReadSerializer
    PKS = ["player_id", "season"]
