import numpy as np
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


class KickAndPuntReturnSplitsDataframeValidator(BaseSplitsDataframeValidator):

    player_id = StaticField(str)
    season = TransformationField(
        int, extract_season_as_int_or_none, from_columns=["Unnamed_Year"]
    )
    age = IntegerField(from_column="Unnamed_Age")
    team_id = TransformationField(
        str,
        extract_team_from_team_link,
        from_columns=["Unnamed_Tm_link"],
    )
    pos = CharField(from_column="Unnamed_Pos")
    gp = IntegerField(from_column="Games_G", replace_values={"0": np.nan})

    pr = IntegerField(from_column="Punt Returns_Ret", replace_values={"": 0})
    pr_yards = IntegerField(from_column="Punt Returns_Yds", replace_values={"": 0})
    pr_tds = IntegerField(
        from_column=("Punt Returns_TD", "Punt Returns_PRTD"), replace_values={"": 0}
    )
    pr_long = IntegerField(from_column="Punt Returns_Lng", replace_values={"": 0})
    pr_yards_avg = FloatField(
        from_column="Punt Returns_Y/R", replace_values={"": np.nan}, null=True
    )
    kr = IntegerField(from_column="Kick Returns_Rt", replace_values={"": 0})
    kr_yards = IntegerField(from_column="Kick Returns_Yds", replace_values={"": 0})
    kr_tds = IntegerField(
        from_column=("Kick Returns_TD", "Kick Returns_KRTD"), replace_values={"": 0}
    )
    kr_long = IntegerField(from_column="Kick Returns_Lng", replace_values={"": 0})
    kr_yards_avg = FloatField(
        from_column="Kick Returns_Y/Rt", replace_values={"": np.nan}, null=True
    )


# TODO: dataframe validators __init__ actions should be moved to __init_subclass__
# and init actions should accept data and validate them outputting the object

table = DataframeController(
    "NFLKickAndPuntReturnsSplits",
    KickAndPuntReturnSplitsDataframeValidator(),
    db_table=schema.table("nflkickandpuntreturnsplits"),
)
