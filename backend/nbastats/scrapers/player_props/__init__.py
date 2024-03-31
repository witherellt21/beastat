import logging

from base.scraper.base import ScraperKwargs

from .datasets.games_dataset import NAME as GAMES
from .datasets.games_dataset.tables.games_table import NAME as GAMES_TABLE
from .datasets.player_props_dataset import NAME as PLAYER_PROPS
from .datasets.player_props_dataset.tables.player_props_table import (
    NAME as PLAYER_PROPS_TABLE,
)

NAME = "PlayerPropsScraper"
CONFIG: ScraperKwargs = {
    "active": False,
    "log_level": logging.INFO,
    "download_rate": 2,
    "align": "inline",
}

DEPENDENCIES = {
    PLAYER_PROPS: {
        "source_name": GAMES,
        "source_table_name": "some table",
        "query_set_provider": lambda: [1, 2],
    }
}

INHERITANCES = {
    (PLAYER_PROPS, PLAYER_PROPS_TABLE): {
        "source": (GAMES, GAMES_TABLE),
        "inheritance_function": lambda dataframe: dataframe,
    }
}
