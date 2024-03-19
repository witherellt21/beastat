import os

from peewee import InterfaceError, PostgresqlDatabase
from sql_app.settings import DB_URL

print(f"Connecting to database at {DB_URL}")

DB = PostgresqlDatabase(DB_URL)

try:
    DB.connect()
except InterfaceError as e:
    DB = None
    print(e)
