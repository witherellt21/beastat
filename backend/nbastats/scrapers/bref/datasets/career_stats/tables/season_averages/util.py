from typing import Optional

import pandas as pd
from core.scraper.base.util import QueryArgs
from nbastats.sql_app.register import SeasonAveragess


def has_season_column(tables: list[pd.DataFrame]) -> Optional[pd.DataFrame]:
    data = next(
        (table for table in tables if "Season" in table.columns),
        None,
    )
    return data


def get_cached_player_season_averages_data(query_args: QueryArgs):
    data = SeasonAveragess.filter_records(
        query={"player_id": query_args.get("player_id")}, as_df=True
    )

    foreign_keys = SeasonAveragess.get_foreign_relationships()

    foreign_keys_remap = {
        foreign_key: f"{foreign_key}_id" for foreign_key in foreign_keys
    }

    data = data.rename(columns=foreign_keys_remap)

    return data
