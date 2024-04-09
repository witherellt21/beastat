from typing import Optional

import pandas as pd
from core.scraper.base.table_form import (
    BaseTableForm,
    CharField,
    DatetimeField,
    HTMLSaveField,
    RenameField,
    TransformationField,
)
from core.scraper.base.util import QueryArgs
from nbastats.lib import constants
from nbastats.sql_app.register import BasicInfo
from unidecode import unidecode


def convert_height_to_inches(height: str) -> int:
    feet, inches = height.split("-")
    return int(feet) * 12 + int(inches)


def has_player_column(tables: list[pd.DataFrame]) -> Optional[pd.DataFrame]:
    data = next(
        (table for table in tables if "Player" in table.columns),
        None,
    )
    return data


def get_cached_player_info_data(query_args: QueryArgs):

    last_initial = query_args.get("player_last_initial", None)

    if last_initial:

        data = BasicInfo.get_players_with_last_initial(last_initial=last_initial)

        foreign_keys = BasicInfo.get_foreign_relationships()

        foreign_keys_remap = {
            foreign_key: f"{foreign_key}_id" for foreign_key in foreign_keys
        }

        data = data.rename(columns=foreign_keys_remap)

        return data

    else:
        return pd.DataFrame()


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
