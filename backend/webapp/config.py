import logging
from typing import Any

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "Player": {"status": True},
    "DefenseRankings": {"status": False},
    "PlayerProps": {"status": False},
    "TodaysGames": {"status": False},
    # "CareerStats": {
    #     "status": False,
    #     "options": {"identifier_source": "matchups_only", "log_level": logging.INFO},
    # },
    # "Gamelogs": {"status": False, "options": {"identifier_source": "all"}},
}
