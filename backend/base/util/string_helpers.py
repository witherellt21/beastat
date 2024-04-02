import logging
import os
import re
from typing import Optional, Sequence

from fuzzywuzzy import fuzz, process
from nbastats.global_implementations import constants
from unidecode import unidecode

logger = logging.getLogger("main")


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

        try:
            match_last_name = match_name.split(" ", 1)[1].lower()
            search_last_name = value.split(" ", 1)[1].lower()
        except IndexError as e:
            logger.error(f"{e}. {match_name} and {value}")
            return False

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

    matched = find_closest_match(
        value="Donte Divincenzo", search_list=["Donte DiVincenzo"]
    )
    print(matched)
