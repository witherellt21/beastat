from peewee import CharField
from peewee import IntegerField
from peewee import ForeignKeyField

from . import BaseModel, Team


class DefenseRanking(BaseModel):
    team = ForeignKeyField(Team, backref="defense_rankings")
    stat = CharField()
    ALL = IntegerField()
    PG = IntegerField()
    SG = IntegerField()
    SF = IntegerField()
    PF = IntegerField()
    C = IntegerField()
