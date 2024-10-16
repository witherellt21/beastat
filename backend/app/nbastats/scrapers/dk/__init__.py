import logging

from scrapp.scraper import WebScraperKwargs

NAME = "DraftKings"
CONFIG: WebScraperKwargs = {
    "active": False,
    "log_level": logging.WARNING,
    "download_rate": 2,
    "align": "inline",
}
