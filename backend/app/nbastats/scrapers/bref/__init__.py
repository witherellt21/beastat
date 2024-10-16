import logging

from scrapp.scraper import WebScraperKwargs

from .util import get_team_id_from_career_stats
from .web_pages.career_stats import NAME as CAREER_STATS
from .web_pages.career_stats.tables.season_averages import NAME as SEASONAVERAGES
from .web_pages.player_info import NAME as PLAYERINFO
from .web_pages.player_info.tables.basic_info import NAME as BASICINFO
from .web_pages.player_season_gamelog import NAME as GAMELOG

NAME = "BasketballReference"

CONFIG: WebScraperKwargs = {
    "active": False,
    "log_level": logging.DEBUG,
    "download_rate": 5,
    "align": "nested",
}

DEPENDENCIES = {
    CAREER_STATS: {
        "source_name": PLAYERINFO,
        "source_table_name": BASICINFO,
        "query_set_provider": lambda dataset: [
            {"player_last_initial": player_id[0], "player_id": player_id}
            for player_id in dataset.index.values
        ],
    },
    GAMELOG: {
        "source_name": CAREER_STATS,
        "source_table_name": SEASONAVERAGES,
        "query_set_provider": lambda dataset: [
            {
                "player_last_initial": row["player_id"][0],
                "player_id": row["player_id"],
                "year": row["Season"],
            }
            for index, row in dataset[["player_id", "Season"]].iterrows()
        ],
    },
}

INHERITANCES = {
    (PLAYERINFO, BASICINFO): {
        "source": (CAREER_STATS, SEASONAVERAGES),
        "inheritance_function": get_team_id_from_career_stats,
    }
}
