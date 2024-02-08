from peewee import *
from sql_app.models.base import BaseModel

class PlayerInfo(BaseModel):
    player_id = CharField(unique=True)
    name = CharField()
    active_from = IntegerField()
    active_to = IntegerField()
    position = CharField()
    height = IntegerField()
    weight = IntegerField()
    birth_date = DateField()
    timestamp = DateTimeField()

class College(BaseModel):
    name = CharField()
    player_info = ForeignKeyField(PlayerInfo, to_field='player_id', backref='colleges')

