import logging

import pandas as pd
from scrapp.scraper.web_page2 import BaseWebPage, NestedWebPage

from .kick_and_punt_return_splits import kick_and_punt_return_splits_table
from .rushing_and_receiving_splits import rushing_and_receiving_splits_table
from .util import has_regular_season_receiving_column, has_regular_season_return_data

pd.set_option("future.no_silent_downcasting", True)


def load_query_set(web_page: BaseWebPage):
    query_set = [
        {"player_id": player_id}
        for player_id in web_page.table_configs["NFLPlayersInfo"]
        .table.data.commits["id"]
        .values
    ]

    return query_set


player_summary_page = NestedWebPage(
    query="{player_id}.htm",
    query_set_provider=load_query_set,
    name="NFLPlayerSummary",
    log_level=logging.DEBUG,
)
# player_summary_page = BaseWebPage(
#     name="NFLPlayersList",
#     base_download_url="https://www.pro-football-reference.com/players/{player_last_initial}/{player_id}.htm",
#     # default_query_set=[{"player_last_initial": "B", "player_id": "BeckOd00"}],
#     log_level=logging.DEBUG,
# )

player_summary_page.add_table(
    rushing_and_receiving_splits_table,
    identification_function=has_regular_season_receiving_column,
    stale_condition={
        "from_args": ["player_id"],
        "query": {"startswith": {"player_id": "player_id"}},
    },
)

player_summary_page.add_table(
    kick_and_punt_return_splits_table,
    identification_function=has_regular_season_return_data,
    stale_condition={
        "from_args": ["player_id"],
        "query": {"startswith": {"player_id": "player_id"}},
    },
)
