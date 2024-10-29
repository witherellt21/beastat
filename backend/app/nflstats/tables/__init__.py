from scrapp import tables

from .models import (
    NFLDefensiveSplitsTable,
    NFLKickAndPuntReturnSplitsTable,
    NFLPlayersTable,
    NFLRushingAndReceivingSplitsTable,
    NFLTeamsTable,
)

tables.schema.register(NFLTeamsTable())
tables.schema.register(NFLPlayersTable())
tables.schema.register(NFLKickAndPuntReturnSplitsTable())
tables.schema.register(NFLRushingAndReceivingSplitsTable())
tables.schema.register(NFLDefensiveSplitsTable())
