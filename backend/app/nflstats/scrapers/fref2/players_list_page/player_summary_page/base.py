import pandas as pd
from scrapp.core.dataframes import BaseDataframeValidator
from scrapp.core.dataframes.serializers.fields import (
    CharField,
    IntegerField,
    StaticField,
    TransformationField,
)

from .util import extract_season_as_int_or_none, extract_team_from_team_link


class BaseSplitsDataframeValidator(BaseDataframeValidator):
    player_id = StaticField(str)
    season = TransformationField(
        int, extract_season_as_int_or_none, from_columns=["Unnamed: 0_level_0_Season"]
    )
    age = IntegerField(from_column="Unnamed: 1_level_0_Age")
    team_id = TransformationField(
        str,
        extract_team_from_team_link,
        from_columns=["Unnamed: 2_level_0_Team_link"],
    )

    pos = CharField(from_column="Unnamed: 4_level_0_Pos")
    gp = IntegerField(from_column="Unnamed: 5_level_0_G")

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Overrides to parse out split seasons where the player played for
        multiple teams.
        """
        team_column = self.team_id.from_columns[0].strip("_link")
        season_column = self.season.from_columns[0]

        age_column: str
        for column in self.age.from_column:
            if column in df.columns:
                age_column = column
                break

        split_seasons = 0
        for index, row in df.iterrows():
            # TODO: use regex to match the number
            cur_team = row[team_column]
            if isinstance(cur_team, str) and cur_team.endswith("TM"):
                split_seasons = int(cur_team[0])
                season = row[season_column]
                age = row[age_column]
                df = df.drop(index)

            elif split_seasons:
                if not df.loc[index, season_column]:  # type: ignore
                    df.loc[index, season_column] = season  # type: ignore

                if not df.loc[index, age_column]:  # type: ignore
                    df.loc[index, age_column] = age  # type: ignore

                split_seasons -= 1

        return super().preprocess(df)
