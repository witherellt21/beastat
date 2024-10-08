import logging
import os

from core.db.settings import *

logger = logging.getLogger("main")

DB_URL = os.environ.get("DB_URL", None)
