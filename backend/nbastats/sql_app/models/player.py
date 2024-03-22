import json

from base.sql_app.models import BaseModel
from peewee import CharField, DateField, DateTimeField, ForeignKeyField, IntegerField
from playhouse.postgres_ext import JSONField

from .team import Team


class Player(BaseModel):
    id = CharField(unique=True, primary_key=True)
    # team
    team = ForeignKeyField(Team, backref="players", null=True)
    name = CharField()
    nicknames = JSONField(dumps=json.dumps)
    active_from = IntegerField()
    active_to = IntegerField()
    position = CharField()
    height = IntegerField()
    weight = IntegerField()
    birth_date = DateField()
    timestamp = DateTimeField()
