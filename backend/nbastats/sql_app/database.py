from peewee import InterfaceError, OperationalError, PostgresqlDatabase

from .settings import DB_URL

print(f"Connecting to database at {DB_URL}")


try:
    DB = PostgresqlDatabase(DB_URL)
    DB.connect()
except InterfaceError as e:
    DB = None
    print(e)
except OperationalError as oe:
    DB = None
    print(oe)
