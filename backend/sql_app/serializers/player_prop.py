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


class OddsSerializer(BaseSerializer):
    odds: int | None = None
    implied_odds: float | None = None


# class LineSerializer(BaseSerializer):
#     line: float | None = None
#     over: OddsSerializer = OddsSerializer()
#     under: OddsSerializer = OddsSerializer()


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
