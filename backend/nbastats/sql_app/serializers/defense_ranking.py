from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer

from .team import TeamReadSerializer


class DefenseRankingSerializer(BaseSerializer):
    id: UUID4
    team_id: UUID4
    stat: str
    ALL: int
    PG: int
    SG: int
    SF: int
    PF: int
    C: int


class DefenseRankingReadSerializer(DefenseRankingSerializer):
    id: str

    _team_id: UUID4
    team: TeamReadSerializer
