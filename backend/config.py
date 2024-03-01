from typing import Any

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "PlayerProps": {"status": True},
    "PlayerInfo": {"status": False},
    "Gamelogs": {"status": False, "options": {"identifier_source": "matchups_only"}},
    "CareerStats": {"status": True, "options": {"identifier_source": "matchups_only"}},
    "Lineups": {"status": False},
    "DefenseRankings": {"status": True},
}
