import os
from pathlib import Path

from base.scraper.get_scrapers import load_scrapers
from sql_app.register import *


def run_scrapers():
    scrapers = load_scrapers(str(Path(__file__).parent) + os.sep + "scrapers")

    for scraper in scrapers:
        scraper.daemon = True
        scraper.configure(nested_download=True)
        scraper.start()


if __name__ == "__main__":
    import sys

    print(sys.argv)

    if sys.argv[1] == "scrape":
        run_scrapers()
