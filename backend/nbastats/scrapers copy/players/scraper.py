import logging

import pandas as pd
from base.scraper import BaseScraper

from .dataset_config import (
    CareerStatsDatasetConfig,
    CareerStatsTableConfig,
    GamelogDatasetConfig,
    GamelogTableConfig,
    PlayerInfoDatasetConfig,
    PlayerInfoTableConfig,
)


def get_team_id_from_career_stats(career_stats_data: pd.DataFrame) -> pd.DataFrame:
    career_stats_data = (
        career_stats_data.sort_values("Season").groupby("player_id").tail(1)
    )
    career_stats_data = career_stats_data.rename(columns={"Tm_id": "team_id"})
    data = career_stats_data[["player_id", "team_id"]]
    data = data.set_index("player_id")

    return data


player_scraper = BaseScraper(name="PlayerScraper", log_level=logging.INFO)

player_table_config = PlayerInfoTableConfig(name="PlayerInfos")
career_stats_table_config = CareerStatsTableConfig(name="CareerStats")
gamelogs_table_config = GamelogTableConfig(name="Gamelogs")

player_dataset_config = PlayerInfoDatasetConfig(name="PlayersConfig")
player_dataset_config.add_table_config(table_config=player_table_config)

career_stats_dataset_config = CareerStatsDatasetConfig(name="CareerStatsConfig")
career_stats_dataset_config.add_table_config(table_config=career_stats_table_config)

gamelog_dataset_config = GamelogDatasetConfig(name="GamelogsConfig")
gamelog_dataset_config.add_table_config(table_config=gamelogs_table_config)


career_stats_dataset_config.add_dependency(
    source=player_dataset_config,
    meta_data={
        "table_name": "PlayerInfos",
        "query_set_provider": lambda dataset: [
            {"player_last_initial": player_id[0], "player_id": player_id}
            for player_id in dataset.index.values
        ],
    },
)

gamelog_dataset_config.add_dependency(
    source=career_stats_dataset_config,
    meta_data={
        "table_name": "CareerStats",
        "query_set_provider": lambda dataset: [
            {
                "player_last_initial": row["player_id"][0],
                "player_id": row["player_id"],
                "year": row["Season"],
            }
            for index, row in dataset[["player_id", "Season"]].iterrows()
        ],
    },
)

player_table_config.add_inheritance(
    source=career_stats_table_config,
    inheritance_function=get_team_id_from_career_stats,
)


player_scraper.add_dataset_config(gamelog_dataset_config)
player_scraper.add_dataset_config(player_dataset_config)
player_scraper.add_dataset_config(career_stats_dataset_config)

# print(player_info_scraper._dataset_configs)
# for dataset_config in player_info_scraper._dataset_configs.values():
#     print(dataset_config._table_configs)

# player_info_scraper.configure()

# print(player_info_scraper._dataset_configs)
# for dataset_config in player_info_scraper._dataset_configs.values():
#     print(dataset_config._table_configs)
