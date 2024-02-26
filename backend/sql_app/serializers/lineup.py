from pydantic import BaseModel as BaseSerializer
from pydantic import UUID4
from typing import Optional


class LineupSerializer(BaseSerializer):
    game_id: UUID4
    team: str
    status: str
    PG: str
    SG: str
    SF: str
    PF: str
    C: str
    injuries: list[dict[str, str]] = []
    # Bench: Optional[list]
