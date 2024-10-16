import logging
import os
from typing import Any

logger = logging.getLogger("main")

DB_URL = os.environ.get("DB_URL", None)

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "PlayerScraper": {"status": False, "log_level": logging.INFO},
    "DefenseRankingsScraper": {"status": False},
    "PlayerPropsScraper": {"status": True},
    "TodaysGamesScraper": {"status": False},
}
