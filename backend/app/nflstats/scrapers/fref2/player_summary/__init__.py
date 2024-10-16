from scrapp.scraper import BaseWebPage

from ..player_list import player_info_table, player_list_page
from .kick_and_punt_return_splits import kick_and_punt_return_splits_table
from .rushing_and_receiving_splits import rushing_and_receiving_table

player_summary_page = BaseWebPage(
    name="NFLPlayerSummary",
    base_download_url="http://www.pro-football-reference.com/players/{player_last_initial}/{player_id}.htm",
    html_tables={
        kick_and_punt_return_splits_table.name: kick_and_punt_return_splits_table,
        rushing_and_receiving_table.name: rushing_and_receiving_table,
    },
    # default_query_set=[{"player_last_initial": "A", "player_id": "AberWa00"}],
)

player_summary_page.add_dependency(
    source=player_list_page,
    meta_data={
        "table_name": player_info_table.name,
        "query_set_provider": lambda dataset: [
            {"player_last_initial": player_id[0].upper(), "player_id": player_id}
            for player_id in dataset.index.values
        ],
    },
)
