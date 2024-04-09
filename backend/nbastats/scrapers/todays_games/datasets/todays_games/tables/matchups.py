import uuid

from core.scraper.fields import CharField
from core.scraper.html_table_serializer import BaseHTMLTableSerializer
from nbastats.sql_app.register import Matchups


class MatchupTableForm(BaseHTMLTableSerializer):
    id = CharField(default=uuid.uuid4)
    game_id = CharField()
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
