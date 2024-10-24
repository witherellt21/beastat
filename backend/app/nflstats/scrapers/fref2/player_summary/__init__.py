import logging
from typing import Optional

import pandas as pd
from scrapp.scraper import BaseWebPage

from .kick_and_punt_return_splits import example_df as kap_df
from .kick_and_punt_return_splits import kick_and_punt_return_splits_table
from .rushing_and_receiving_splits import example_df as rar_df
from .rushing_and_receiving_splits import rushing_and_receiving_splits_table

# from scrapp.scraper.web_page import CachedQueryConfig
# from scrapp.tables.base_table import AdvancedQuery


pd.set_option("future.no_silent_downcasting", True)


def has_regular_season_return_data(
    tables: list[pd.DataFrame],
) -> Optional[pd.DataFrame]:
    return next(
        (
            table
            for table in tables
            if "Punt Returns" in table.columns.get_level_values(0)
            and "No." in table.columns.get_level_values(1)
        ),
        None,
    )


def has_regular_season_receiving_column(
    tables: list[pd.DataFrame],
) -> Optional[pd.DataFrame]:
    return next(
        (
            table
            for table in tables
            if "Rushing" in table.columns.get_level_values(0)
            and "Receiving" in table.columns.get_level_values(0)
            and "AV" in table.columns.get_level_values(1)
        ),
        None,
    )


player_summary_page = BaseWebPage(
    name="NFLPlayerSummary",
    base_download_url="{player_id}.htm",
    log_level=logging.DEBUG,
    download_rate=5,
    default_query_set=[{"player_last_initial": "A", "player_id": "AberWa00"}],
)

player_summary_page.add_table(
    kick_and_punt_return_splits_table,
    identification_function=has_regular_season_return_data,
    stale_condition={
        "from_args": ["player_id"],
        "query": {"equal_to": {"player_id": "player_id"}},
    },
)


# player_summary_page.add_table(
#     rushing_and_receiving_splits_table,
#     identification_function=has_regular_season_receiving_column,
#     stale_condition=lambda: True,
# )

player_summary_page.configure()

# player_summary_page.add_dependency(
#     source=players_page,
#     table_name="NFLPlayersInfo",
#     query_set_provider=lambda dataset: [
#         {"player_last_initial": player_id[0], "player_id": player_id}
#         for player_id in dataset.index.values
#     ],
# )

# player_summary_page.add_dependency(
#     source=player_list_page,
#     meta_data={
#         "table_name": player_info_table.name,
#         "query_set_provider": lambda dataset: [
#             {"player_last_initial": player_id[0].upper(), "player_id": player_id}
#             for player_id in dataset.index.values
#         ],
#     },
# )
