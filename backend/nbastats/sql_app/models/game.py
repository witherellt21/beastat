import uuid

from peewee import (
    CharField,
    DateTimeField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    UUIDField,
)

from .base_model import BaseModel
from .team import Team


class Game(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    date_time = DateTimeField()
    home = ForeignKeyField(Team, backref="home_games")
    away = ForeignKeyField(Team, backref="away_games")
    home_score = IntegerField(null=True)
    away_score = IntegerField(null=True)
    winner = CharField(max_length=3, null=True)
    victory_margin = IntegerField(null=True)
    timestamp = DateTimeField()


class GameLine(BaseModel):
    game = ForeignKeyField(Game, backref="line", unique=True)
    favored_team = ForeignKeyField(Team, backref="favored_games")
    line = FloatField()
    spread = FloatField()
    over_under = FloatField()
