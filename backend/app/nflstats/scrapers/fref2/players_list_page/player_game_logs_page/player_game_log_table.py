import numpy as np
import pandas as pd
from scrapp.core.dataframes import BaseDataframeValidator
from scrapp.core.dataframes.serializers import (
    BooleanField,
    CharField,
    DatetimeField,
    FloatField,
    IntegerField,
    StaticField,
    TransformationField,
)
from scrapp.scraper import DataframeController
from scrapp.tables import schema
from scrapp.utils import dates, percentages

from ..util import extract_team_from_team_link

# from .ex_data import ex_data
from .util import (
    convert_age_to_age_days,
    convert_age_to_age_years,
    convert_GS_to_start_bool,
    convert_home_away,
    convert_result_to_opp_pts,
    convert_result_to_team_pts,
    convert_result_to_win_loss_tie,
)


class FRefPlayerGameLogDataframeValidator(BaseDataframeValidator):
    player_id = StaticField(str)
    date = DatetimeField(
        "%Y-%m-%d", from_column="Unnamed_Date", groups=("GameFigures",)
    )
    week = IntegerField(
        from_column="Unnamed_Week",
        replace_values={"": np.nan},
        null=True,
        groups=("GameFigures",),
    )
    age_years = TransformationField(
        int,
        convert_age_to_age_years,
        ["Unnamed_Age"],
        groups=("GameFigures",),
    )
    age_days = TransformationField(
        int,
        convert_age_to_age_days,
        ["Unnamed_Age"],
        groups=("GameFigures",),
    )
    team_id = TransformationField(
        str,
        extract_team_from_team_link,
        from_columns=["Unnamed_Tm_link"],
        groups=("GameFigures",),
    )
    home = TransformationField(
        bool,
        convert_home_away,
        ["Unnamed_Unnamed"],
        groups=("GameFigures",),
    )
    opp_id = TransformationField(
        str,
        extract_team_from_team_link,
        from_columns=["Unnamed_Opp_link"],
        groups=("GameFigures",),
    )
    result = TransformationField(
        str,
        convert_result_to_win_loss_tie,
        ["Unnamed_Result"],
        groups=("GameFigures",),
    )
    team_pts = TransformationField(
        int,
        convert_result_to_team_pts,
        ["Unnamed_Result"],
        groups=("GameFigures",),
    )
    opp_pts = TransformationField(
        int,
        convert_result_to_opp_pts,
        ["Unnamed_Result"],
        groups=("GameFigures",),
    )
    start = TransformationField(
        bool,
        convert_GS_to_start_bool,
        ["Unnamed_GS"],
        null=True,
        groups=("GameFigures",),
    )

    # Should all be null if the player did not play any offensive snaps
    pass_cmp = IntegerField(
        from_column="Passing_Cmp",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Passing",),
    )
    pass_att = IntegerField(
        from_column="Passing_Att",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Passing",),
    )
    pass_cmp_pct = FloatField(
        from_column="Passing_Cmp%",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Passing",),
    )
    pass_yds = IntegerField(
        from_column="Passing_Yds",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Passing",),
    )
    pass_tds = IntegerField(
        from_column="Passing_TD",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Passing",),
    )
    pass_ints = IntegerField(
        from_column="Passing_Int",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Passing",),
    )
    pass_rtng = FloatField(
        from_column="Passing_Rate",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Passing",),
    )
    pass_scks = IntegerField(
        from_column="Passing_Sk",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Passing",),
    )
    pass_scks_yds = IntegerField(
        from_column="Passing_Yds.1",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Passing",),
    )
    pass_yds_per_att = FloatField(
        from_column="Passing_Y/A",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Passing",),
    )
    pass_yds_per_att_adj = FloatField(
        from_column="Passing_AY/A",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Passing",),
    )

    rec_tgts = IntegerField(
        from_column="Receiving_Tgt",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Receiving",),
    )
    rec_recs = IntegerField(
        from_column="Receiving_Rec",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Receiving",),
    )
    rec_yds = IntegerField(
        from_column="Receiving_Yds",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Receiving",),
    )
    rec_yds_per_rec = FloatField(
        from_column="Receiving_Y/R",
        replace_values={"": np.nan},
        default=np.nan,
        null=True,
        groups=("Receiving",),
    )
    rec_tds = IntegerField(
        from_column="Receiving_TD",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Receiving",),
    )
    rec_catch_pct = TransformationField(
        float,
        percentages.strppct,
        ["Receiving_Ctch%"],
        null=True,
        default=np.nan,
        groups=("Receiving",),
    )
    rec_yds_per_tgt = FloatField(
        from_column="Receiving_Y/Tgt",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Receiving",),
    )

    rush_att = IntegerField(
        from_column="Rushing_Att",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Rushing",),
    )
    rush_yds = IntegerField(
        from_column="Rushing_Yds",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Rushing",),
    )
    rush_yds_per_att = FloatField(
        from_column="Rushing_Y/A",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Rushing",),
    )
    rush_tds = IntegerField(
        from_column="Rushing_TD",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Rushing",),
    )

    kickret_rts = IntegerField(
        from_column="Kick Returns_Rt",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Kick Returns",),
    )
    kickret_yds = IntegerField(
        from_column="Kick Returns_Yds",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Kick Returns",),
    )
    kickret_yds_per_rt = FloatField(
        from_column="Kick Returns_Y/Rt",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Kick Returns",),
    )
    kickret_tds = IntegerField(
        from_column="Kick Returns_TD",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Kick Returns",),
    )

    puntret_rts = IntegerField(
        from_column="Punt Returns_Ret",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Punt Returns",),
    )
    puntret_yds = IntegerField(
        from_column="Punt Returns_Yds",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Punt Returns",),
    )
    puntret_yds_per_rt = FloatField(
        from_column="Punt Returns_Y/R",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Punt Returns",),
    )
    puntret_tds = IntegerField(
        from_column="Punt Returns_TD",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Punt Returns",),
    )

    two_pts = IntegerField(
        from_column="Scoring_2PM",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Scoring",),
    )
    td_tot = IntegerField(
        from_column="Scoring_TD", null=True, default=np.nan, groups=("Scoring",)
    )
    pts_tot = IntegerField(
        from_column="Scoring_Pts", null=True, default=np.nan, groups=("Scoring",)
    )

    # Should be nan if the player did not play any defensive snaps
    def_scks = FloatField(
        from_column=("Unnamed_Sk",),
        null=True,
        default=np.nan,
        groups=("Defensive Tackles",),
    )
    def_tcks_tfls = IntegerField(
        from_column="Tackles_TFL",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Defensive Tackles",),
    )
    def_tcks_qbhits = IntegerField(
        from_column="Tackles_QBHits",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Defensive Tackles",),
    )

    # Interceptions group
    def_ints = IntegerField(
        from_column="Def Interceptions_Int",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Interceptions", "Pass Defense"),
    )
    def_ints_yds = IntegerField(
        from_column="Def Interceptions_Yds",
        replace_values={"": np.nan},
        null=True,
        default=np.nan,
        groups=("Interceptions", "Pass Defense"),
    )
    def_ints_tds = IntegerField(
        from_column="Def Interceptions_TD",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Interceptions", "Pass Defense"),
    )
    def_pass_def = IntegerField(
        from_column="Def Interceptions_PD",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Pass Defense",),
    )

    # These could theoretically happen if a ball is turned over and still live so they are not tied to the def. snaps
    tcks_solo = IntegerField(
        from_column="Tackles_Solo",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Tackles",),
    )
    tcks_ast = IntegerField(
        from_column="Tackles_Ast",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Tackles",),
    )
    tcks = IntegerField(
        from_column="Tackles_Comb",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Tackles",),
    )

    fmbs = IntegerField(
        from_column="Fumbles_Fmb",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Fumbles",),
    )
    fmbs_lost = IntegerField(
        from_column="Fumbles_FL",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Fumbles",),
    )
    fmbs_forced = IntegerField(
        from_column="Fumbles_FF",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Fumbles",),
    )
    fmbs_rcovd = IntegerField(
        from_column="Fumbles_FR",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Fumbles",),
    )
    fmbs_yds = IntegerField(
        from_column="Fumbles_Yds",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Fumbles",),
    )
    fmbs_TD = IntegerField(
        from_column="Fumbles_TD",
        null=True,
        replace_values={"": 0},
        default=np.nan,
        groups=("Fumbles",),
    )

    offsnaps_num = IntegerField(
        from_column="Off. Snaps_Num",
        null=True,
        replace_values={"": np.nan},
        groups=("Snap Counts",),
    )
    offsnaps_pct = TransformationField(
        int,
        percentages.strppct,
        ["Off. Snaps_Pct"],
        null=True,
        replace_values={"": np.nan},
        groups=("Snap Counts",),
    )

    defsnaps_num = IntegerField(
        from_column="Def. Snaps_Num",
        null=True,
        replace_values={"": np.nan},
        groups=("Snap Counts",),
    )
    defsnaps_pct = TransformationField(
        int,
        percentages.strppct,
        ["Def. Snaps_Pct"],
        null=True,
        replace_values={"": np.nan},
        groups=("Snap Counts",),
    )

    # Defensive special teams snaps
    stsnaps_num = IntegerField(
        from_column="ST Snaps_Num",
        null=True,
        replace_values={"": np.nan},
        groups=("Snap Counts",),
    )
    stsnaps_pct = TransformationField(
        int,
        percentages.strppct,
        ["ST Snaps_Pct"],
        null=True,
        replace_values={"": np.nan},
        groups=("Snap Counts",),
    )

    status = CharField(
        from_column=("Unnamed_Status",),
        null=True,
        default=np.nan,
    )

    dnp = BooleanField()
    out = BooleanField()
    sspd = BooleanField()

    NAN_VALUES = [
        r"Inactive",
        r"Injured Reserve",
        r"Did Not Play",
        r"COVID",
        r"Suspended",
    ]

    class Meta:
        groups = {
            "Offense": ("Passing", "Receiving", "Rushing"),
            "Defense": ("Defensive Tackles", "Pass Defense"),
            "Special Teams": ("Kick Returns", "Punt Returns"),
            "Player Stats": (
                "Offense",
                "Defense",
                "Special Teams",
                "Tackles",
                "Fumbles",
                "Snap Counts",
                "status",
            ),
        }

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[~df["Unnamed_Rk"].isin(["Rk", np.nan])].reset_index(drop=True)

        date_col = self.date.from_column[0]
        age_col = self.age_years.from_columns[0]
        start_col = self.start.from_columns[0]

        df["dnp"] = df[start_col].str.startswith("Did Not Play")
        df["out"] = df[start_col].str.startswith(("Injured", "Inactive", "COVID"))
        df["sspd"] = df[start_col].str.startswith(("Suspended"))

        # Calculate birthday base on the first row with existing age and date data
        first_age_row = df[df[age_col] != ""].iloc[0]
        birthday = dates.age_to_birthday(
            first_age_row[age_col], first_age_row[date_col]
        )

        # Fix all missing age cells by back calulating the age using the birthday
        # and date
        idx = 0
        for _, row in df[[date_col, age_col]].iterrows():
            if row[age_col] == "":
                df.loc[idx, age_col] = dates.birthday_to_age(birthday, row[date_col])

            idx += 1

        return super().preprocess(df)

    def postprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        # fill all defense fields with nan if the number of defensive snaps is 0
        df.loc[df["defsnaps_num"] == 0, list(self.group("Defense"))] = np.nan
        df.loc[df["offsnaps_num"] == 0, list(self.group("Offense"))] = np.nan
        df.loc[
            df["pass_att"] == 0, list(self.group("Passing").difference(("pass_att",)))
        ] = np.nan
        df.loc[
            (df["dnp"] == True) | (df["out"] == True), list(self.group("Player Stats"))
        ] = np.nan

        return df


table = DataframeController(
    "FrefPlayerGameLogs",
    FRefPlayerGameLogDataframeValidator(),
    db_table=schema.table("nflplayergamelogs"),
)
