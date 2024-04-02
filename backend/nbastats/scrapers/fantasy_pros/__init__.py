import logging

from base.scraper.base import ScraperKwargs

NAME = "FantasyPros"

CONFIG: ScraperKwargs = {
    "active": False,
    "log_level": logging.INFO,
    "download_rate": 1,
    "align": "inline",
}

DEPENDENCIES = {}

INHERITANCES = {}
