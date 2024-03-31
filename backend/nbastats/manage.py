import os
from pathlib import Path
from time import sleep

from base.scraper.get_scrapers import load_scrapers
from sql_app.register import *


def run_scrapers():
    scrapers = load_scrapers(str(Path(__file__).parent) + os.sep + "scrapers")

    for scraper in scrapers:
        for dataset in scraper._dataset_configs.values():
            print([str(dependency) for dependency in dataset.dependencies])
            for table in dataset._table_configs.values():
                print([str(inheritance) for inheritance in table.inheritances])

        if scraper.RUNNING:
            scraper.daemon = True
            scraper.configure()
            scraper.start()

    return scrapers


if __name__ == "__main__":
    import sys

    if sys.argv[1] == "scrape":
        scrapers = run_scrapers()

        running = True

        while running:
            sleep(1)

        for scraper in scrapers:
            scraper.kill_process()
