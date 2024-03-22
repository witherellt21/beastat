import logging
from typing import Any

logger = logging.getLogger("main")

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "PlayerScraper": {"status": True, "log_level": logging.INFO},
    "DefenseRankingsScraper": {"status": False},
    "PlayerPropsScraper": {"status": False},
    "TodaysGamesScraper": {"status": False},
}
