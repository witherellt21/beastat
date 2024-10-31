import numpy as np
from pandas import DataFrame
from scrapp.core.dataframes.serializers.fields import (
    CharField,
    FloatField,
    IntegerField,
    StaticField,
    TransformationField,
)
from scrapp.scraper import DataframeController
from scrapp.tables import schema

from ..util import extract_team_from_team_link
from .base import BaseSplitsDataframeValidator
from .util import extract_season_as_int_or_none


class DefensiveSplitsDataframeValidator(BaseSplitsDataframeValidator):
    player_id = StaticField(str)
    season = TransformationField(
        int, extract_season_as_int_or_none, from_columns=["Unnamed_Season"]
    )
    age = IntegerField(from_column="Unnamed_Age")
    team_id = TransformationField(
        str,
        extract_team_from_team_link,
        from_columns=["Unnamed_Team_link"],
    )

    pos = CharField(from_column="Unnamed_Pos")
    gp = IntegerField(from_column="Unnamed_G", replace_values={"0": np.nan})
    gs = IntegerField(from_column="Unnamed_GS")

    ints = IntegerField(from_column="Def Interceptions_Int", replace_values={"": 0})
    int_yds = IntegerField(from_column="Def Interceptions_Yds", replace_values={"": 0})
    int_tds = IntegerField(
        from_column="Def Interceptions_IntTD", replace_values={"": 0}
    )
    int_long = IntegerField(from_column="Def Interceptions_Lng", replace_values={"": 0})
    passes_def = IntegerField(
        from_column="Def Interceptions_PD", replace_values={"": 0}
    )

    fumb_forced = IntegerField(from_column="Fumbles_FF")
    fumb = IntegerField(from_column="Fumbles_Fmb")
    fumb_rec = IntegerField(from_column="Fumbles_FR")
    fumb_yds = IntegerField(from_column="Fumbles_Yds")
    fumb_tds = IntegerField(from_column="Fumbles_FRTD")

    sack = FloatField(from_column="Unnamed_Sk", replace_values={"": 0})

    tack = IntegerField(from_column="Tackles_Comb", replace_values={"": 0})
    tack_solo = IntegerField(from_column="Tackles_Solo", replace_values={"": 0})
    tack_ast = IntegerField(from_column="Tackles_Ast", replace_values={"": 0})
    tack_fl = IntegerField(from_column="Tackles_TFL", replace_values={"": 0})
    tack_qb = IntegerField(from_column="Tackles_QBHits", replace_values={"": 0})

    safety = IntegerField(from_column="Unnamed_Sfty", replace_values={"": 0})
    value = IntegerField(from_column="Unnamed_AV", replace_values={"": 0}, default=0)


table = DataframeController(
    "NFLDefensiveSplits",
    DefensiveSplitsDataframeValidator(),
    db_table=schema.table("nfldefensivesplits"),
)
