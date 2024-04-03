import os
from pathlib import Path
from time import sleep

from core.scraper.management.manager import (
    add_dataset,
    add_scraper,
    add_table,
    load_scrapers,
)
from sql_app.register import *

SCRAPERS_DIR = str(Path(__file__).parent) + os.sep + "scrapers"


def run_scrapers():
    scrapers = load_scrapers(SCRAPERS_DIR)
    # print(scrapers)

    for scraper in scrapers:
        # for dataset in scraper._dataset_configs.values():
        #     # print([str(dependency) for dependency in dataset.dependencies])
        #     for table in dataset._table_configs.values():
        # print([str(inheritance) for inheritance in table.inheritances])

        if scraper.RUNNING:
            scraper.daemon = True
            scraper.configure()
            scraper.start()

    return scrapers


def create_scraper(name: str):
    add_scraper(name=name, path=SCRAPERS_DIR)


def create_dataset(scraper_name: str, name: str):
    add_dataset(scraper_name=scraper_name, name=name, path=SCRAPERS_DIR)


def create_table(scraper_name: str, dataset_name: str, name: str):
    add_table(
        scraper_name=scraper_name,
        dataset_name=dataset_name,
        name=name,
        path=SCRAPERS_DIR,
    )


if __name__ == "__main__":
    import sys

    if sys.argv[1] == "scrape":
        scrapers = run_scrapers()

        running = True

        while running:
            sleep(1)

        for scraper in scrapers:
            scraper.kill_process()

    if sys.argv[1] == "makescraper":
        scrapers = create_scraper(sys.argv[2])

    if sys.argv[1] == "makedataset":
        scrapers = create_dataset(sys.argv[2], sys.argv[3])

    if sys.argv[1] == "maketable":
        scrapers = create_table(sys.argv[2], sys.argv[3], sys.argv[4])
