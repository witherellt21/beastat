import logging

from base.scraper import BaseScraper
from datasets import DATASETS

SCRAPER = BaseScraper(
    name="PlayerPropsScraper", log_level=logging.INFO, download_rate=2
)

for dataset_name, dataset in DATASETS.items():
    SCRAPER.add_dataset_config(dataset_config=dataset)
