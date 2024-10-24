import json
from typing import Annotated

from peewee import CharField
from playhouse.postgres_ext import BinaryJSONField
from pydantic import BaseModel as BaseSerializer
from pydantic import StringConstraints
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable


class NFLTeam(BaseModel):
    id = CharField(primary_key=True, unique=True, max_length=3)
    name = CharField()
    abbr = CharField(max_length=3)
    alt_abbrs = BinaryJSONField(dumps=json.dumps)


class NFLTeamSerializer(BaseSerializer):
    id: Annotated[str, StringConstraints(min_length=3, max_length=3)]
    name: str
    abbr: Annotated[str, StringConstraints(min_length=3, max_length=3)]
    alt_abbrs: list[Annotated[str, StringConstraints(min_length=3, max_length=3)]] = []


class NFLTeamReadSerializer(NFLTeamSerializer):
    pass


class NFLTeamsTable(BaseTable):
    MODEL_CLASS = NFLTeam
    SERIALIZER_CLASS = NFLTeamSerializer
    READ_SERIALIZER_CLASS = NFLTeamReadSerializer
    PKS = ["abbr"]
