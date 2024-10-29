from scrapp import tables

from .models import (
    NFLDefensiveSplitsTable,
    NFLKickAndPuntReturnSplitsTable,
    NFLPassingSplitsTable,
    NFLPlayersTable,
    NFLRushingAndReceivingSplitsTable,
    NFLTeamsTable,
)

tables.schema.register(NFLTeamsTable())
tables.schema.register(NFLPlayersTable())
tables.schema.register(NFLKickAndPuntReturnSplitsTable())
tables.schema.register(NFLRushingAndReceivingSplitsTable())
tables.schema.register(NFLDefensiveSplitsTable())
tables.schema.register(NFLPassingSplitsTable())
