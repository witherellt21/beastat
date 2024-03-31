from nbastats.global_implementations import constants
from nbastats.scrapers.players.datasets.player_info.tables.basic_info.util import (
    convert_height_to_inches,
    get_cached_player_info_data,
    has_player_column,
)
from sql_app.register import BasicInfo
from unidecode import unidecode

NAME = "BasicInfo"

SQL_TABLE = BasicInfo

IDENTIFICATION_FUNCTION = has_player_column

CONFIG = {
    "filters": [lambda dataframe: dataframe["active_to"] == constants.CURRENT_SEASON],
    "datetime_columns": {"birth_date": "%B %d, %Y"},
    "rename_columns": {
        "Player": "name",
        "From": "active_from",
        "To": "active_to",
        "Pos": "position",
        "Ht": "height",
        "Wt": "weight",
        "Birth Date": "birth_date",
    },
    "rename_values": {"weight": {"": 0}},
    "transformations": {
        "name": lambda name: unidecode(name),
        "height": lambda height: convert_height_to_inches(height=height),
        ("player_link", "id"): lambda link: link.rsplit("/", 1)[1].split(".")[0],
        ("name", "team_id"): lambda row: None,
    },
    "data_transformations": [],
    "query_save_columns": {},
    "required_columns": [],
    "href_save_map": {"Player": "player_link"},
    "cached_query_generator": get_cached_player_info_data,
}
