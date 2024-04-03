from typing import Optional

import pandas as pd
from base.scraper.base.util import QueryArgs
from nbastats.sql_app.register import BasicInfo


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
