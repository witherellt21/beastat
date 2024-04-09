from typing import Annotated
from uuid import UUID

from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer
from pydantic import StringConstraints


class TeamSerializer(BaseSerializer):
    id: UUID4
    name: str
    abbr: Annotated[str, StringConstraints(min_length=3, max_length=3)]
    alt_abbrs: list[Annotated[str, StringConstraints(min_length=3, max_length=3)]] = []


class TeamReadSerializer(TeamSerializer):
    id: UUID4
