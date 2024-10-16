from scrapp import tables

from .models import (
    NFLKickAndPuntReturnSplitsTable,
    NFLPlayersTable,
    NFLRushingAndReceivingSplitsTable,
    NFLTeamsTable,
)

tables.schema.register(NFLPlayersTable())
tables.schema.register(NFLTeamsTable())
tables.schema.register(NFLKickAndPuntReturnSplitsTable())
tables.schema.register(NFLRushingAndReceivingSplitsTable())
