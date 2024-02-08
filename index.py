import numpy as np
import pandas as pd

import datetime
import traceback
import sys

from data_scrape.lineups import get_lineups
from fuzzywuzzy import process
from global_implementations import constants
# from player_stats.player_info import PlayerInfo
from data_scrape.player_info import PlayerInfoScraper
from player_stats.career_stats import CareerStats
from player_stats.gamelog import Gamelog
from string import ascii_lowercase

# import logging

# logger = logging.getLogger("main")

def run_hypothesis(*, player_dataset: pd.DataFrame, hypothesis: str) -> tuple[int]:
    # p1_subset_matchup = p1_set_matchup[p1_filter]
    hypothesis_set: pd.DataFrame = player_dataset.query(hypothesis)
    return len(hypothesis_set) / len(player_dataset) * 100, len(player_dataset)

def get_matchup_data(*, player_1_dataset: pd.DataFrame, player_2_dataset: pd.DataFrame):
    # Merge the datasets on games they played against each other and drop inactive games
    matchup_gamelog = pd.merge(player_1_dataset, player_2_dataset, left_on=['Date','Tm'], right_on=['Date', 'Opp']).dropna()
    
    # Get the original column names of the datasets that were not duplicated
    column_headers = player_1_dataset.loc[:, player_1_dataset.columns != "Date"].columns

    # Create filters to separate the respective datasets for each player
    p1_subset_filter: list = ["Date"] + list(map(lambda stat: f"{stat}_x", column_headers))
    p2_subset_filter: list = ["Date"] + list(map(lambda stat: f"{stat}_y", column_headers))

    rename_function = lambda column: column.rsplit('_', 1)[0]

    # Rename the columns for each player to remove the suffixes
    p1_matchup_data: pd.DataFrame = matchup_gamelog[p1_subset_filter].rename(rename_function, axis="columns")
    p2_matchup_data: pd.DataFrame = matchup_gamelog[p2_subset_filter].rename(rename_function, axis="columns")

    # Combine the datasets to that the merged values are now concatenated
    matchup_data = pd.concat([p1_matchup_data, p2_matchup_data], ignore_index=True)

    return matchup_data

def get_player_full_gamelog(*, player_id: str, years_active: list[int]) -> pd.DataFrame:
    # Get the players full gamelog
    full_gamelog_data = pd.DataFrame()
    for year in years_active:
        current_gamelog: Gamelog = Gamelog(player_id=player_id, year=year)
        current_gamelog_data: pd.DataFrame = current_gamelog.get_data()
        full_gamelog_data = pd.concat([full_gamelog_data, current_gamelog_data], ignore_index=True)

    return full_gamelog_data


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


# ------------------- Program ------------------------


lineups: pd.DataFrame = get_lineups()

lineups_matchups: pd.DataFrame = lineups.merge(lineups, left_on=["game_id", "team"], right_on=["game_id", "opp"]).drop(labels=[
    "team_x", "opp_x", "home_x", "confirmed_x", "Bench_x", "team_y", "opp_y", "home_y", "confirmed_y", "Bench_y"
], axis="columns").drop_duplicates(subset="game_id")

matchups: list = []
for index, row in lineups_matchups.iterrows():
    matchups.extend(list(map(lambda position: (row[f"{position}_x"], row[f"{position}_y"]), constants.BASKETBALL_POSITIONS)))

# matchups: list = [
#     ("Jakob Poetl", "Nick Richards"),
#     ("Brandon Miller", "Gary Trent Jr."),
#     ("Evan Mobley", "Kyle Kuzma"),
#     ("Donovan Mitchell", "Jordan Poole")
# ]

# Get all of the active players by last initial
for letter in ascii_lowercase:
    # TODO: idea - create an EXPECTED_COLUMNS variable for ABD and initialize the data using this. This would save an empty dataframe
    if letter == "x":
        continue

    player_info = PlayerInfoScraper(last_initial=letter)
    player_ids = pd.concat([player_ids, player_info.get_data()], ignore_index=True)

