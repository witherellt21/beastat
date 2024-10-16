import logging

from scrapp.scraper.web_scraper import WebScraperKwargs

NAME = ""

CONFIG: WebScraperKwargs = {
    "active": True,
    "log_level": logging.INFO,
    "download_rate": 5,
    "align": "inline",
}

DEPENDENCIES = {}

INHERITANCES = {}
