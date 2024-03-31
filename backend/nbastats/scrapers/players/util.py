import pandas as pd


def get_team_id_from_career_stats(career_stats_data: pd.DataFrame) -> pd.DataFrame:
    career_stats_data = (
        career_stats_data.sort_values("Season").groupby("player_id").tail(1)
    )
    career_stats_data = career_stats_data.rename(columns={"Tm_id": "team_id"})
    data = career_stats_data[["player_id", "team_id"]]
    data = data.set_index("player_id")

    return data
