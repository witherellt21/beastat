import time
from typing import Type

from old_scraper.abstract_base_scraper import AbstractBaseScraper


def test_scraper_thread(*, scraper_class: Type[AbstractBaseScraper]):
    scraper: AbstractBaseScraper = scraper_class()
    scraper.start()

    start = time.time()
    while time.time() - start < 10:
        time.sleep(1)

    scraper.RUNNING = False
