import peewee

from sql_app.models.gamelog import Gamelog
from sql_app.serializers.gamelog import GamelogSerializer

from sql_app.database import DB
from sql_app.register.base import BaseTable


class GamelogTable(BaseTable):
    MODEL_CLASS = Gamelog
    SERIALIZER_CLASS = GamelogSerializer
    PKS = ["player_id", "Date"]


# try:
Gamelogs = GamelogTable(DB)
# except peewee.OperationalError as e:
#     print("Unable to connect to database for Gamelog.")
