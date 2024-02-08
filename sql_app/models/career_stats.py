from peewee import CharField
from peewee import FloatField
from peewee import IntegerField
from sql_app.models.base import BaseModel

class CareerStats(BaseModel):
    player_id = CharField()
    Season = CharField()
    Age = IntegerField()
    Tm = CharField()
    Lg = CharField()
    Pos = CharField()
    G = IntegerField()
    GS = IntegerField()
    MP = FloatField()
    FG = FloatField()
    FGA = FloatField()
    FG_perc = FloatField()
    THP = FloatField()
    THPA = FloatField()
    THP_perc = FloatField(null=True)
    TWP = FloatField()
    TWPA = FloatField()
    TWP_perc = FloatField()
    eFG_perc = FloatField()
    FT = FloatField()
    FTA = FloatField()
    FT_perc = FloatField()
    ORB = FloatField()
    DRB = FloatField()
    TRB = FloatField()
    AST = FloatField()
    STL = FloatField()
    BLK = FloatField()
    TOV = FloatField()
    PF = FloatField()
    PTS = FloatField()
    Awards = CharField()
    PA = FloatField()
    PR = FloatField()
    RA = FloatField()
    PRA = FloatField()