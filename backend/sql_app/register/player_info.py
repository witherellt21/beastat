from sql_app.models.player_info import College
from sql_app.models.player_info import PlayerInfo, Player
from sql_app.serializers.player_info import CollegeSerializer
from sql_app.serializers.player_info import (
    PlayerInfoSerializer,
    PlayerSerializer,
    PlayerTableEntrySerializer,
)
from sql_app.serializers.player_info import PlayerInfoReadSerializer
from sql_app.serializers.player_info import PlayerInfoTableEntrySerializer

from sql_app.database import DB
from sql_app.register.base import BaseTable
from playhouse.shortcuts import model_to_dict

from sql_app.models.player_prop import PropLine

import logging

logger = logging.getLogger("main")


class PlayerInfoTable(BaseTable):
    MODEL_CLASS = PlayerInfo
    SERIALIZER_CLASS = PlayerInfoSerializer
    READ_SERIALIZER_CLASS = PlayerInfoReadSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = PlayerInfoTableEntrySerializer
    PKS = ["player_id"]


class PlayerTable(BaseTable):
    MODEL_CLASS = Player
    SERIALIZER_CLASS = PlayerSerializer
    # READ_SERIALIZER_CLASS = PlayerInfoReadSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = PlayerTableEntrySerializer
    PKS = ["id"]

    def get_with_prop_lines(self, *, query: dict):
        # player = Player.get(**query)
        player = Player.select().join(PropLine).dicts()
        # logger.debug(model_to_dict(player.props))
        print(player)
        # for prop in player.props:
        #     logger.debug(model_to_dict(prop))
        return player


class CollegeTable(BaseTable):
    MODEL_CLASS = College
    SERIALIZER_CLASS = CollegeSerializer

    # try:


PlayerInfos = PlayerInfoTable(DB)
Players = PlayerTable(DB)
Colleges = CollegeTable(DB)


# except peewee.OperationalError as e:
#     print("Unable to connect to database for PlayerInfo.")

# def populate_db_from_csv():
#     # with open('saved_tables\\player_data\\player_ids\\a.csv') as f:
#     #     rows = csv.reader(f)
#     #     for row in rows:
#     #         print(row)
#     df = pd.read_csv('saved_tables\\player_data\\player_ids\\a.csv')
#     df = df.drop("Unnamed: 0", axis=1)
#     df = df.rename(columns = COLUMN_NAMES)
#     df["height"] = list(map(lambda height: int(height.split('-')[0])*12 + int(height.split('-')[1]), df["height"]))
#     df["birth_date"] = pd.to_datetime(df["birth_date"])
#     # df["colleges"] = df["colleges"].fillna([])
#     df["colleges"].loc[df["colleges"].isnull()] = df["colleges"].loc[df["colleges"].isnull()].apply(lambda x: [])
#     df["colleges"] = list(map(lambda colleges: [colleges] if type(colleges) != list else colleges, df["colleges"]))
#     # print(df)
#     df.loc[2, "colleges"].append("Arkansas")
#     row_dicts = df.to_dict(orient='records')
#     for row in row_dicts:
#         player_info = PlayerInfos.insert_row(data=row)
#         print(player_info)


# if __name__ == "__main__":
#     # populate_db = populate_db_from_csv()
#     # print(populate_db)
#     player_info = PlayerInfos.get_info_by_player_id(id='agbajoc01')
#     print(player_info)

if __name__ == "__main__":
    PlayerInfos.update_or_insert_record(data={"player_id": "iuwriwer"})
