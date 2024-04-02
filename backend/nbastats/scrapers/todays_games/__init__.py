import logging

from base.scraper.base import ScraperKwargs

NAME = "TodaysGames"

CONFIG: ScraperKwargs = {
    "active": True,
    "log_level": logging.INFO,
    "download_rate": 5,
    "align": "inline",
}

DEPENDENCIES = {}

INHERITANCES = {}
