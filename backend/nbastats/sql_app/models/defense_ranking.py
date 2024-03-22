from peewee import CharField, ForeignKeyField, IntegerField

from .base_model import BaseModel
from .team import Team


class DefenseRanking(BaseModel):
    team = ForeignKeyField(Team, backref="defense_rankings")
    stat = CharField()
    ALL = IntegerField()
    PG = IntegerField()
    SG = IntegerField()
    SF = IntegerField()
    PF = IntegerField()
    C = IntegerField()
