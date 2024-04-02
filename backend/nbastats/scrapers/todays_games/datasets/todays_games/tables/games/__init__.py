import uuid

from nbastats.scrapers.util.team_helpers import get_team_id_by_abbr
from nbastats.sql_app.register import Games

NAME = "Games"

SQL_TABLE = Games

IDENTIFICATION_FUNCTION = lambda tables: next(
    (table for table in tables if "date_time" in table.columns),
    None,
)

CONFIG = {
    "filters": [],
    "datetime_columns": {"date_time": "%Y-%m-%d"},
    # "json_columns": ["injuries"],
    "rename_columns": {},
    "rename_values": {},
    "transformations": {
        ("date_time", "id"): lambda x: uuid.uuid4(),
        "home_id": get_team_id_by_abbr,
        "away_id": get_team_id_by_abbr,
        # ("date_time", "home_score"): lambda x: 0,
        # ("date_time", "away_score"): lambda x: 0,
    },
    "data_transformations": [],
    "query_save_columns": {},
    "required_fields": [],
    "nan_values": [],
    "stat_augmentations": {},
    "href_save_map": {},
}
