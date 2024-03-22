from base.sql_app.settings import DB_URL
from peewee import InterfaceError, PostgresqlDatabase

print(f"Connecting to database at {DB_URL}")

DB = PostgresqlDatabase(DB_URL)

try:
    DB.connect()
except InterfaceError as e:
    DB = None
    print(e)
