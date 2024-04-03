import uuid

import numpy as np
from base.scraper.base.table_entry_serializers import (
    BaseTableEntrySerializer,
    CharField,
    FloatField,
    IntegerField,
    QueryArgField,
    RenameField,
    TransformationField,
)
from base.util.nullables import sum_nullables
from nbastats.global_implementations import constants
from nbastats.global_implementations.string_helpers import convert_season_to_year
from nbastats.scrapers.players.datasets.career_stats.tables.season_averages.util import (
    get_cached_player_season_averages_data,
    has_season_column,
)
from nbastats.scrapers.util.team_helpers import get_team_id_by_abbr
from nbastats.sql_app.register import SeasonAveragess


class SeasonAveragesTableEntrySerializer(BaseTableEntrySerializer):
    id = CharField(default=uuid.uuid4)
    player_id = QueryArgField()
    Season = TransformationField(int, convert_season_to_year)
    Age = FloatField()
    Tm_id = TransformationField(
        str, get_team_id_by_abbr, from_columns=["Tm"], replace_values={"TOT": np.nan}
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
    # TWP: Optional[float]
    # TWPA: Optional[float]
    # TWP_perc: Optional[float]
    # eFG_perc: Optional[float]
    Awards = CharField(null=True)


NAME = "SeasonAverages"

SQL_TABLE = SeasonAveragess

IDENTIFICATION_FUNCTION = has_season_column

TABLE_SERIALIZER = SeasonAveragesTableEntrySerializer()

CONFIG = {
    # "stat_augmentations": {
    #     "PA": "PTS+AST",
    #     "PR": "PTS+TRB",
    #     "RA": "TRB+AST",
    #     "PRA": "PTS+TRB+AST",
    # },
    # "rename_columns": {
    #     # "FG%": "FG_perc",
    #     # "3P": "THP",
    #     # "3PA": "THPA",
    #     # "3P%": "THP_perc",
    #     # "2P": "TWP",
    #     # "2PA": "TWPA",
    #     # "2P%": "TWP_perc",
    #     "eFG%": "eFG_perc",
    #     # "FT%": "FT_perc",
    # },
    # "rename_values": {
    #     # "Tm": {"TOT": np.nan},
    #     # "TWP_perc": {"": np.nan},
    #     # "THP_perc": {"": np.nan},
    #     # "FT_perc": {"": np.nan},
    #     # "FG_perc": {"": np.nan},
    #     "eFG_perc": {"": np.nan},
    # },
    # "transformations": {
    #     # "Season": lambda season: convert_season_to_year(season=season),
    #     # ("PTS", "id"): lambda x: uuid.uuid4(),
    #     # ("Tm", "Tm_id"): get_team_id_by_abbr,
    # },
    "nan_values": constants.NAN_VALUES,
    # "data_transformations": [],
    # "query_save_columns": {"player_id": "player_id"},
    # "required_fields": ["Season", "G", "Tm"],
    "cached_query_generator": get_cached_player_season_averages_data,
}
