from peewee import (
    CharField,
    AutoField,
    FloatField,
    IntegerField,
    ForeignKeyField,
    UUIDField,
)
from sql_app.models.base import BaseModel
from sql_app.models.player_info import Player


class PlayerBet(BaseModel):
    player_id = CharField(unique=True)
    name = CharField()


class PropLine(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    stat = CharField()
    line = FloatField()
    over = IntegerField()
    under = IntegerField()
    over_implied = FloatField()
    under_implied = FloatField()
    player = ForeignKeyField(Player, backref="props")
