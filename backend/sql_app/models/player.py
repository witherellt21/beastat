from peewee import CharField, DateField, DateTimeField, IntegerField, ForeignKeyField
from playhouse.postgres_ext import JSONField
from sql_app.models.base import BaseModel
import json

from . import Team


class Player(BaseModel):
    id = CharField(unique=True, primary_key=True)
    # team
    team = ForeignKeyField(Team, backref="team")
    name = CharField()
    nicknames = JSONField(dumps=json.dumps)
    active_from = IntegerField()
    active_to = IntegerField()
    position = CharField()
    height = IntegerField()
    weight = IntegerField()
    birth_date = DateField()
    timestamp = DateTimeField()
