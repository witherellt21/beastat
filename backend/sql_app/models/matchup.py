from peewee import CharField
from peewee import IntegerField
from sql_app.models.base import BaseModel


class Matchup(BaseModel):
    game_id = IntegerField()
    position = CharField()
    home_player = CharField()
    away_player = CharField()
    home_player_id = CharField(null=True)
    away_player_id = CharField(null=True)
