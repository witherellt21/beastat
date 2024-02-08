import peewee

from sql_app.database import DB

class BaseModel(peewee.Model):
    class Meta:
        database = DB
        