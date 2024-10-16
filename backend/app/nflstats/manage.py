import os
import time
from pathlib import Path
from time import sleep

from scrapers import *
from scrapp.scraper.management.manager import (
    ScraperManager,
    add_scraper,
    add_table,
    add_web_page,
    load_scrapers,
)

SCRAPERS_DIR = str(Path(__file__).parent) + os.sep + "scrapers"


def run_scrapers():
    scraper_manager = ScraperManager.get_instance("nflstats")
    scraper = scraper_manager.get_scraper("FootballReference")
    scraper.execute()

    # scraper_manager.run()

    # running = True
    # while running:
    #     sleep(1)

    # scraper_manager.kill()


def create_scraper(name: str):
    add_scraper(name=name, path=SCRAPERS_DIR)


def create_dataset(scraper_name: str, name: str):
    add_web_page(scraper_name=scraper_name, name=name, path=SCRAPERS_DIR)


def create_table(scraper_name: str, dataset_name: str, name: str):
    add_table(
        scraper_name=scraper_name,
        web_page_name=dataset_name,
        name=name,
        path=SCRAPERS_DIR,
    )


if __name__ == "__main__":
    import sys

    if sys.argv[1] == "scrape":
        scrapers = run_scrapers()

    if sys.argv[1] == "makescraper":
        scrapers = create_scraper(sys.argv[2])

    if sys.argv[1] == "makedataset":
        scrapers = create_dataset(sys.argv[2], sys.argv[3])

    if sys.argv[1] == "maketable":
        scrapers = create_table(sys.argv[2], sys.argv[3], sys.argv[4])
