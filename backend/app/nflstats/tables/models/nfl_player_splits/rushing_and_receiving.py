from peewee import CharField, FloatField, ForeignKeyField, IntegerField
from pydantic import UUID4
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable

from ..nfl_team import NFLTeam, NFLTeamReadSerializer
from .base_split import NFLPlayerBaseInfoSerializer


class NFLRushingAndReceivingSplit(BaseModel):
    player_id = CharField()
    season = IntegerField()
    age = IntegerField()
    team = ForeignKeyField(NFLTeam, backref="player_rushing_and_receiving_splits")
    pos = CharField()
    gp = IntegerField()
    gs = IntegerField()

    rush = IntegerField()
    rush_yds = IntegerField()
    rush_tds = IntegerField()
    rush_fds = IntegerField()
    rush_succ_perc = FloatField()
    rush_long = IntegerField()
    yds_per_carry = FloatField()
    rush_yds_per_game = FloatField()
    rush_per_game = FloatField()

    targets = IntegerField()
    rec = IntegerField()
    rec_yds = IntegerField()
    yds_per_rec = FloatField()
    rec_tds = IntegerField()
    rec_fds = IntegerField()
    rec_succ_perc = FloatField()
    rec_long = IntegerField()
    rec_per_game = FloatField()
    rec_yds_per_game = FloatField()
    catch_perc = FloatField()
    yds_per_target = FloatField()


class NFLRushingAndReceivingSplitSerializer(NFLPlayerBaseInfoSerializer):
    gs: int

    rush: int
    rush_yds: int
    rush_tds: int
    rush_fds: int
    rush_succ_perc: float
    rush_long: int
    yds_per_carry: float
    rush_yds_per_game: float
    rush_per_game: float

    targets: int
    rec: int
    rec_yds: int
    yds_per_rec: float
    rec_tds: int
    rec_fds: int
    rec_succ_perc: float
    rec_long: int
    rec_per_game: float
    rec_yds_per_game: float
    catch_perc: float
    yds_per_target: float


class NFLRushingAndReceivingSplitReadSerializer(NFLRushingAndReceivingSplitSerializer):
    _team_id: UUID4
    team: NFLTeamReadSerializer


class NFLRushingAndReceivingSplitsTable(BaseTable):
    MODEL_CLASS = NFLRushingAndReceivingSplit
    SERIALIZER_CLASS = NFLRushingAndReceivingSplitSerializer
    READ_SERIALIZER_CLASS = NFLRushingAndReceivingSplitReadSerializer
    PKS = ["player_id", "season"]