player_names: list[str] = player_ids['Player'].to_list()

# Get the gamelog of a specific player, starting with Giannis as an example
gamelog_datasets: dict[str: pd.DataFrame] = {}
career_averages: dict[str: pd.DataFrame] = {}

for matchup in matchups:
    print(matchup)
    for player_name in matchup:
        player: pd.DataFrame = player_ids[player_ids["Player"] == player_name]

        if player.empty:
            player_name_match: str = find_closest_match(value=player_name, search_list=player_names)
            player: pd.DataFrame = player_ids[player_ids["Player"] == player_name_match]

        player_id: str = player.iloc[0]["player_id"]

        # Get the CareerStats for the given player
        career_stats: CareerStats = CareerStats(player_id=player_id)
        career_data: pd.DataFrame = career_stats.get_data()
        career_averages[player_name] = career_data

        # Get the players active seasons from the CareerStats
        seasons_active: list[int] = career_stats.get_active_seasons()

        # Get the player Gamelog
        player_gamelog: pd.DataFrame = get_player_full_gamelog(player_id=player_id, years_active=seasons_active)
        player_gamelog["player_name"] = player_name

        gamelog_datasets[player_name] = player_gamelog
    
    player_1, player_2 = matchup

    player_1_data: pd.DataFrame = gamelog_datasets[player_1]
    player_2_data: pd.DataFrame = gamelog_datasets[player_2]

    # Create a filter to just get the stats which will be averaged
    matchup_data: pd.DataFrame = get_matchup_data(player_1_dataset=player_1_data, player_2_dataset=player_2_data)

    # Check that the filtering process worked and that the number of games for each player match
    num_matchups_per_player: list[int] = matchup_data["player_name"].value_counts().tolist()
    if not num_matchups_per_player:
        continue

    assert num_matchups_per_player[0] == num_matchups_per_player[1], Exception("Number of games for each player in the matchup do not match.")
    
    num_matchups: int = num_matchups_per_player[0]

    numerical_columns: list[str] = matchup_data.select_dtypes(include=[np.number]).columns
    
    matchup_averages: pd.DataFrame = matchup_data.groupby("player_name")[numerical_columns].mean().round()
    matchup_averages["num_matchups"] = num_matchups

    current_matchup_data: pd.DataFrame = matchup_data[matchup_data["Date"].dt.year >= 2024]
    current_matchup_averages: pd.DataFrame = current_matchup_data.groupby("player_name")[numerical_columns].mean().round()
    current_matchup_averages["num_matchups"] = len(current_matchup_data) / 2

    p2_points_over_num = len(matchup_data.query(f"player_name == '{player_2}' and PTS >= 25"))
    
    # p1_11_pts = player_1_data[player_1_data["PTS"] >= 11]
    # p1_11_pts_3_threes = p1_11_pts[p1_11_pts["3P"] >= 4]
    # p1_filters =

    subfilter_name: str = "16_PTS"
    # p1_subfilter: str = "PTS >= 15" # 55%
    # p1_hypothesis: str = "`3P` >= 3"
    p1_hypothesis: str = "PTS >= 27" # 55%
    player_1_data: pd.DataFrame = player_1_data.dropna()
    # player_1_data = player_1_data[player_1_data["MP"] >= datetime.datetime(minute=30, second=0)]
    # p1_subfilter_set: pd.DataFrame = player_1_data.query(p1_subfilter)
    p1_subfilter_set: pd.DataFrame = player_1_data[player_1_data["PTS"] >= 15]
    subfilter_res, subfilter_count = run_hypothesis(player_dataset=p1_subfilter_set, hypothesis=p1_hypothesis)

    p1_matchup_set: pd.DataFrame = matchup_data[matchup_data["player_name"] == player_1]
    matchup_res, matchup_count = run_hypothesis(player_dataset=p1_matchup_set, hypothesis=p1_hypothesis)

    player_res, player_count = run_hypothesis(player_dataset=player_1_data, hypothesis=p1_hypothesis)

    player_current_set: pd.DataFrame = player_1_data[player_1_data["Date"] >= datetime.datetime(2023, 6, 1)]
    player_current_res, player_current_count = run_hypothesis(player_dataset=player_current_set, hypothesis=p1_hypothesis)

    player_last_10_set: pd.DataFrame = player_1_data.tail(10)
    player_last_10_res, player_last_10_count = run_hypothesis(player_dataset=player_last_10_set, hypothesis=p1_hypothesis)

    results = pd.DataFrame({
        "player_name": [player_1],
        "overall": [player_res],
        "overall_count": [player_count],
        "matchup": [matchup_res],
        "matchup_count": [matchup_count],
        f"{constants.CURRENT_SEASON}": [player_current_res],
        f"{constants.CURRENT_SEASON}_count": [player_current_count],
        "last_10": [player_last_10_res],
        "last_10_count": [player_last_10_count],
        # str(p1_subfilter): [subfilter_res],
        # f"{p1_subfilter}_count": [subfilter_count]
    })

    print(results)
    # print(matchup_averages)
    # print(current_matchup_averages)
    # print(career_averages[player_1])

