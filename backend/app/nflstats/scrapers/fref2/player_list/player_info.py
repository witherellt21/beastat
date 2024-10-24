from typing import Optional

import pandas as pd
from scrapp.core.dataframes import BaseDataframeValidator
from scrapp.core.dataframes.serializers import (
    CharField,
    IntegerField,
    ListField,
    TransformationField,
)
from scrapp.scraper import DataframeController
from scrapp.tables import schema
from unidecode import unidecode

from ..player_summary.kick_and_punt_return_splits import (
    kick_and_punt_return_splits_table,
)


class PlayerInfoTableEntrySerializer(BaseDataframeValidator):
    id = CharField()
    name = TransformationField(str, lambda name: unidecode(name))
    # team_id = IntegerField(post_validated=True)
    pos = ListField(str)
    active_from = IntegerField()
    active_to = IntegerField(filters=[lambda x: x == 2024])


player_info_table = DataframeController(
    "NFLPlayersInfo",
    PlayerInfoTableEntrySerializer(),
    db_table=schema.table("nflplayers"),
)

# player_info_table.add_inheritance(kick_and_punt_return_splits_table.data, ["team_id"])
