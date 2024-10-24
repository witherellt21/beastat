from scrapp import setup
from scrapp.scraper.identification_functions import first
from scrapp.tables.base_table import AdvancedQuery

setup()

import logging

from scrapp.scraper import BaseWebPage

from .teams import teams_table

teams_list_page = BaseWebPage(
    name="NFLTeamsList",
    base_download_url="https://www.pro-football-reference.com/teams/",
    log_level=logging.DEBUG,
    download_rate=5,
)

teams_list_page.add_table(
    teams_table, identification_function=first, stale_condition=None
)
