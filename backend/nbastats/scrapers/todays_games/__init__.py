import logging

from core.scraper.base import ScraperKwargs

NAME = "TodaysGames"

CONFIG: ScraperKwargs = {
    "active": False,
    "log_level": logging.INFO,
    "download_rate": 5,
    "align": "inline",
}

DEPENDENCIES = {}

INHERITANCES = {}
