from . import tables

NAME = "PlayerPropsDataset"
DEFAULT_QUERY_SET = (
    [
        {"stat_category": "points", "stat_subcategory": "points"},
        {"stat_category": "assists", "stat_subcategory": "assists"},
        {"stat_category": "threes", "stat_subcategory": "threes"},
        {"stat_category": "rebounds", "stat_subcategory": "rebounds"},
        {"stat_category": "combos", "stat_subcategory": "pts-+-reb-+-ast"},
        {"stat_category": "combos", "stat_subcategory": "pts-+-reb"},
        {"stat_category": "combos", "stat_subcategory": "pts-+-ast"},
        {"stat_category": "combos", "stat_subcategory": "ast-+-reb"},
    ],
)
BASE_DOWNLOAD_URL = "http://sportsbook.draftkings.com/nba-player-props?category=player-{stat_category}&subcategory={stat_subcategory}"

_tables = tables.__load_all__()
