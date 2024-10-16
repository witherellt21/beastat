import logging
import os
from configparser import ConfigParser
from typing import Any

logger = logging.getLogger("main")

config = ConfigParser()
config.read("config.ini")

DB_URL = os.environ.get("DB_URL", None)

API_PREFIX: str = config.get("api_prefix", "")

DATA_SCRAPE: dict[str, dict[str, Any]] = {}
