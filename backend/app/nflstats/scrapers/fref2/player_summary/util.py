import re
from typing import Any, Optional

import numpy as np
from scrapp.tables import schema


def extract_season_as_int_or_none(season: Any) -> Optional[int]:
    if type(season) == float:
        if np.isnan(season):
            return None

        return int(season)

    elif type(season) == str:
        year_match = re.search(r"\d{4}", season)

        return int(year_match.group(0)) if year_match else None

    else:
        return None


def get_team_id_by_abbr_or_none(abbr: str):
    record = schema.table("nflteams").get_record({"abbr": abbr})

    return record.id if record else None  # type: ignore
