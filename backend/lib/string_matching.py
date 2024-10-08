import logging
import re
from typing import Optional, Sequence

from fuzzywuzzy import fuzz, process

logger = logging.getLogger("main")


def find_closest_match(
    *,
    target: str,
    search_list: list[str],
    match_threshold: int = 80,
) -> Optional[str]:
    """
    From the given search list, find the string that most closes matches the target string.

    Return None if no matches clear the match threshold.
    """

    def match_is_valid(match) -> bool:
        match_name = match[0]
        match_validity = match[1]

        if type(match_name) != str or type(match_validity) != int:
            return False

        try:
            match_last_name = match_name.split(" ", 1)[1].lower()
            search_last_name = target.split(" ", 1)[1].lower()
        except IndexError as e:
            logger.error(f"{e}. {match_name} and {target}")
            return False

        match_last_name = re.sub(
            r"[\.\s]*(jr|sr|I|II|III|IV|V)[\.]*", "", search_last_name
        )
        search_last_name = re.sub(
            r"[\.\s]*(jr|sr|I|II|III|IV|V)[\.]*", "", search_last_name
        )

        if len(match_last_name) >= 2 and len(search_last_name) >= 2:
            return (
                fuzz.ratio(match_last_name, search_last_name) > match_threshold
                and match[1] >= match_threshold
            )

        return False

    matches: Sequence[tuple[str, int] | tuple[str, int, str]] = process.extract(
        target, search_list, limit=5
    )
    valid_matches: Sequence[tuple[str, int] | tuple[str, int, str]] = list(
        filter(match_is_valid, matches)
    )

    if not valid_matches:
        return None
    else:
        return valid_matches[0][0]
