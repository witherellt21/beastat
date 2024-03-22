import logging
import time

from nbastats.config import scrapers as nbastats_scrapers
from nbastats.scraper import SCRAPERS

from .settings import DATA_SCRAPE

# print(SCRAPERS)

for scraper_name, scraper in SCRAPERS.items():
    if scraper_name in DATA_SCRAPE:
        if (
            "status" in DATA_SCRAPE[scraper_name]
            and not DATA_SCRAPE[scraper_name]["status"]
        ):
            continue

        if "log_level" in DATA_SCRAPE[scraper_name]:
            scraper.set_log_level(DATA_SCRAPE[scraper_name]["log_level"])

    scraper.daemon = True
    scraper.configure(nested_download=True)
    scraper.set_log_level(log_level=logging.DEBUG)
    scraper.start()

RUNNING = True

while RUNNING:
    print(SCRAPERS)
    time.sleep(1)

for scraper in nbastats_scrapers:
    scraper.kill_process()
