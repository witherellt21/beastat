from peewee import CharField
from peewee import IntegerField
from peewee import UUIDField
from peewee import ForeignKeyField
from sql_app.models.base import BaseModel
from sql_app.models.player import Player
from sql_app.models.game import Game


class Matchup(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    game = ForeignKeyField(Game, backref="matchups")
    position = CharField()
    home_player = ForeignKeyField(Player, backref="home_matchups")
    away_player = ForeignKeyField(Player, backref="away_matchups")
