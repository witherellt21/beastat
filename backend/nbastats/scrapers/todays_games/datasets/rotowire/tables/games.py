import uuid

from core.scraper import (
    BaseHTMLTableSerializer,
    CharField,
    DatetimeField,
    IntegerField,
    TransformationField,
)
from nbastats.sql_app.register import Games, Teams


class GamesTableForm(BaseHTMLTableSerializer):
    id = CharField(default=uuid.uuid4)
    date_time = DatetimeField(format="%Y-%m-%d")
    # home: Annotated[str, StringConstraints(min_length=3, max_length=3)]
    # away: Annotated[str, StringConstraints(min_length=3, max_length=3)]  # type: ignore
    home_id = TransformationField(str, Teams.get_team_id_or_nan)
    away_id = TransformationField(str, Teams.get_team_id_or_nan)
    home_score = IntegerField(null=True, default=None)
    away_score = IntegerField(null=True, default=None)
    winner = CharField(null=True, default=None)  # type: ignore
    victory_margin = IntegerField(null=True, default=None)


NAME = "Games"

SQL_TABLE = Games

IDENTIFICATION_FUNCTION = lambda tables: next(
    (table for table in tables if "date_time" in table.columns),
    None,
)

TABLE_SERIALIZER = GamesTableForm()
