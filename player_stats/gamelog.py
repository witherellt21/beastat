import os
import pandas as pd

from player_stats.abstract_base_dataset import AbstractBaseDataset

class Gamelog(AbstractBaseDataset):
    COLUMN_TYPES: dict[str: str] = {
        "Tm": "category", "Opp": "category", "PTS": "float", 
        "AST": "float", "TRB": "float", "FT": "float", "3PA": "float", 
        "3P": "float", "FGA": "float", "FG": "float", "STL": "float"
    }
    DATETIME_COLUMNS: dict[str: str] = {
        "Date": "%Y-%m-%d", "MP": "%M:%S"
    }
    STAT_AUGMENTATIONS: dict[str: str] = {
        "PA": "PTS+AST", "PR":"PTS+TRB", "RA":"TRB+AST", "PRA":"PTS+TRB+AST"
    }
    DESIRED_COLUMNS: list[str] = [
        "Date", "Tm", "Opp", "MP", 
        "PTS", "AST", "TRB", "FT", 
        "3PA", "3P", "FGA", "FG", 
        "PA", "RA", "PRA"
    ]
    
    def __init__(self, *, player_id: str, year: int):
        super().__init__(player_id=player_id)

        self.year = year

    @property
    def download_url(self):
        return f"http://www.basketball-reference.com/players/{self.player_initial}/{self.player_id}/gamelog/{self.year}"

    @property
    def save_path(self):
        return os.path.join("player_data", "gamelogs", self.player_initial, self.player_id)
    
    @property
    def save_file(self) -> str:
        return os.path.join(self.full_save_path, f"{self.year}.csv")
    
    def select_dataset_from_html_tables(self, *, datasets: list[pd.DataFrame]) -> pd.DataFrame:
        return list(filter(lambda x: x.shape[1] == 30, datasets))[0]
    
    def clean(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # Remove extra column rows from dataset
        data: pd.DataFrame = data[data["Rk"] != "Rk"]

        # Reset the index to all games where player was rostered this season, including Inactive games
        data: pd.DataFrame = data.set_index("Rk")

        return super().clean(data=data)
