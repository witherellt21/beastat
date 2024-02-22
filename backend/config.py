from typing import Any

DATA_SCRAPE: dict[str, dict[str, Any]] = {
    "PlayerProps": {"status": True},
    "PlayerInfo": {"status": False},
    "Gamelogs": {"status": True, "options": {"identifier_source": "matchups_only"}},
    "CareerStats": {"status": False, "options": {"identifier_source": "matchups_only"}},
    "Lineups": {"status": True},
}
