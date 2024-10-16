from email.policy import default
from typing import Optional

import pandas as pd
from scrapp.scraper import BaseHTMLTable, BaseHTMLTableSerializer
from scrapp.scraper.fields import (
    CharField,
    FloatField,
    IntegerField,
    QueryArgField,
    TransformationField,
)
from scrapp.tables import schema

from .util import extract_season_as_int_or_none, get_team_id_by_abbr_or_none


def has_regular_season_receiving_column(
    tables: list[pd.DataFrame],
) -> Optional[pd.DataFrame]:
    return next(
        (
            table
            for table in tables
            if "Rushing" in table.columns.get_level_values(0)
            and "Receiving" in table.columns.get_level_values(0)
            and "AV" in table.columns.get_level_values(1)
        ),
        None,
    )


class RushingAndReceivingSplitsHTMLTableSerializer(BaseHTMLTableSerializer):
    player_id = QueryArgField()
    season = TransformationField(
        int, extract_season_as_int_or_none, from_columns=["Unnamed: 0_level_0_Season"]
    )
    age = IntegerField(from_column="Unnamed: 1_level_0_Age")
    team_id = TransformationField(
        str,
        get_team_id_by_abbr_or_none,
        from_columns=["Unnamed: 2_level_0_Team"],
    )
    pos = CharField(from_column="Unnamed: 4_level_0_Pos")
    gp = IntegerField(from_column="Unnamed: 5_level_0_G")
    gs = CharField(from_column="Unnamed: 6_level_0_GS")

    rush = IntegerField(from_column="Rushing_Att")
    rush_yds = IntegerField(from_column="Rushing_Yds")
    rush_tds = IntegerField(from_column="Rushing_TD")
    rush_fds = IntegerField(from_column="Rushing_1D", default=None, null=True)
    rush_succ_perc = FloatField(from_column="Rushing_Succ%", default=None, null=True)
    rush_long = IntegerField(from_column="Rushing_Lng", default=None, null=True)
    yds_per_carry = FloatField(from_column="Rushing_Y/A", default=None, null=True)
    rush_yds_per_game = FloatField(from_column="Rushing_Y/G", default=None, null=True)
    rush_per_game = FloatField(from_column="Rushing_A/G", default=None, null=True)

    targets = IntegerField(from_column="Receiving_Tgt", default=None, null=True)
    rec = IntegerField(from_column="Receiving_Rec")
    rec_yds = IntegerField(from_column="Receiving_Yds")
    yds_per_rec = FloatField(from_column="Receiving_Y/R", default=None, null=True)
    rec_tds = IntegerField(from_column="Receiving_TD")
    rec_fds = IntegerField(from_column="Receiving_1D", default=None, null=True)
    rec_succ_perc = FloatField(from_column="Receiving_Succ%", default=None, null=True)
    rec_long = IntegerField(from_column="Receiving_Lng", default=None, null=True)
    rec_per_game = FloatField(from_column="Receiving_R/G", default=None, null=True)
    rec_yds_per_game = FloatField(from_column="Receiving_Y/G", default=None, null=True)
    catch_perc = FloatField(from_column="Receiving_Ctch%", default=None, null=True)
    yds_per_target = FloatField(from_column="Receiving_Y/Tgt", default=None, null=True)


rushing_and_receiving_table = BaseHTMLTable(
    "NFLPlayerRushingAndReceivingSplits",
    schema.table("nflrushingandreceivingsplits"),
    RushingAndReceivingSplitsHTMLTableSerializer(),
    has_regular_season_receiving_column,
)
