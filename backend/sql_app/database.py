from peewee import PostgresqlDatabase
import os


DB = PostgresqlDatabase(
    "nbastats", user="nbastats", password="nbastats", host="localhost", port=5432
)

DB.connect()
