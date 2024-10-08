import datetime
from typing import Annotated  # import Annotated
from typing import Literal, Optional

from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer
from pydantic import Field

from .game import GameSerializer
from .team import TeamReadSerializer


class BasePlayerSerializer(BaseSerializer):
    id: str
    name: str
    nicknames: list[str] = []
    active_from: int
    active_to: int
    position: str
    height: int
    weight: int
    birth_date: datetime.date
    timestamp: datetime.datetime  # timestamp in epoch


class PlayerInsertSerializer(BasePlayerSerializer):
    team_id: Optional[UUID4]


class PlayerReadSerializer(BasePlayerSerializer):
    team: Optional[TeamReadSerializer]

    # class Config:
    #     # fields = {"team_id": {"exclude": True}}
    #     exclude = ["team_id"]

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     for field in self.Config.exclude:
    #         self.model_fields.pop(field)

    # def json(self, **kwargs):
    #     include = getattr(self.Config, "include", set())
    #     if len(include) == 0:
    #         include = None
    #     exclude = getattr(self.Config, "exclude", set())
    #     if len(exclude) == 0:
    #         exclude = None
    #     return super().json(include=include, exclude=exclude, **kwargs)


class PlayerUpdateSerializer(PlayerInsertSerializer):
    pass


####################
# Player Props
####################


class PlayerPropSerializer(BaseSerializer):
    id: UUID4
    game_id: UUID4
    status: Literal[0, 1]
    stat: str
    line: float
    over: int
    over_implied: float
    under: int
    under_implied: float
    player_id: str


class PlayerPropReadSerializer(PlayerPropSerializer):
    id: str

    _game_id: UUID4
    game: GameSerializer

    _player_id: str
    player: Optional[PlayerInsertSerializer]
