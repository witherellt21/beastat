import uuid

from peewee import CharField, ForeignKeyField, IntegerField
from playhouse.postgres_ext import UUIDField

from .base_model import BaseModel
from .team import Team


class DefenseRanking(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    team = ForeignKeyField(Team, backref="defense_rankings")
    stat = CharField()
    ALL = IntegerField()
    PG = IntegerField()
    SG = IntegerField()
    SF = IntegerField()
    PF = IntegerField()
    C = IntegerField()
