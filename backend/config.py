from typing import Any

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "PlayerProps": {"status": False},
    "PlayerInfo": {"status": False},
    "Gamelogs": {"status": False, "options": {"identifier_source": "matchups_only"}},
    "CareerStats": {"status": True, "options": {"identifier_source": "all"}},
    "Lineups": {"status": True},
    "DefenseRankings": {"status": False},
}
