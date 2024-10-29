from typing import Optional

from scrapp.tables import schema


def extract_team_id_from_team_link(link: Optional[str]) -> Optional[str]:
    return link.rsplit("/", 2)[1].split(".")[0] if link else None


def extract_team_abbr_from_team_name(name: str) -> str:
    city, mascot = name.rsplit(" ", 1)

    city_parts = city.split(" ")
    if len(city_parts) == 1:
        abbr = city_parts[0][:3].upper()
    else:
        abbr = "".join([city_part[0].upper() for city_part in city_parts])

    if abbr in ("NY", "LA"):
        abbr += mascot[0].upper()

    return abbr


def database_has_32_teams() -> bool:
    """
    Stale condition that enforces the database to have 32 records for teams.

    At the time of creation, there are 32 teams in the NFL.
    """
    return schema.table("nflteams").count_records() == 32
