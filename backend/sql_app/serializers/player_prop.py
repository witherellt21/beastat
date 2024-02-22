from pydantic import BaseModel as BaseSerializer
import datetime


class PlayerPropSerializer(BaseSerializer):
    player_id: str
    name: str
    # stat: str
    # line: float
    # odds_over: int
    # implied_odds_over: float
    # odds_under: int
    # implied_odds_under: float
    # timestamp: datetime.datetime


class PlayerPropTableEntrySerializer(BaseSerializer):
    player_id: str
    name: str
    stat: str
    line: float
    odds_over: int
    implied_odds_over: float
    odds_under: int
    implied_odds_under: float


class OddsSerializer(BaseSerializer):
    odds: int | None = None
    implied_odds: float | None = None


class PropLineSerializer(BaseSerializer):
    line: float | None = None
    stat: str
    over: int
    under: int
    over_implied: float
    under_implied: float
    player_id: int


class ReadPropLineSerializer(BaseSerializer):
    line: float | None = None
    stat: str
    over: int
    under: int
    over_implied: float
    under_implied: float
    player: PlayerPropSerializer


class ReadPlayerPropSerializer(BaseSerializer):
    id: int
    player_id: str
    name: str
    # lines: "list[PropLineSerializer]"
