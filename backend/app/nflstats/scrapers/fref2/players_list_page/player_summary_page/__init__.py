import logging

import pandas as pd
from scrapp.scraper.web_page import BaseWebPage, NestedWebPage

from . import (
    defensive_splits_table,
    kick_and_punt_return_splits_table,
    passing_splits_table,
    rushing_and_receiving_splits_table,
)
from .util import (
    has_regular_season_defensive_data,
    has_regular_season_passing_data,
    has_regular_season_return_data,
    has_regular_season_rushing_and_receiving_columns,
)

pd.set_option("future.no_silent_downcasting", True)


def get_player_ids_from_parent(web_page: BaseWebPage):
    query_set = [
        {"player_id": player_id}
        for player_id in web_page.table_configs["NFLPlayersInfo"]
        .table.data.commits["id"]
        .values
    ]

    return query_set


player_summary_page = NestedWebPage(
    query="{player_id}.htm",
    query_set_provider=get_player_ids_from_parent,
    name="NFLPlayerSummary",
    log_level=logging.DEBUG,
)
# player_summary_page2 = BaseWebPage(
#     name="NFLPlayersList",
#     base_download_url="https://www.pro-football-reference.com/players/{player_last_initial}/{player_id}.htm",
#     default_query_set=[{"player_last_initial": "A", "player_id": "AbraJo01"}],
#     log_level=logging.DEBUG,
# )

player_summary_page.add_table(
    rushing_and_receiving_splits_table.table,
    identification_function=has_regular_season_rushing_and_receiving_columns,
    stale_condition={
        "from_args": ["player_id"],
        "query": {"startswith": {"player_id": "player_id"}},
    },
)

player_summary_page.add_table(
    kick_and_punt_return_splits_table.table,
    identification_function=has_regular_season_return_data,
    stale_condition={
        "from_args": ["player_id"],
        "query": {"startswith": {"player_id": "player_id"}},
    },
)

player_summary_page.add_table(
    defensive_splits_table.table,
    identification_function=has_regular_season_defensive_data,
    stale_condition={
        "from_args": ["player_id"],
        "query": {"startswith": {"player_id": "player_id"}},
    },
)

player_summary_page.add_table(
    passing_splits_table.table,
    identification_function=has_regular_season_passing_data,
    stale_condition={
        "from_args": ["player_id"],
        "query": {"startswith": {"player_id": "player_id"}},
    },
)
