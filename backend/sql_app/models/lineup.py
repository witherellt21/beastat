from peewee import BooleanField
from peewee import CharField
from peewee import IntegerField
from peewee import UUIDField
from playhouse.postgres_ext import JSONField
from sql_app.models.base import BaseModel
import json


class Lineup(BaseModel):
    game_id = UUIDField()
    team = CharField()
    status = CharField()
    PG = CharField(null=True)
    SG = CharField(null=True)
    SF = CharField(null=True)
    PF = CharField(null=True)
    C = CharField(null=True)
    injuries = JSONField(dumps=json.dumps)
    # Bench = FloatField(null=True)
