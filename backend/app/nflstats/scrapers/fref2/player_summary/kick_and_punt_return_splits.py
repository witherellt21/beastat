import numpy as np
import pandas as pd
from numpy import nan
from scrapp.core.dataframes import BaseDataframeValidator
from scrapp.core.dataframes.serializers.fields import (  # InheritedField,
    CharField,
    FloatField,
    IntegerField,
    StaticField,
    TransformationField,
)
from scrapp.scraper import DataframeController
from scrapp.tables import schema

from .rushing_and_receiving_splits import rushing_and_receiving_splits_table
from .util import extract_season_as_int_or_none, get_team_id_by_abbr_or_none


class KickAndPuntReturnSplitsTableEntrySerializer(BaseDataframeValidator):
    # receiving_yds = IntegerField(post_validated=True, from_column="rec_yds")

    player_id = StaticField()
    season = TransformationField(
        int, extract_season_as_int_or_none, from_columns=["Unnamed: 0_level_0_Year"]
    )
    age = IntegerField(from_column="Unnamed: 1_level_0_Age")
    team_id = TransformationField(
        str,
        get_team_id_by_abbr_or_none,
        from_columns=["Unnamed: 2_level_0_Tm"],
    )
    pos = CharField(from_column="Unnamed: 3_level_0_Pos")
    gp = IntegerField(from_column="Games_G")
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


kick_and_punt_return_splits_table = DataframeController(
    "NFLKickAndPuntReturnsSplits",
    KickAndPuntReturnSplitsTableEntrySerializer(),
    db_table=schema.table("nflkickandpuntreturnsplits"),
)

# kick_and_punt_return_splits_table.add_inheritance(
#     rushing_and_receiving_splits_table.data, ["rec_yds"]
# )


example_data = {
    ("Unnamed: 0_level_0", "Year"): {
        0: ("1982", "/years/1982/"),
        1: ("1988", "/years/1988/"),
        2: "Career",
        3: "6 yrs",
        4: "1 yr",
    },
    ("Unnamed: 1_level_0", "Age"): {
        0: ("23", None),
        1: ("29", None),
        2: "Career",
        3: "6 yrs",
        4: "1 yr",
    },
    ("Unnamed: 2_level_0", "Tm"): {
        0: ("PIT", "/teams/pit/1982.htm"),
        1: ("PHI", "/teams/phi/1988.htm"),
        2: nan,
        3: "PIT",
        4: "PHI",
    },
    ("Unnamed: 3_level_0", "Pos"): {
        0: ("RB", None),
        1: ("RB", None),
        2: nan,
        3: nan,
        4: nan,
    },
    ("Unnamed: 4_level_0", "No."): {
        0: ("34", None),
        1: ("32", None),
        2: nan,
        3: nan,
        4: nan,
    },
    ("Games", "G"): {0: ("6", None), 1: ("5", None), 2: "84", 3: "79", 4: "5"},
    ("Games", "GS"): {0: ("0", None), 1: ("0", None), 2: nan, 3: "64", 4: "0"},
    ("Punt Returns", "Ret"): {0: ("", None), 1: ("", None), 2: nan, 3: nan, 4: nan},
    ("Punt Returns", "Yds"): {0: ("", None), 1: ("", None), 2: nan, 3: nan, 4: nan},
    ("Punt Returns", "TD"): {0: ("0", None), 1: ("0", None), 2: "0", 3: "0", 4: "0"},
    ("Punt Returns", "Lng"): {0: ("", None), 1: ("", None), 2: nan, 3: nan, 4: nan},
    ("Punt Returns", "Y/R"): {0: ("", None), 1: ("", None), 2: nan, 3: nan, 4: nan},
    ("Kick Returns", "Rt"): {0: ("7", None), 1: ("5", None), 2: "12", 3: "7", 4: "5"},
    ("Kick Returns", "Yds"): {
        0: ("139", None),
        1: ("87", None),
        2: "226",
        3: "139",
        4: "87",
    },
    ("Kick Returns", "TD"): {0: ("0", None), 1: ("0", None), 2: "0", 3: "0", 4: "0"},
    ("Kick Returns", "Lng"): {
        0: ("46", None),
        1: ("31", None),
        2: "46",
        3: "46",
        4: "31",
    },
    ("Kick Returns", "Y/Rt"): {
        0: ("19.9", None),
        1: ("17.4", None),
        2: "18.8",
        3: "19.9",
        4: "17.4",
    },
    ("Unnamed: 17_level_0", "APYd"): {
        0: ("253", None),
        1: ("99", None),
        2: "4936",
        3: "4837",
        4: "99",
    },
    ("Unnamed: 18_level_0", "AV"): {
        0: ("1", None),
        1: ("0", None),
        2: "35",
        3: "35",
        4: "0",
    },
}

example_df = pd.DataFrame(example_data)
