import json
import uuid

from nbastats.sql_app.database import DB

from .career_stats import CareerStatsTable
from .defense_ranking import DefenseRankingTable
from .game import GameLineTable, GameTable
from .gamelog import GamelogTable
from .lineup import LineupTable
from .matchup import MatchupTable
from .player import PlayerPropTable, PlayerTable
from .team import TeamTable

Teams = TeamTable(DB)
BasicInfo = PlayerTable(DB)
SeasonAveragess = CareerStatsTable(DB)
Games = GameTable(DB)
GameLines = GameLineTable(DB)
PlayerBoxScores = GamelogTable(DB)
Lineups = LineupTable(DB)
Matchups = MatchupTable(DB)
PlayerProps = PlayerPropTable(DB)
DefenseRankings = DefenseRankingTable(DB)


try:
    with open("nbastats/sql_app/static_data/teams.json", "r") as teams_file:
        new_data = {}
        team_data = json.load(teams_file)
        for name, abbreviations in team_data.items():
            Teams.update_or_insert_record(
                data={
                    "id": uuid.uuid4(),
                    "abbr": abbreviations[0],
                    "name": name,
                    "alt_abbrs": abbreviations[1:],
                }
            )
except FileNotFoundError as e:
    print(f"Unable to download team data. {e}")
