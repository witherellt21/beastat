import logging

from base.scraper.base import ScraperKwargs

NAME = "PlayerPropsScraper"
CONFIG: ScraperKwargs = {
    "active": False,
    "log_level": logging.INFO,
    "download_rate": 2,
    "align": "inline",
}
