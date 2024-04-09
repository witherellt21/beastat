import logging

from core.scraper import WebScraperKwargs

NAME = "DraftKings"
CONFIG: WebScraperKwargs = {
    "active": False,
    "log_level": logging.DEBUG,
    "download_rate": 2,
    "align": "inline",
}
