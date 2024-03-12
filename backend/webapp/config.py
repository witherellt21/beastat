from typing import Any
import logging

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "Player": {"status": False},
    "DefenseRankings": {"status": False},
    "PlayerProps": {"status": True},
    "Lineups": {"status": False},
    "CareerStats": {
        "status": True,
        "options": {"identifier_source": "matchups_only", "log_level": logging.INFO},
    },
    "Gamelogs": {"status": False, "options": {"identifier_source": "all"}},
}
