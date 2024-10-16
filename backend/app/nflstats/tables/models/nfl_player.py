import json

from peewee import CharField, IntegerField
from playhouse.postgres_ext import JSONField
from pydantic import BaseModel as BaseSerializer
from scrapp.db import DB
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable


class NFLPlayer(BaseModel):
    id = CharField(unique=True, primary_key=True)
    # team = ForeignKeyField(Team, backref="players", null=True)
    name = CharField()
    pos = JSONField(dumps=json.dumps)
    active_from = IntegerField()
    active_to = IntegerField()

    # timestamp = DateTimeField()
    class Meta:
        database = DB


class NFLPlayerSerializer(BaseSerializer):
    id: str
    name: str
    pos: list[str]
    active_from: int
    active_to: int
    # timestamp: datetime.datetime  # timestamp in epoch


class NFLPlayerInsertSerializer(NFLPlayerSerializer):
    id: str
    name: str
    pos: list[str]
    active_from: int
    active_to: int


class NFLPlayerReadSerializer(NFLPlayerSerializer):
    id: str
    name: str
    pos: list[str]
    active_from: int
    active_to: int


class NFLPlayersTable(BaseTable):
    MODEL_CLASS = NFLPlayer
    SERIALIZER_CLASS = NFLPlayerInsertSerializer
    READ_SERIALIZER_CLASS = NFLPlayerReadSerializer
    PKS = ["id"]
