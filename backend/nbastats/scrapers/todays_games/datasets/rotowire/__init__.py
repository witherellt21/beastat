from nbastats.scrapers.todays_games.datasets.rotowire.util import (
    extract_games_lineups_matchups,
)

NAME = "TodaysGames"

BASE_DOWNLOAD_URL = "http://www.rotowire.com/basketball/nba-lineups.php"

CONFIG = {"extract_tables": extract_games_lineups_matchups}
