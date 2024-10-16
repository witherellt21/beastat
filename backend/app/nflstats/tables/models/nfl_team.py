import json
import uuid
from typing import Annotated

from peewee import CharField, UUIDField
from playhouse.postgres_ext import BinaryJSONField
from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer
from pydantic import Field, StringConstraints
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable


class NFLTeam(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    name = CharField()
    abbr = CharField(max_length=3)
    alt_abbrs = BinaryJSONField(dumps=json.dumps)


class NFLTeamSerializer(BaseSerializer):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str
    abbr: Annotated[str, StringConstraints(min_length=3, max_length=3)]
    alt_abbrs: list[Annotated[str, StringConstraints(min_length=3, max_length=3)]] = []


class NFLTeamReadSerializer(NFLTeamSerializer):
    # id: UUID4  # type: ignore
    pass


class NFLTeamsTable(BaseTable):
    MODEL_CLASS = NFLTeam
    SERIALIZER_CLASS = NFLTeamSerializer
    READ_SERIALIZER_CLASS = NFLTeamReadSerializer
    PKS = ["abbr"]
