import logging

from scrapp.scraper import WebScraperKwargs

NAME = "FantasyPros"

CONFIG: WebScraperKwargs = {
    "active": False,
    "log_level": logging.INFO,
    "download_rate": 1,
    "align": "inline",
}

DEPENDENCIES = {}

INHERITANCES = {}
