import pandas as pd
from fuzzywuzzy import process

from data_scrape.lineups import get_lineups
from data_scrape.career_stats import CareerStatsScraper
from data_scrape.gamelog import GamelogScraper
from data_scrape.player_info import PlayerInfoScraper
from global_implementations import constants
from string import ascii_lowercase


def find_closest_match(
        *, 
        value: str, 
        search_list: list[str], 
        match_threshold: int = constants.DEFAULT_MATCH_THRESHOLD
    ) -> str:
    matches: list[tuple[str, int]] = process.extract(value, search_list, limit=1)
    valid_matches: list[tuple[str, int]] = list(filter(lambda match: match[1] >= match_threshold, matches))

    if not valid_matches:
        raise Exception(f"Could not find match for {value}. Closest match = {matches[0]}")
    else:
        return valid_matches[0][0]

def get_player_full_gamelog(*, player_id: str, years_active: list[int]) -> pd.DataFrame:
    # Get the players full gamelog
    full_gamelog_data = pd.DataFrame()
    for year in years_active:
        current_gamelog: GamelogScraper = GamelogScraper(player_id=player_id, year=year)
        current_gamelog_data: pd.DataFrame = current_gamelog.get_data()
        full_gamelog_data = pd.concat([full_gamelog_data, current_gamelog_data], ignore_index=True)

    return full_gamelog_data

# Get the starting linups for the current day
lineups: pd.DataFrame = get_lineups()

# Merge the lineups for each game to get the opposing teams lineup
lineups_matchups: pd.DataFrame = lineups.merge(lineups, left_on=["game_id", "team"], right_on=["game_id", "opp"]).drop(labels=[
    "team_x", "opp_x", "home_x", "confirmed_x", "Bench_x", "team_y", "opp_y", "home_y", "confirmed_y", "Bench_y"
], axis="columns").drop_duplicates(subset="game_id")

# Iterate through the game lineups to get the player matchups
matchups: list = []
for index, row in lineups_matchups.iterrows():
    matchups.extend(list(map(lambda position: (row[f"{position}_x"], row[f"{position}_y"]), constants.BASKETBALL_POSITIONS)))

player_ids = pd.DataFrame()

# Get all of the active players by last initial
for letter in ascii_lowercase:
    # TODO: idea - create an EXPECTED_COLUMNS variable for ABD and initialize the data using this. This would save an empty dataframe
    if letter == "x":
        continue

    player_info = PlayerInfoScraper(last_initial=letter)
    player_ids = pd.concat([player_ids, player_info.get_data()], ignore_index=True)

player_names: list[str] = player_ids['Player'].to_list()

for matchup in matchups:
    print(matchup)
    for player_name in matchup:
        player: pd.DataFrame = player_ids[player_ids["Player"] == player_name]

        if player.empty:
            player_name_match: str = find_closest_match(value=player_name, search_list=player_names)
            player: pd.DataFrame = player_ids[player_ids["Player"] == player_name_match]

        player_id: str = player.iloc[0]["player_id"]

        # Get the CareerStats for the given player
        career_stats: CareerStatsScraper = CareerStatsScraper(player_id=player_id)
        career_data: pd.DataFrame = career_stats.get_data()

        # Get the players active seasons from the CareerStats
        seasons_active: list[int] = career_stats.get_active_seasons()

        # Get the player Gamelog
        player_gamelog: pd.DataFrame = get_player_full_gamelog(player_id=player_id, years_active=seasons_active)
        player_gamelog["player_name"] = player_name
    