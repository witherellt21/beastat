from peewee import BooleanField
from peewee import CharField
from peewee import IntegerField
from sql_app.models.base import BaseModel


class Lineup(BaseModel):
    game_id = IntegerField()
    team = CharField()
    opp = CharField()
    home = BooleanField()
    confirmed = BooleanField(null=True)
    PG = CharField(null=True)
    SG = CharField(null=True)
    SF = CharField(null=True)
    PF = CharField(null=True)
    C = CharField(null=True)
    # Bench = FloatField(null=True)
