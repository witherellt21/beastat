from peewee import BooleanField
from peewee import CharField
from peewee import IntegerField
from peewee import UUIDField
from peewee import ForeignKeyField
from playhouse.postgres_ext import JSONField
import json

from .game import Game
from .player import Player
from .team import Team
from .base import BaseModel


class Lineup(BaseModel):
    id = UUIDField(primary_key=True, unique=True)
    game = ForeignKeyField(Game, backref="lineups")
    team = ForeignKeyField(Team, backref="team")
    status = CharField()
    PG = ForeignKeyField(Player, backref="lineups_as_pg")
    SG = ForeignKeyField(Player, backref="lineups_as_sg")
    SF = ForeignKeyField(Player, backref="lineups_as_sf")
    PF = ForeignKeyField(Player, backref="lineups_as_pf")
    C = ForeignKeyField(Player, backref="lineups_as_c")
    injuries = JSONField(dumps=json.dumps)
    # Bench = FloatField(null=True)
