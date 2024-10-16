import logging

from scrapp.scraper import BaseWebScraper

from .player_list import player_list_page
from .player_summary import player_summary_page

fref_scraper = BaseWebScraper(
    "FootballReference", log_level=logging.DEBUG, download_rate=5, align="nested"
)

fref_scraper.add_web_page(web_page=player_list_page)
fref_scraper.add_web_page(web_page=player_summary_page)
