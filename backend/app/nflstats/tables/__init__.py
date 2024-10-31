from scrapp import tables

from .models import (
    NFLDefensiveSplitsTable,
    NFLKickAndPuntReturnSplitsTable,
    NFLOffensiveLinePenaltiesSplitsTable,
    NFLPassingSplitsTable,
    NFLPlayerGameLogs,
    NFLPlayersTable,
    NFLRushingAndReceivingSplitsTable,
    NFLTeamsTable,
    ScraperPageDownloadsTable,
)

tables.schema.register(NFLTeamsTable())
tables.schema.register(NFLPlayersTable())
tables.schema.register(NFLKickAndPuntReturnSplitsTable())
tables.schema.register(NFLRushingAndReceivingSplitsTable())
tables.schema.register(NFLDefensiveSplitsTable())
tables.schema.register(NFLPassingSplitsTable())
tables.schema.register(NFLOffensiveLinePenaltiesSplitsTable())
tables.schema.register(NFLPlayerGameLogs())
tables.schema.register(ScraperPageDownloadsTable())
