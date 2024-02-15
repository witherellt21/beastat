from peewee import *
from sql_app.models.base import BaseModel


class Player(BaseModel):
    # id = AutoField(unique=True)
    player_id = CharField(unique=True)
    name = CharField()
    # stat = CharField()
    # line = FloatField()
    # odds_over = IntegerField()
    # implied_odds_over = FloatField()
    # odds_under = IntegerField()
    # implied_odds_under = FloatField()
    # timestamp = DateTimeField()


class PropLine(BaseModel):
    id = AutoField(unique=True)
    stat = CharField()
    line = FloatField()
    over = IntegerField()
    under = IntegerField()
    over_implied = FloatField()
    under_implied = FloatField()
    player = ForeignKeyField(Player, backref="props")
