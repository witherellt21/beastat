import json

from peewee import (
    CharField,
    DateField,
    DateTimeField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    UUIDField,
)
from playhouse.postgres_ext import JSONField

from .base_model import BaseModel
from .game import Game
from .team import Team


class Player(BaseModel):
    id = CharField(unique=True, primary_key=True)
    # team
    team = ForeignKeyField(Team, backref="players", null=True)
    name = CharField()
    nicknames = JSONField(dumps=json.dumps)
    active_from = IntegerField()
    active_to = IntegerField()
    position = CharField()
    height = IntegerField()
    weight = IntegerField()
    birth_date = DateField()
    timestamp = DateTimeField()


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
