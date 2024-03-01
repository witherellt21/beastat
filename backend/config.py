from typing import Any
import logging

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "PlayerProps": {"status": True},
    "PlayerInfo": {"status": False},
    "Gamelogs": {"status": True, "options": {"identifier_source": "all"}},
    "CareerStats": {
        "status": False,
        "options": {"identifier_source": "all", "log_level": logging.INFO},
    },
    "Lineups": {"status": True},
    "DefenseRankings": {"status": True},
}
