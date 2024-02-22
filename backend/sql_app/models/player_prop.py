from peewee import CharField, AutoField, FloatField, IntegerField, ForeignKeyField
from sql_app.models.base import BaseModel


class Player(BaseModel):
    player_id = CharField(unique=True)
    name = CharField()


class PropLine(BaseModel):
    id = AutoField(unique=True)
    stat = CharField()
    line = FloatField()
    over = IntegerField()
    under = IntegerField()
    over_implied = FloatField()
    under_implied = FloatField()
    player = ForeignKeyField(Player, backref="props")
