import uuid

from core.scraper import (
    BaseHTMLTableSerializer,
    CharField,
    ListField,
    TransformationField,
)
from nbastats.sql_app.register import Lineups, Teams


class LineupTableForm(BaseHTMLTableSerializer):
    id = CharField(default=uuid.uuid4)
    game_id = CharField(depends_on="Games")
    team_id = TransformationField(str, Teams.get_team_id_or_nan)
    status = CharField()
    PG_id = CharField()
    SG_id = CharField()
    SF_id = CharField()
    PF_id = CharField()
    C_id = CharField()
    injuries = ListField(type=str)


NAME = "Lineups"

SQL_TABLE = Lineups

IDENTIFICATION_FUNCTION = lambda tables: next(
    (table for table in tables if "status" in table.columns),
    None,
)

TABLE_SERIALIZER = LineupTableForm()
