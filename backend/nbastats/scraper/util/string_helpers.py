import re
from typing import Optional

from unidecode import unidecode

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
