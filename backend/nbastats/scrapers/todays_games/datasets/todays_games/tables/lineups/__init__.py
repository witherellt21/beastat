import uuid

from nbastats.scrapers.util.team_helpers import get_team_id_by_abbr
from nbastats.sql_app.register import Lineups

NAME = "Lineups"

SQL_TABLE = Lineups

IDENTIFICATION_FUNCTION = lambda tables: next(
    (table for table in tables if "status" in table.columns),
    None,
)

CONFIG = {
    "json_columns": ["injuries"],
    "transformations": {
        ("team_id", "id"): lambda x: uuid.uuid4(),
        "team_id": get_team_id_by_abbr,
    },
}
