# Aliases
import pandas as pd

# Module imports
import os

# Package imports
from player_stats.abstract_base_dataset import AbstractBaseDataset
from helpers.string_helpers import convert_season_to_year


class CareerStats(AbstractBaseDataset):
    COLUMN_TYPES: dict[str:str] = {
        "Season": "category",
        "Tm": "category",
        "PTS": "float",
        "AST": "float",
        "TRB": "float",
        "FT": "float",
        "3PA": "float",
        "3P": "float",
        "FGA": "float",
        "FG": "float",
        "STL": "float",
    }

    DESIRED_COLUMNS: list[str] = list(COLUMN_TYPES.keys()) + ["PA", "PR", "RA", "PRA"]

    STAT_AUGMENTATIONS: dict[str:str] = {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
    }

    _exception_msgs = {
        "load_data": f"Error reading saved player overview from csv.",
        "download_data": f"Error fetching (http) player overview from html.",
    }

    def __init__(self, *, player_id: str) -> None:
        super().__init__(player_id=player_id)

    @property
    def download_url(self):
        return f"http://www.basketball-reference.com/players/{self.player_initial}/{self.player_id}.html"

    @property
    def save_path(self):
        return os.path.join("player_data", "career_stats", self.player_initial)

    def generate_exception_msg(self, *, exception_type: str) -> str:
        exception_msg = super().generate_exception_msg(exception_type=exception_type)
        return exception_msg + f"{{ id: {self.player_id}}}"

    def select_dataset_from_html_tables(
        self, *, datasets: list[pd.DataFrame]
    ) -> pd.DataFrame:
        # Filter the dataframe to get the career stats dataframe
        season_stat_datasets: list[pd.DataFrame] = list(
            filter(lambda dataset: "Season" in dataset.columns, datasets)
        )
        return season_stat_datasets[0]
        # return datasets

    def get_active_seasons(self) -> list[int]:
        try:
            # Filter the career stats to contain just the season averages
            season_stats: pd.DataFrame = self.data[
                self.data["Season"].str.contains("^\d{4}") == True
            ]
            season_stats: pd.DataFrame = season_stats.dropna()

            # Delete duplicate seasons (player played for multiple teams in same season)
            season_stats: pd.DataFrame = season_stats.drop_duplicates(subset="Season")

            # Get the seasons active by converting seasons column to a value list
            seasons_active: list[str] = season_stats["Season"].to_list()
            seasons_active: list[int] = list(
                map(
                    lambda season: convert_season_to_year(season=season), seasons_active
                )
            )
        except Exception as e:
            print(self.data)
            raise e

        return seasons_active


if __name__ == "__main__":
    player_info: CareerStats = CareerStats(player_id="johnsja01")
    data: pd.DataFrame = player_info.download_data()
    print(data)
