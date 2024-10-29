import logging

from scrapp.scraper import BaseWebPage
from scrapp.scraper.identification_functions import indexed

from . import teams_table
from .util import database_has_32_teams

teams_list_page = BaseWebPage(
    name="NFLTeamsList",
    base_download_url="https://www.pro-football-reference.com/teams/",
    log_level=logging.DEBUG,
    download_rate=5,
)

teams_list_page.add_table(
    teams_table.table,
    identification_function=indexed(0),
    stale_condition=None,
)
