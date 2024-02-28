from typing import Any

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "PlayerProps": {"status": False},
    "PlayerInfo": {"status": False},
    "Gamelogs": {"status": False, "options": {"identifier_source": "all"}},
    "CareerStats": {"status": False, "options": {"identifier_source": "matchups_only"}},
    "Lineups": {"status": True},
    "DefenseRankings": {"status": False},
}