# for matchup in matchups:
#     for player_name in matchup:
#         player_id: str = get_player_id_from_name(player_name=player_name)
#         if player_name in ["Jaylen Brown", "Tobias Harris"]:
#             player_number = 2
#         else:
#             player_number = 1

#         career_stats: pd.DataFrame = get_player_active_seasons(player_id=player_id, player_number=player_number)
#         career_averages[player_name] = career_stats

#         # Filter the career stats to contain just the season averages
#         season_stats: pd.DataFrame = career_stats[career_stats["Season"].str.contains('^\d{4}') == True]
#         season_stats: pd.DataFrame = season_stats.dropna()

#         # Get the seasons active by converting seasons column to a value list
#         seasons_active: list[str] = season_stats["Season"].to_list()
#         seasons_active: list[int] = list(map(lambda season: convert_season_to_year(season=season), seasons_active))

#         player_gamelog: pd.DataFrame = get_player_full_gamelog(player_id=player_id, years_active=seasons_active, player_number=player_number)
#         # player_gamelog = player_gamelog.drop(labels="Rk", axis="columns") # add this to function above
#         player_gamelog["player_name"] = player_name

#         gamelog_datasets[player_name] = player_gamelog
    
#     player_1, player_2 = matchup

#     player_1_data: pd.DataFrame = gamelog_datasets[player_1]
#     player_2_data: pd.DataFrame = gamelog_datasets[player_2]

#     # Create a filter to just get the stats which will be averaged
#     matchup_data: pd.DataFrame = get_matchup_data(player_1_dataset=player_1_data, player_2_dataset=player_2_data)

#     # Check that the filtering process worked and that the number of games for each player match
#     num_matchups = matchup_data["player_name"].value_counts().tolist()
#     if not num_matchups:
#         continue

#     assert num_matchups[0] == num_matchups[1], Exception("Number of games for each player in the matchup do not match.")
    
#     num_matchups = num_matchups[0]
#     # assert num_matchups.iloc[0, 0] == num_matchups.iloc[1, 0], Exception("Number of games for each player in the matchup do not match.")

#     numerical_columns: list[str] = matchup_data.select_dtypes(include=[np.number]).columns
#     matchup_averages: pd.DataFrame = matchup_data.groupby("player_name")[numerical_columns].mean().round()

#     current_matchup_data: pd.DataFrame = matchup_data[matchup_data["Date"].dt.year >= 2024]

#     current_matchup_averages: pd.DataFrame = matchup_data.groupby("player_name")[numerical_columns].mean().round()
    
#     num_over_14_jrue = len(matchup_data.query(f"player_name == '{player_2}' and PTS >= 25"))

"""
PG
SF/PF
C
SF/PF
SG

PG
SG
"""