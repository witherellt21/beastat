from nbastats.db.database import DB
from peewee import Model


class BaseModel(Model):
    class Meta:
        database = DB
