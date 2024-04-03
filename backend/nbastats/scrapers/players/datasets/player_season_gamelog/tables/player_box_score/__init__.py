import uuid
from typing import Type

import numpy as np
from core.scraper.base.table_form import (
    AugmentationField,
    BaseTableForm,
    CharField,
    DatetimeField,
    FloatField,
    HTMLSaveField,
    QueryArgField,
    RenameField,
    TransformationField,
)
from core.util.nullables import sum_nullables
from nbastats.global_implementations import constants
from nbastats.scrapers.players.datasets.player_season_gamelog.tables.player_box_score.util import *
from nbastats.sql_app.register import PlayerBoxScores


class PlayerBoxScoreTableConfig(BaseTableForm):
    Rk = CharField(replace_values={"Rk": np.nan}, cache=False)
    id = CharField(default=uuid.uuid4)
    player_id = QueryArgField("player_id")
    G = CharField(replace_values={"": np.nan}, null=True)
    Date = DatetimeField(format="%Y-%m-%d", null=True)
    Age = CharField()
    home = TransformationField(
        str, lambda cell: cell != "@", from_columns=["Unnamed: 5"], null=True
    )
    game_id = TransformationField(
        str,
        get_game_id,
        from_columns=["Date", "Tm", "Opp", "home"],
        to_columns=["game_id"],
        null=True,
    )
    GS = CharField(null=True)
    MP = TransformationField(float, convert_minutes_to_float, null=True)
    FG = FloatField(null=True)
    FGA = FloatField(null=True)
    FG_perc = RenameField("FG%", type=float, null=True, replace_values={"": np.nan})
    THP = RenameField("3P", type=float, null=True)
    THPA = RenameField("3PA", type=float, null=True)
    THP_perc = RenameField("3P%", type=float, null=True, replace_values={"": np.nan})
    FT = FloatField(null=True)
    FTA = FloatField(null=True)
    FT_perc = RenameField("FT%", type=float, null=True, replace_values={"": np.nan})
    result = TransformationField(
        str,
        get_result_and_margin,
        from_columns=["Unnamed: 7"],
        to_columns=["result", "margin"],
    )
    ORB = FloatField(null=True)
    DRB = FloatField(null=True)
    TRB = FloatField(null=True)
    AST = FloatField(null=True)
    STL = FloatField(null=True)
    BLK = FloatField(null=True)
    TOV = FloatField(null=True)
    PF = FloatField(null=True)
    PTS = FloatField(null=True)
    GmSc = FloatField(null=True)
    plus_minus = RenameField("+/-", type=float, null=True)
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
    days_rest = AugmentationField(
        float,
        get_closest_games,
        null=True,
    )


NAME = "PlayerBoxScore"

SQL_TABLE = PlayerBoxScores

IDENTIFICATION_FUNCTION = has_30_columns

TABLE_SERIALIZER = PlayerBoxScoreTableConfig()

CONFIG = {
    # "filters": [],
    # "datetime_columns": {"Date": "%Y-%m-%d"},
    # "rename_columns": {
    #     "FT%": "FT_perc",
    #     "FG%": "FG_perc",
    #     "3P": "THP",
    #     "3PA": "THPA",
    #     "3P%": "THP_perc",
    #     "+/-": "plus_minus",
    # },
    # "rename_values": {
    #     "Rk": {"Rk": np.nan},
    #     "G": {"": np.nan},
    #     "TWP_perc": {"": np.nan},
    #     "THP_perc": {"": np.nan},
    #     "FT_perc": {"": np.nan},
    #     "FG_perc": {"": np.nan},
    # },
    # "transformations": {
    #     "MP": lambda x: convert_minutes_to_float(x),
    #     ("PTS", "id"): lambda x: uuid.uuid4(),
    #     ("Unnamed: 5", "home"): lambda cell: cell != "@",
    # },
    # "data_transformations": [get_result_and_margin],
    # "stat_augmentations": {
    #     # "PA": "PTS+AST",
    #     # "PR": "PTS+TRB",
    #     # "RA": "TRB+AST",
    #     # "PRA": "PTS+TRB+AST",
    #     "days_rest": get_days_rest,
    #     # "game_id": get_game_ids,
    # },
    "nan_values": constants.NAN_VALUES,
    # "query_save_columns": {"player_id": "player_id"},
    # "required_fields": ["Rk"],
    # "href_save_map": {},
    "cached_query_generator": get_cached_gamelog_query_data,
    # "column_ordering": ["player_id"]
}
