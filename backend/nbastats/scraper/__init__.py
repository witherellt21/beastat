from typing import Type

from base.scraper import BaseScraper

from . import player_props
from .players.scraper import player_scraper
from .todays_games.scraper import todays_games_scraper

# from .defensive_rankings.
SCRAPERS: dict[str, BaseScraper] = {}

for scraper in [player_props.SCRAPER, player_scraper, todays_games_scraper]:
    SCRAPERS[scraper.name] = scraper
