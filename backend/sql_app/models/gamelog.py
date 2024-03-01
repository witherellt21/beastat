from peewee import CharField
from peewee import DateField
from peewee import FloatField
from peewee import ForeignKeyField
from peewee import UUIDField
from peewee import IntegerField
from sql_app.models.base import BaseModel
from sql_app.models.player_info import Player


class Gamelog(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    player = ForeignKeyField(Player, backref="gamelogs")
    G = FloatField(null=True)
    Date = DateField()
    Age = CharField()
    Tm = CharField()
    Opp = CharField()
    result = CharField()
    margin = IntegerField()
    GS = FloatField(null=True)
    MP = FloatField(null=True)
    FG = FloatField(null=True)
    FGA = FloatField(null=True)
    FG_perc = FloatField(null=True)
    THP = FloatField(null=True)
    THPA = FloatField(null=True)
    THP_perc = FloatField(null=True)
    FT = FloatField(null=True)
    FTA = FloatField(null=True)
    FT_perc = FloatField(null=True)
    ORB = FloatField(null=True)
    DRB = FloatField(null=True)
    TRB = FloatField(null=True)
    AST = FloatField(null=True)
    STL = FloatField(null=True)
    BLK = FloatField(null=True)
    TOV = FloatField(null=True)
    PF = FloatField(null=True)
    PTS = FloatField(null=True)
    GmSc = FloatField(null=True)
    PA = FloatField(null=True)
    PR = FloatField(null=True)
    RA = FloatField(null=True)
    PRA = FloatField(null=True)
    days_rest = FloatField(null=True)
