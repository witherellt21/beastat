from peewee import (
    CharField,
    FloatField,
    IntegerField,
    ForeignKeyField,
    UUIDField,
)
from sql_app.models.base import BaseModel
from sql_app.models.player import Player
from . import Game


class PropLine(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    game = ForeignKeyField(Game, backref="game")
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
