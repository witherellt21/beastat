from peewee import CharField
from peewee import FloatField
from peewee import IntegerField
from peewee import ForeignKeyField
from peewee import UUIDField
from sql_app.models.base import BaseModel
from sql_app.models.player import Player


class CareerStats(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    player = ForeignKeyField(Player, backref="career_stats")
    Season = CharField()
    Age = IntegerField()
    Tm = CharField()  # link to team
    Lg = CharField()
    Pos = CharField()
    G = IntegerField()
    GS = IntegerField()
    MP = FloatField(null=True)
    FG = FloatField(null=True)
    FGA = FloatField(null=True)
    FG_perc = FloatField(null=True)
    THP = FloatField(null=True)
    THPA = FloatField(null=True)
    THP_perc = FloatField(null=True)
    TWP = FloatField(null=True)
    TWPA = FloatField(null=True)
    TWP_perc = FloatField(null=True)
    eFG_perc = FloatField(null=True)
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
    Awards = CharField()
    PA = FloatField(null=True)
    PR = FloatField(null=True)
    RA = FloatField(null=True)
    PRA = FloatField(null=True)
