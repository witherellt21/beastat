from peewee import Model
from scrapp.db import DB


class BaseModel(Model):
    class Meta:
        database = DB
