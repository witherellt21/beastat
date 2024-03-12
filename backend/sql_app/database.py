from peewee import PostgresqlDatabase, InterfaceError
import os


# DB = PostgresqlDatabase(
#     "nbastats", user="nbastats", password="nbastats", host="localhost", port=5432
# )
DB = PostgresqlDatabase(os.environ.get("DB_URL"))

try:
    DB.connect()
except InterfaceError:
    DB = None
