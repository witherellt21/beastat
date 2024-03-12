from typing import Any
import logging

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "Player": {"status": False},
    "DefenseRankings": {"status": False},
    "PlayerProps": {"status": False},
    "Lineups": {"status": True},
    "CareerStats": {
        "status": False,
        "options": {"identifier_source": "all", "log_level": logging.INFO},
    },
    "Gamelogs": {"status": False, "options": {"identifier_source": "all"}},
}
