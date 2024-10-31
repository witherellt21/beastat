import numpy as np
from scrapp.core.dataframes.serializers.fields import (
    CharField,
    IntegerField,
    StaticField,
    TransformationField,
)
from scrapp.scraper import DataframeController
from scrapp.tables import schema

from ..util import extract_team_from_team_link
from .base import BaseSplitsDataframeValidator
from .util import extract_season_as_int_or_none


class OffensiveLinePenaltiesSplitsDataframeValidator(BaseSplitsDataframeValidator):
    player_id = StaticField(str)
    season = TransformationField(
        int, extract_season_as_int_or_none, from_columns=["Year"]
    )
    age = IntegerField(from_column="Age")
    team_id = TransformationField(
        str,
        extract_team_from_team_link,
        from_columns=["Tm_link"],
    )

    pos = CharField(from_column="Pos")
    gp = IntegerField(from_column="G", replace_values={"0": np.nan})
    gs = IntegerField(from_column="GS")

    holding = IntegerField(from_column="Holding")
    false_start = IntegerField(from_column="False Start")
    voided = IntegerField(from_column="Decl/Offs")
    pen_tot = IntegerField(from_column="All Pen.")


table = DataframeController(
    "NFLOffensiveLinePenaltiesSplits",
    OffensiveLinePenaltiesSplitsDataframeValidator(),
    db_table=schema.table("nfloffensivelinepenaltiessplits"),
)
