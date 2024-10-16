from peewee import InterfaceError, OperationalError, PostgresqlDatabase
from settings import DB_URL

print(f"Connecting to database at {DB_URL}")

DB = PostgresqlDatabase(DB_URL)
DB.connect()
