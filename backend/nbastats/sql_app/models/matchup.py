from peewee import CharField, ForeignKeyField, UUIDField

from .base_model import BaseModel
from .game import Game
from .player import Player


class Matchup(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    game = ForeignKeyField(Game, backref="matchups")
    position = CharField()
    home_player = ForeignKeyField(Player, backref="home_matchups")
    away_player = ForeignKeyField(Player, backref="away_matchups")
