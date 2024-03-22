import json

from base.sql_app.models import BaseModel
from peewee import CharField, ForeignKeyField, UUIDField
from playhouse.postgres_ext import JSONField

from .game import Game
from .player import Player
from .team import Team


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
