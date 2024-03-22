import os

from base.sql_app.settings import *
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ["DB_URL"]
