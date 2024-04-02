import logging

from base.scraper.base.scraper import ScraperKwargs

from .datasets.career_stats import NAME as CAREER_STATS
from .datasets.player_info import NAME as PLAYERINFO
from .datasets.player_season_gamelog import NAME as GAMELOG
from .util import get_team_id_from_career_stats

NAME = "Players"

CONFIG: ScraperKwargs = {
    "active": False,
    "log_level": logging.INFO,
    "download_rate": 5,
    "align": "nested",
}

DEPENDENCIES = {
    CAREER_STATS: {
        "source_name": PLAYERINFO,
        "source_table_name": "BasicInfo",
        "query_set_provider": lambda dataset: [
            {"player_last_initial": player_id[0], "player_id": player_id}
            for player_id in dataset.index.values
        ],
    },
    GAMELOG: {
        "source_name": CAREER_STATS,
        "source_table_name": "SeasonAverages",
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
    (PLAYERINFO, "BasicInfo"): {
        "source": (CAREER_STATS, "SeasonAverages"),
        "inheritance_function": get_team_id_from_career_stats,
    }
}
