from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer

from .game import ReadGameSerializer
from .player import PlayerSerializer
from .team import ReadTeamSerializer


class LineupSerializer(BaseSerializer):
    id: UUID4
    game_id: UUID4
    team_id: UUID4
    status: str
    PG_id: str
    SG_id: str
    SF_id: str
    PF_id: str
    C_id: str
    injuries: list[dict[str, str]] = []
    # Bench: Optional[list]


class LineupReadSerializer(BaseSerializer):
    game: ReadGameSerializer
    team: ReadTeamSerializer
    status: str
    PG: PlayerSerializer
    SG: PlayerSerializer
    SF: PlayerSerializer
    PF: PlayerSerializer
    C: PlayerSerializer
    injuries: list[dict[str, str]] = []


class LineupTableEntrySerializer(BaseSerializer):
    id: str
    game_id: str
    team_id: str
    status: str
    PG_id: str
    SG_id: str
    SF_id: str
    PF_id: str
    C_id: str
    injuries: list[dict[str, str]] = []
    # Bench: Optional[list]
