import uuid

from core.scraper.base.table_form import (
    BaseTableForm,
    CharField,
    DatetimeField,
    HTMLSaveField,
    IntegerField,
    RenameField,
    TransformationField,
)
from nbastats.global_implementations import constants
from nbastats.scrapers.players.datasets.player_info.tables.basic_info.util import (
    convert_height_to_inches,
    get_cached_player_info_data,
    has_player_column,
)
from nbastats.sql_app.register import BasicInfo
from unidecode import unidecode


class PlayerInfoTableEntrySerializer(BaseTableForm):
    # id = CharField(default=uuid.uuid4)
    team_id = CharField(null=True, default=None)
    player_link = HTMLSaveField("Player")

    id = TransformationField(
        str,
        lambda link: link.rsplit("/", 1)[1].split(".")[0],
        from_columns=["player_link"],
    )
    name = TransformationField(
        str, lambda name: unidecode(name), from_columns=["Player"]
    )
    active_from = RenameField("From", type=int)
    active_to = RenameField(
        "To", type=int, filters=[lambda x: x == constants.CURRENT_SEASON]
    )
    position = RenameField("Pos", type=str)
    height = TransformationField(int, convert_height_to_inches, from_columns=["Ht"])
    weight = RenameField("Wt", type=int, replace_values={"": 0})
    birth_date = DatetimeField(format="%B %d, %Y", from_column="Birth Date")


print(PlayerInfoTableEntrySerializer().html_save_fields)

NAME = "BasicInfo"

SQL_TABLE = BasicInfo

IDENTIFICATION_FUNCTION = has_player_column

TABLE_SERIALIZER = PlayerInfoTableEntrySerializer()

CONFIG = {
    "cached_query_generator": get_cached_player_info_data,
}
