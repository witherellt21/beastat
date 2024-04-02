import json

from peewee import CharField, UUIDField
from playhouse.postgres_ext import BinaryJSONField

from .base_model import BaseModel


class Team(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    name = CharField()
    abbr = CharField(max_length=3)
    alt_abbrs = BinaryJSONField(dumps=json.dumps)
