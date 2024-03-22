from base.sql_app.models import BaseModel
from peewee import CharField, ForeignKeyField, IntegerField

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
