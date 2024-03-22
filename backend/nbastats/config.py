from base.scraper import BaseScraper
from nbastats.scraper import SCRAPERS

from .settings import DATA_SCRAPE

scrapers: list[BaseScraper] = []

for scraper_name, scraper in SCRAPERS.items():
    if scraper_name in DATA_SCRAPE:
        if (
            "status" in DATA_SCRAPE[scraper_name]
            and not DATA_SCRAPE[scraper_name]["status"]
        ):
            continue

        if "log_level" in DATA_SCRAPE[scraper_name]:
            scraper.set_log_level(DATA_SCRAPE[scraper_name]["log_level"])

    scrapers.append(scraper)
