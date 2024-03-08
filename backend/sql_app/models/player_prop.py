from peewee import (
    CharField,
    FloatField,
    IntegerField,
    ForeignKeyField,
    UUIDField,
)
from sql_app.models.base import BaseModel
from sql_app.models.player_info import Player


class PropLine(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    # game (contains teams)
    # status (upcoming, live, past)
    stat = CharField()
    line = FloatField()
    over = IntegerField()
    under = IntegerField()
    over_implied = FloatField()
    under_implied = FloatField()
    player = ForeignKeyField(Player, backref="props")
    # when we get player_id fetch the team they are currently on
    # then get the teams current game
