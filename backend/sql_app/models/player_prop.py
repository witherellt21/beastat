from peewee import *
from sql_app.models.base import BaseModel


class PlayerProp(BaseModel):
    player_id = CharField()
    player_name = CharField()
    stat = CharField()
    line = FloatField()
    odds_over = IntegerField()
    implied_odds_over = FloatField()
    odds_under = IntegerField()
    implied_odds_under = FloatField()
    timestamp = DateTimeField()
