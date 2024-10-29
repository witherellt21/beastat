from scrapp import setup

setup()

import logging
from string import ascii_uppercase

from scrapp.scraper.identification_functions import indexed
from scrapp.scraper.web_page import BaseWebPage

from . import player_info_table
from .player_summary_page import player_summary_page
from .util import get_player_list_page_tables

### Create Page
players_list_page = BaseWebPage(
    name="NFLPlayersList",
    base_download_url="https://www.pro-football-reference.com/players/{player_last_initial}/",
    default_query_set=[{"player_last_initial": letter} for letter in ascii_uppercase],
    extract_tables=get_player_list_page_tables,
    log_level=logging.DEBUG,
)

### Add tables to page
players_list_page.add_table(
    player_info_table.table,
    identification_function=indexed(0),
    stale_condition={
        "from_args": ["player_last_initial"],
        "query": {"startswith": {"id": "CCC"}},
    },
)

### Add nested web pages
players_list_page.add_nested_web_page(player_summary_page)


### Add dependencies to tables within the page/nested pages - TODO: Should be done elsewhere if possible
player_summary_page.table_configs[
    "NFLPlayerRushingAndReceivingSplits"
].table.add_dependency(source=player_info_table.table)


players_list_page.configure()
