import uuid
from peewee import IntegerField
from peewee import CharField
from peewee import DateTimeField
from peewee import UUIDField
from sql_app.models.base import BaseModel


class Game(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    date_time = DateTimeField()
    home = CharField(max_length=3)  # link to team
    away = CharField(max_length=3)  # link to team
    line = CharField(null=True)
    spread = CharField(null=True)
    over_under = CharField(null=True)
    home_score = IntegerField(null=True)
    away_score = IntegerField(null=True)
    winner = CharField(max_length=3, null=True)
    victory_margin = IntegerField(null=True)
    timestamp = DateTimeField()
