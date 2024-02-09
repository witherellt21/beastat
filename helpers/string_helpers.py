import os
import re

from global_implementations import constants
from fuzzywuzzy import process
from unidecode import unidecode


RENAME = {
    "Nenê": "Nenê Hilario",
    "Maxi Kleber": "Maxi Klebir"
}

def get_player_id_from_name(*, player_name: str) -> str:
    player_name = RENAME.get(player_name, player_name)

    try:
        name_components = player_name.split(" ")[:2]
        
        # remove all apostraphe's and normalize the odd characters
        normalized_components = map(lambda name: re.sub("[^a-zA-Z0-9 -]", "", unidecode(name)), name_components)
        first_name, last_name = map(lambda x: x.lower(), normalized_components)
        player_id = f"{last_name[:5]}{first_name[:2]}"
        return player_id
    except Exception as e:
        raise Exception(f"Error getting player id for {player_name}. {e}")

def convert_season_to_year(*, season:str) -> int:
    try:
        # Split the year to fetch the millenium and year
        start_year, end_year = season.split('-')
        year_prefix = start_year[:2]
        year_suffix = end_year

        # Correct for seasons that span accross milleniums
        if end_year == "00":
            year_prefix = str(int(year_prefix) + 1)
        
        # Concatenate the millenium and year and convert to int
        return int(year_prefix + year_suffix)
    except Exception as e:
        raise Exception(f"Error converting {season} to a year: {e}")

def construct_file_path(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


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

if __name__ == "__main__":
    # player_id = format_player_id("Terrance Mann")
    # print(player_id)
    # print(convert_season_to_year(season="2020-21"))
    
    # save_path = f"saved_tables/player_data/gamelogs/p"
    # construct_file_path(save_path)
    name = "Luka Dončić"
    player_id = get_player_id_from_name(player_name=name)
    print(player_id)
