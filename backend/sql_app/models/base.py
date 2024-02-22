from peewee import Model
from sql_app.database import DB


class BaseModel(Model):
    class Meta:
        database = DB
