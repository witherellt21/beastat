import logging
import os

from base.sql_app.settings import *

logger = logging.getLogger("main")

DB_URL = os.environ.get("DB_URL", None)
