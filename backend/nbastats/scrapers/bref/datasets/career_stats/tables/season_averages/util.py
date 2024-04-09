import uuid
from typing import Optional

import numpy as np
import pandas as pd
from core.scraper import (
    BaseHTMLTableSerializer,
    CharField,
    FloatField,
    IntegerField,
    QueryArgField,
    QueryArgs,
    RenameField,
    TransformationField,
)
from lib.util import sum_nullables
from nbastats.lib.string_helpers import convert_season_to_year
from nbastats.sql_app.register import SeasonAveragess, Teams


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


class SeasonAveragesTableEntrySerializer(BaseHTMLTableSerializer):
    id = CharField(default=uuid.uuid4)
    player_id = QueryArgField()
    Season = TransformationField(int, convert_season_to_year)
    Age = FloatField()
    Tm_id = TransformationField(
        str,
        lambda abbr: Teams.get_team_id_or_nan(abbr, raise_exception=True),
        from_columns=["Tm"],
        replace_values={"TOT": np.nan},
    )
    Lg = CharField(null=True)
    Pos = CharField(null=True)
    G = CharField()
    GS = IntegerField(null=True)
    MP = FloatField(null=True)
    FG = FloatField(null=True)
    FGA = FloatField(null=True)
    FG_perc = RenameField("FG%", type=float, null=True, replace_values={"": np.nan})
    eFG_perc = RenameField("eFG%", type=float, null=True, replace_values={"": np.nan})
    TWP = RenameField("2P", type=float, null=True)
    TWPA = RenameField("2PA", type=float, null=True)
    TWP_perc = RenameField("2P%", type=float, null=True, replace_values={"": np.nan})
    THP = RenameField("3P", type=float, null=True)
    THPA = RenameField("3PA", type=float, null=True)
    THP_perc = RenameField("3P%", type=float, null=True, replace_values={"": np.nan})
    FT = FloatField(null=True)
    FTA = FloatField(null=True)
    FT_perc = RenameField(
        "FT%", type=float, null=True, replace_values={"": np.nan}
    )  # TODO: Add to model
    ORB = FloatField(null=True)
    DRB = FloatField(null=True)
    TRB = FloatField(null=True)
    AST = FloatField(null=True)
    STL = FloatField(null=True)
    BLK = FloatField(null=True)
    TOV = FloatField(null=True)
    PF = FloatField(null=True)
    PTS = FloatField(null=True)
    # plus_minus = RenameField("+/-", type=float, null=True)  # TODO: exists?
    PA = TransformationField(
        float,
        lambda row: sum_nullables(row["PTS"], row["AST"]),
        null=True,
        from_columns=["PTS", "AST"],
    )
    PR = TransformationField(
        float,
        lambda row: sum_nullables(row["PTS"], row["TRB"]),
        null=True,
        from_columns=["PTS", "TRB"],
    )
    RA = TransformationField(
        float,
        lambda row: sum_nullables(row["TRB"], row["AST"]),
        null=True,
        from_columns=["TRB", "AST"],
    )
    PRA = TransformationField(
        float,
        lambda row: sum_nullables(row["PTS"], row["TRB"], row["AST"]),
        null=True,
        from_columns=["PTS", "TRB", "AST"],
    )

    Awards = CharField(null=True)
