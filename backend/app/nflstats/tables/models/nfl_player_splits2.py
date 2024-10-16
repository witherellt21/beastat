from peewee import CharField, ForeignKeyField, IntegerField
from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable

from .nfl_team import NFLTeam, NFLTeamReadSerializer


class NFLCareerSplit(BaseModel):
    player_id = CharField()
    season = IntegerField()
    age = IntegerField()
    team = ForeignKeyField(NFLTeam, backref="player_career_splits")
    pos = CharField()
    gp = IntegerField()
    gs = IntegerField()
    targets = IntegerField()
    receptions = IntegerField()
    yards = IntegerField()

    class Meta:
        indexes = ((("player_id", "season"), True),)


class NFLCareerSplitSerializer(BaseSerializer):
    id: str
    season: int
    age: int
    team: UUID4
    pos: str
    gp: int
    gs: int
    targets: int
    receptions: int
    yards: int


class NFLCareerSplitReadSerializer(NFLCareerSplitSerializer):
    team: NFLTeamReadSerializer


class NFLPlayerSplitsTable(BaseTable):
    MODEL_CLASS = NFLCareerSplit
    SERIALIZER_CLASS = NFLCareerSplitSerializer
    READ_SERIALIZER_CLASS = NFLCareerSplitReadSerializer
    PKS = ["id"]
