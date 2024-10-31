import re
from typing import Any, Optional

import numpy as np
import pandas as pd
from scrapp.tables import schema


def extract_season_as_int_or_none(season: Any) -> Optional[int]:
    if type(season) == float:
        if np.isnan(season):
            return None

        return int(season)

    elif type(season) == str:
        year_match = re.search(r"\d{4}", season)

        return int(year_match.group(0)) if year_match else None

    elif type(season) == int:
        return season

    else:
        return None


def has_regular_season_return_data(
    tables: list[pd.DataFrame],
) -> Optional[pd.DataFrame]:
    return next(
        (
            table
            for table in tables
            if "Punt Returns" in table.columns.get_level_values(0)
            and "No." in table.columns.get_level_values(1)
        ),
        None,
    )


def has_regular_season_rushing_and_receiving_columns(
    tables: list[pd.DataFrame],
) -> Optional[pd.DataFrame]:
    return next(
        (
            table
            for table in tables
            if "Rushing" in table.columns.get_level_values(0)
            and "Receiving" in table.columns.get_level_values(0)
            and "Season" in table.columns.get_level_values(1)
        ),
        None,
    )


def has_regular_season_defensive_data(
    tables: list[pd.DataFrame],
) -> Optional[pd.DataFrame]:
    return next(
        (
            table
            for table in tables
            if "Def Interceptions" in table.columns.get_level_values(0)
            and "Season" in table.columns.get_level_values(1)
        ),
        None,
    )


def has_regular_season_passing_data(
    tables: list[pd.DataFrame],
) -> Optional[pd.DataFrame]:
    return next(
        (table for table in tables if "Cmp" in table.columns and "AV" in table.columns),
        None,
    )


def has_regular_season_offensive_line_data(
    tables: list[pd.DataFrame],
) -> Optional[pd.DataFrame]:
    return next(
        (table for table in tables if "Holding" in table.columns),
        None,
    )
