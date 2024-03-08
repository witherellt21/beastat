from typing import Any
import logging

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "PlayerInfo": {"status": False},
    "DefenseRankings": {"status": True},
    "PlayerProps": {"status": True},
    "Lineups": {"status": True},
    "CareerStats": {
        "status": False,
        "options": {"identifier_source": "all", "log_level": logging.INFO},
    },
    "Gamelogs": {"status": True, "options": {"identifier_source": "all"}},
}
