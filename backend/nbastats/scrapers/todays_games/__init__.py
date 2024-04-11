import logging

from core.scraper import WebScraperKwargs

NAME = "TodaysGames"

CONFIG: WebScraperKwargs = {
    "active": False,
    "log_level": logging.WARNING,
    "download_rate": 5,
    "align": "inline",
}

DEPENDENCIES = {}

INHERITANCES = {}
