import os

from base.sql_app.settings import *
from dotenv import load_dotenv

load_dotenv("../.env")

DB_URL = os.environ["DB_URL"]
print(DB_URL)
