import time

from data_scrape.abstract_base_scraper import AbstractBaseScraper


def test_scraper_thread(*, scraper_class: AbstractBaseScraper):
    scraper: AbstractBaseScraper = scraper_class()
    scraper.start()

    start = time.time()
    while time.time() - start < 10:
        time.sleep(1)

    scraper.RUNNING = False
