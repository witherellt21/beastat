import logging

from scraper.base import BaseScraper

from .dataset_config import (
    GameTableConfig,
    LineupTableConfig,
    MatchupTableConfig,
    TodaysGamesDatasetConfig,
)

todays_games_scraper = BaseScraper(log_level=logging.DEBUG, download_rate=3)
todays_games_dataset_config = TodaysGamesDatasetConfig(name="TodaysGamesDataset")

gamelog_table_config = GameTableConfig()
matchup_table_config = MatchupTableConfig()
lineup_table_config = LineupTableConfig()

todays_games_dataset_config.add_table_config(table_config=gamelog_table_config)
todays_games_dataset_config.add_table_config(table_config=matchup_table_config)
todays_games_dataset_config.add_table_config(table_config=lineup_table_config)

lineup_table_config.add_dependency(source=gamelog_table_config)
matchup_table_config.add_dependency(source=lineup_table_config)

todays_games_scraper.add_dataset_config(dataset_config=todays_games_dataset_config)

# print(todays_games_scraper._dataset_configs)
# for dataset_config in todays_games_scraper._dataset_configs.values():
#     print(dataset_config._table_configs)

# todays_games_scraper.configure()

# print(todays_games_scraper._dataset_configs)
# for dataset_config in todays_games_scraper._dataset_configs.values():
#     print(dataset_config._table_configs)
