# import logging

# from base.scraper import BaseScraper

# from . import datasets

# SCRAPER = BaseScraper(
#     name="PlayerPropsScraper", log_level=logging.INFO, download_rate=2
# )

# for dataset in datasets.__iter__():
#     print(dataset)
#     SCRAPER.add_dataset_config(dataset_config=dataset)
import logging

NAME = "PlayerPropsScraper"
CONFIG = {"log_level": logging.INFO, "download_rate": 2}
