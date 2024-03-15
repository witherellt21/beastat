from peewee import PostgresqlDatabase, InterfaceError
import os

DB = PostgresqlDatabase(os.environ.get("DB_URL"))

try:
    DB.connect()
except InterfaceError as e:
    DB = None
    print(e)
