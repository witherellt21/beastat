from peewee import CharField, UUIDField
from playhouse.postgres_ext import JSONField
from sql_app.models import BaseModel
import json


class Team(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    name = CharField()
    abbr = CharField(max_length=3)
    alt_abbrs = JSONField(dumps=json.dumps)
    # ranking =
