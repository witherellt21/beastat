import logging

from scrapp.scraper.identification_functions import indexed
from scrapp.scraper.web_page import NestedWebPage

from ..util import get_player_ids_from_players_info
from .player_game_log_table import table as game_log_table

player_game_logs_page = NestedWebPage(
    "{player_id}/gamelog/",
    get_player_ids_from_players_info,
    name="NFLPlayerGameLogs",
    log_level=logging.DEBUG,
)

player_game_logs_page.add_table(
    game_log_table,
    identification_function=indexed(0),
    stale_condition={
        "from_args": ["player_id"],
        "query": {"equal_to": {"player_id": "player_id"}},
    },
)
