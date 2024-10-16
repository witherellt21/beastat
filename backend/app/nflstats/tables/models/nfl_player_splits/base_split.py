from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer

from ..nfl_team import NFLTeamReadSerializer


class NFLPlayerBaseInfoSerializer(BaseSerializer):
    player_id: str
    season: int
    age: int
    team_id: UUID4
    pos: str
    gp: int


class NFLPlayerBaseInfoReadSerializer(NFLPlayerBaseInfoSerializer):
    _team_id: UUID4
    team: NFLTeamReadSerializer
