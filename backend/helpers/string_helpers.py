import os
import re

from global_implementations import constants
from fuzzywuzzy import process, fuzz
from unidecode import unidecode
from typing import Optional, Sequence


RENAME = {
    "Nene": "Nene Hilario",
    "Nene": "Nene Hilario",
    "Maxi Kleber": "Maxi Klebir",
    "Clint Capela": "Caint Capela",
}


def get_player_id_from_name(*, player_name: str) -> str:
    player_name = unidecode(player_name)
    player_name = RENAME.get(player_name, player_name)

    try:

        name_components = player_name.split(" ")[:2]

        # remove all apostraphe's and normalize the odd characters
        normalized_components = map(
            lambda name: re.sub("[^a-zA-Z0-9 -]", "", name), name_components
        )

        first_name, last_name = map(lambda x: x.lower(), normalized_components)
        player_id = f"{last_name[:5]}{first_name[:2]}"
        return player_id
    except Exception as e:
        raise Exception(f"Error getting player id for {player_name}. {e}")


def convert_season_to_year(*, season: str) -> Optional[int]:
    try:
        # Split the year to fetch the millenium and year
        year_range = season.split("-")

        if len(year_range) != 2:
            try:
                return int(float(season))
            except ValueError:
                return None
        else:
            start_year = year_range[0]
            end_year = year_range[1]

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
    match_threshold: int = constants.DEFAULT_MATCH_THRESHOLD,
) -> Optional[str]:
    def match_is_valid(match) -> bool:
        match_name = match[0]
        match_validity = match[1]

        if type(match_name) != str or type(match_validity) != int:
            return False

        match_last_name = match_name.split(" ", 1)[1].lower()
        search_last_name = value.split(" ", 1)[1].lower()

        match_last_name = re.sub(
            r"[\.\s]*(jr|sr|I|II|III|IV|V)[\.]*", "", search_last_name
        )
        search_last_name = re.sub(
            r"[\.\s]*(jr|sr|I|II|III|IV|V)[\.]*", "", search_last_name
        )

        if len(match_last_name) >= 2 and len(search_last_name) >= 2:
            return (
                fuzz.ratio(match_last_name, search_last_name)
                > constants.DEFAULT_MATCH_THRESHOLD
                and match[1] >= match_threshold
            )

        return False

    matches: Sequence[tuple[str, int] | tuple[str, int, str]] = process.extract(
        value, search_list, limit=5
    )
    valid_matches: Sequence[tuple[str, int] | tuple[str, int, str]] = list(
        filter(match_is_valid, matches)
    )

    if not valid_matches:
        return None
    else:
        return valid_matches[0][0]


if __name__ == "__main__":
    # player_id = format_player_id("Terrance Mann")
    # print(player_id)
    # print(convert_season_to_year(season="2020-21"))

    # save_path = f"saved_tables/player_data/gamelogs/p"
    # construct_file_path(save_path)
    # name = "Luka Dončić"
    # player_id = get_player_id_from_name(player_name="Nickeil Alexander-Walker")
    # print(player_id)

    matched = find_closest_match(value="Jabari Smith", search_list=["Jabari Smith Jr."])
    print(matched)
