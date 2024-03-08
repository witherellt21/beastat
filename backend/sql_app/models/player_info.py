from peewee import CharField, DateField, DateTimeField, IntegerField, ForeignKeyField
from playhouse.postgres_ext import JSONField
from sql_app.models.base import BaseModel
import json


class PlayerInfo(BaseModel):
    player_id = CharField(unique=True)
    name = CharField()
    active_from = IntegerField()
    active_to = IntegerField()
    position = CharField()
    height = IntegerField()
    weight = IntegerField()
    birth_date = DateField()
    timestamp = DateTimeField()


class Player(BaseModel):
    id = CharField(unique=True, primary_key=True)
    # team
    name = CharField()
    nicknames = JSONField(dumps=json.dumps)
    active_from = IntegerField()
    active_to = IntegerField()
    position = CharField()
    height = IntegerField()
    weight = IntegerField()
    birth_date = DateField()
    timestamp = DateTimeField()


class College(BaseModel):
    name = CharField()
    player_info = ForeignKeyField(PlayerInfo, to_field="player_id", backref="colleges")
