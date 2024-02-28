from typing import Any

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "PlayerProps": {"status": True},
    "PlayerInfo": {"status": False},
    "Gamelogs": {"status": False, "options": {"identifier_source": "all"}},
    "CareerStats": {"status": False, "options": {"identifier_source": "all"}},
    "Lineups": {"status": True},
    "DefenseRankings": {"status": False},
}
