import uuid

from core.scraper import BaseHTMLTableSerializer, CharField
from nbastats.db.register import Matchups


class MatchupTableForm(BaseHTMLTableSerializer):
    id = CharField(default=uuid.uuid4)
    game_id = CharField(depends_on="Games")
    position = CharField()
    home_player_id = CharField()
    away_player_id = CharField()


NAME = "Matchups"

SQL_TABLE = Matchups

IDENTIFICATION_FUNCTION = lambda tables: next(
    (table for table in tables if "position" in table.columns),
    None,
)

TABLE_SERIALIZER = MatchupTableForm()
