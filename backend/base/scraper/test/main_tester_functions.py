import time

from base.scraper import BaseScraper


def test_scraper_thread(*, scraper: BaseScraper, timeout: int = 10):
    scraper.start()

    start = time.time()
    while time.time() - start < timeout:
        time.sleep(1)

    scraper.RUNNING = False
