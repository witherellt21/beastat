from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer

from .team import ReadTeamSerializer


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


class ReadDefenseRankingSerializer(BaseSerializer):
    team: ReadTeamSerializer
    stat: str
    ALL: int
    PG: int
    SG: int
    SF: int
    PF: int
    C: int


class DefenseRankingTableEntrySerializer(BaseSerializer):
    id: str
    team_id: str
    stat: str
    ALL: int
    PG: int
    SG: int
    SF: int
    PF: int
    C: int
