import logging
import time

import scrapers
from settings import DATA_SCRAPE

for scraper_name, scraper in scrapers.__iter__():
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
    print(scrapers._scrapers)
    time.sleep(1)

for scraper_name, scraper in scrapers.__iter__():
    scraper.kill_process()
