from peewee import PostgresqlDatabase
from scrapp.conf import settings

print(f"Connecting to database at {settings.DB_URL}")

DB = PostgresqlDatabase(settings.DB_URL)
connected = DB.connect()
