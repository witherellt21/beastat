from nbastats.sql_app.database import DB

from .career_stats import CareerStatsTable
from .defense_ranking import DefenseRankingTable
from .game import GameLineTable, GameTable
from .gamelog import GamelogTable
from .lineup import LineupTable
from .matchup import MatchupTable
from .player import PlayerPropTable, PlayerTable
from .team import TeamTable

Teams = TeamTable(DB, source="nbastats/sql_app/static_data/teams.json")
BasicInfo = PlayerTable(DB)
SeasonAveragess = CareerStatsTable(DB)
Games = GameTable(DB)
GameLines = GameLineTable(DB)
PlayerBoxScores = GamelogTable(DB)
Lineups = LineupTable(DB)
Matchups = MatchupTable(DB)
PlayerProps = PlayerPropTable(DB)
DefenseRankings = DefenseRankingTable(DB)
