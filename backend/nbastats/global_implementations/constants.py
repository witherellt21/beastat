REQUEST_HEADER: dict[str, str] = {"User-agent": "Web Scraper 1.0"}
DESIRED_STATS: list[str] = [
    "Date",
    "Tm",
    "Opp",
    "MP",
    "PTS",
    "AST",
    "TRB",
    "FT",
    "3PA",
    "3P",
    "FGA",
    "FG",
    "PA",
    "RA",
    "PRA",
]
AUGMENTED_STATS: dict[str, str] = {
    "PA": "PTS+AST",
    "PR": "PTS+TRB",
    "RA": "TRB+AST",
    "PRA": "PTS+TRB+AST",
}
NAN_VALUES: list[str] = [
    "",
    "Player Suspended",
    "Not With Team",
    "Did Not Dress",
    "Did Not Play",
    "Inactive",
]
CURRENT_SEASON: int = 2024
BASKETBALL_POSITIONS: list[str] = ["PG", "SG", "SF", "PF", "C"]
DEFAULT_MATCH_THRESHOLD: int = 80
