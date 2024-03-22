from base.sql_app.database import DB
from peewee import Model


class BaseModel(Model):
    class Meta:
        database = DB
