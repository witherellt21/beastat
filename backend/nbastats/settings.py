import logging
from typing import Any

logger = logging.getLogger("main")

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "PlayerScraper": {"status": False, "log_level": logging.INFO},
    "DefenseRankingsScraper": {"status": False},
    "PlayerPropsScraper": {"status": True},
    "TodaysGamesScraper": {"status": False},
}
