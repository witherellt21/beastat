import os
from pathlib import Path
from time import sleep

from core.scraper.management.manager import (
    add_scraper,
    add_table,
    add_web_page,
    load_scrapers,
)
from sql_app.register import *

SCRAPERS_DIR = str(Path(__file__).parent) + os.sep + "scrapers"


def run_scrapers():
    scrapers = load_scrapers(SCRAPERS_DIR)

    for scraper in scrapers:

        if scraper.RUNNING:
            scraper.daemon = True
            scraper.configure()

            # for web_page in scraper._web_pages.values():
            #     print(web_page.html_tables)
            scraper.start()

    return scrapers


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

        running = True

        while running:
            sleep(1)

        for scraper in scrapers:
            scraper.kill()

    if sys.argv[1] == "makescraper":
        scrapers = create_scraper(sys.argv[2])

    if sys.argv[1] == "makedataset":
        scrapers = create_dataset(sys.argv[2], sys.argv[3])

    if sys.argv[1] == "maketable":
        scrapers = create_table(sys.argv[2], sys.argv[3], sys.argv[4])
