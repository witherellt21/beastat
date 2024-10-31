from typing import Optional

import numpy as np
import pandas as pd
from scrapp.core.dataframes.serializers import (
    CharField,
    FloatField,
    IntegerField,
    StaticField,
    TransformationField,
)
from scrapp.scraper.html_table import DataframeController
from scrapp.tables import schema

from ..util import extract_team_from_team_link
from .base import BaseSplitsDataframeValidator
from .util import extract_season_as_int_or_none


def parse_qb_record(record: str) -> Optional[pd.Series]:
    if record == "":
        return None

    wins, losses, ties = record.split("-")

    return pd.Series([wins, losses, ties])


def parse_qb_wins(record_str: str):
    record = parse_qb_record(record_str)

    return record[0] if record is not None else None


def parse_qb_losses(record_str: str):
    record = parse_qb_record(record_str)

    return record[1] if record is not None else None


def parse_qb_ties(record_str: str):
    record = parse_qb_record(record_str)

    return record[2] if record is not None else None


class NFLPassingSplitsDataframeValidator(BaseSplitsDataframeValidator):
    # Overrides
    player_id = StaticField(str)
    season = TransformationField(
        int, extract_season_as_int_or_none, from_columns=["Season"]
    )
    age = IntegerField(from_column="Age")
    team_id = TransformationField(
        str,
        extract_team_from_team_link,
        from_columns=["Team_link"],
    )
    pos = CharField(from_column="Pos")
    gp = IntegerField(from_column="G", replace_values={"0": np.nan})
    gs = IntegerField(from_column="GS")

    wins = TransformationField(
        int,
        parse_qb_wins,
        from_columns=["QBrec"],
    )
    losses = TransformationField(
        int,
        parse_qb_losses,
        from_columns=["QBrec"],
    )
    ties = TransformationField(
        int,
        parse_qb_ties,
        from_columns=["QBrec"],
    )

    comp = IntegerField(from_column="Cmp")
    att = IntegerField(from_column="Att")
    comp_perc = FloatField(from_column="Cmp%")
    yds = IntegerField(from_column="Yds")
    tds = IntegerField(from_column="TD")
    td_perc = FloatField(from_column="TD%")
    ints = IntegerField(from_column="Int")
    int_perc = FloatField(from_column="Int%")
    fds = IntegerField(from_column="1D")
    succ_rate = FloatField(from_column="Succ%", replace_values={"": 0})
    long = IntegerField(from_column="Lng", replace_values={"": 0})
    yds_per_att = FloatField(from_column="Y/A")
    yds_per_att_adj = FloatField(from_column="AY/A")
    yds_per_comp = FloatField(from_column="Y/C")
    yds_per_gp = FloatField(from_column="Y/G")
    rating = FloatField(from_column="Rate")
    qbr = FloatField(from_column="QBR", replace_values={"": 0})
    sacks = IntegerField(from_column="Sk")
    sack_yds = IntegerField(from_column="Yds.1")
    sack_perc = FloatField(from_column="Sk%")
    yds_per_att_net = FloatField(from_column="NY/A")
    yds_per_att_net_adj = FloatField(from_column="NY/A")
    cbs = IntegerField(from_column="4QC")
    gwds = IntegerField(from_column="GWD")
    value = IntegerField(from_column="AV", replace_values={"": 0})


table = DataframeController(
    "NFLPassingSplits",
    NFLPassingSplitsDataframeValidator(),
    db_table=schema.table("nflpassingsplits"),
)
