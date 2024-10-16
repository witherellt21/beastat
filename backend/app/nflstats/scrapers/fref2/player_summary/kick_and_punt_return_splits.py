from os import replace
from typing import Optional

import numpy as np
import pandas as pd
from scrapp.scraper import BaseHTMLTable
from scrapp.scraper.fields import (
    FloatField,
    IntegerField,
    QueryArgField,
    RenameField,
    TransformationField,
)
from scrapp.scraper.html_table_serializer import BaseHTMLTableSerializer
from scrapp.tables import schema

from .util import extract_season_as_int_or_none, get_team_id_by_abbr_or_none


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


class KickAndPuntReturnSplitsTableEntrySerializer(BaseHTMLTableSerializer):
    player_id = QueryArgField()
    season = TransformationField(
        int, extract_season_as_int_or_none, from_columns=["Unnamed: 0_level_0_Year"]
    )
    age = RenameField("Unnamed: 1_level_0_Age", type=int)
    team_id = TransformationField(
        str,
        get_team_id_by_abbr_or_none,
        from_columns=["Unnamed: 2_level_0_Tm"],
    )
    pos = RenameField("Unnamed: 3_level_0_Pos", type=str)
    gp = RenameField("Games_G", type=int)
    pr = IntegerField(from_column="Punt Returns_Ret", replace_values={"": 0})
    pr_yards = IntegerField(from_column="Punt Returns_Yds", replace_values={"": 0})
    pr_tds = IntegerField(from_column="Punt Returns_TD", replace_values={"": 0})
    pr_long = IntegerField(from_column="Punt Returns_Lng", replace_values={"": 0})
    pr_yards_avg = FloatField(
        from_column="Punt Returns_Y/R", replace_values={"": np.nan}, null=True
    )
    kr = IntegerField(from_column="Kick Returns_Rt", replace_values={"": 0})
    kr_yards = IntegerField(from_column="Kick Returns_Yds", replace_values={"": 0})
    kr_tds = IntegerField(from_column="Kick Returns_TD", replace_values={"": 0})
    kr_long = IntegerField(from_column="Kick Returns_Lng", replace_values={"": 0})
    kr_yards_avg = FloatField(
        from_column="Kick Returns_Y/Rt", replace_values={"": np.nan}, null=True
    )


kick_and_punt_return_splits_table = BaseHTMLTable(
    "NFLKickAndPuntReturnsSplits",
    schema.table("nflkickandpuntreturnsplits"),
    KickAndPuntReturnSplitsTableEntrySerializer(),
    identification_function=has_regular_season_return_data,
)
