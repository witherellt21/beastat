from peewee import MySQLDatabase
from peewee import PostgresqlDatabase

# DB = MySQLDatabase(
#     'nbastats',
#     user='root',
#     password='T@yl0r31lax',
#     host='localhost',
#     port=3306
# )

try:
    DB = PostgresqlDatabase(
        "nbastats", user="nbastats", password="nbastats", host="nbastats-db", port=5432
    )

    DB.connect()
except:
    DB = None
    print("Unable to connect to DB.")
