import time
from typing import Type

from new_scraper.base2 import BaseScraper


def test_scraper_thread(*, scraper: BaseScraper, timeout: int = 10):
    # scraper: BaseScraper = scraper_class()
    scraper.start()

    start = time.time()
    while time.time() - start < timeout:
        time.sleep(1)

    scraper.RUNNING = False
