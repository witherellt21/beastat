from peewee import CharField
from peewee import IntegerField
from sql_app.models.base import BaseModel


class DefenseRanking(BaseModel):
    team = CharField()  # link to team
    # team_abr = CharField()
    stat = CharField()
    ALL = IntegerField()
    PG = IntegerField()
    SG = IntegerField()
    SF = IntegerField()
    PF = IntegerField()
    C = IntegerField()
    # Bench = FloatField(null=True)
