import logging

from base.scraper import BaseScraper

from .dataset_config import PlayerPropsDatasetConfig, PlayerPropsTableConfig

player_props_scraper = BaseScraper(log_level=logging.DEBUG, download_rate=2)

player_props_dataset_config = PlayerPropsDatasetConfig(name="PlayerPropsDataset")
player_props_table_config = PlayerPropsTableConfig(name="PlayerPropsTable")

player_props_dataset_config.add_table_config(table_config=player_props_table_config)
player_props_scraper.add_dataset_config(dataset_config=player_props_dataset_config)
