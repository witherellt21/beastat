from peewee import BooleanField
from peewee import CharField
from peewee import DateField
from peewee import FloatField
from peewee import IntegerField
from sql_app.models.base import BaseModel
"game_id", "team", "opp", "home", "confirmed", "PG","SG","SF","PF","C","Bench"
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