from pydantic import BaseModel as BaseSerializer


class DefenseRankingSerializer(BaseSerializer):
    team: str
    team_abr: str
    stat: str
    ALL: int
    PG: int
    SG: int
    SF: int
    PF: int
    C: int
