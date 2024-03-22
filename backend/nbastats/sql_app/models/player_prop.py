from base.sql_app.models import BaseModel
from peewee import CharField, FloatField, ForeignKeyField, IntegerField, UUIDField

from .game import Game
from .player import Player


class PropLine(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    game = ForeignKeyField(Game, backref="props")
    status = IntegerField(choices=[0, 1])
    stat = CharField()
    line = FloatField()
    over = IntegerField()
    under = IntegerField()
    over_implied = FloatField()
    under_implied = FloatField()
    player = ForeignKeyField(Player, backref="props")
    # when we get player_id fetch the team they are currently on
    # then get the teams current game
