from peewee import PostgresqlDatabase

try:
    DB = PostgresqlDatabase(
        "nbastats", user="nbastats", password="nbastats", host="nbastats-db", port=5432
    )

    DB.connect()
except:
    DB = None
    print("Unable to connect to DB.")
