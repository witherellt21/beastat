import logging

from core.scraper import WebScraperKwargs

NAME = "TodaysGames"

CONFIG: WebScraperKwargs = {
    "active": True,
    "log_level": logging.INFO,
    "download_rate": 5,
    "align": "inline",
}

DEPENDENCIES = {}

INHERITANCES = {}
