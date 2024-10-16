from typing import Optional

import pandas as pd
from scrapp.scraper import BaseHTMLTable
from scrapp.scraper.fields import (
    CharField,
    IntegerField,
    ListField,
    TransformationField,
)
from scrapp.scraper.html_table_serializer import BaseHTMLTableSerializer
from scrapp.tables import schema
from unidecode import unidecode


def first(tables: list[pd.DataFrame]) -> Optional[pd.DataFrame]:
    return tables[0]


class PlayerInfoTableEntrySerializer(BaseHTMLTableSerializer):
    id = CharField()
    name = TransformationField(str, lambda name: unidecode(name))
    pos = ListField(str)
    active_from = IntegerField()
    active_to = IntegerField()


player_info_table = BaseHTMLTable(
    "NFLPlayersInfo",
    schema.table("nflplayers"),
    PlayerInfoTableEntrySerializer(),
    identification_function=first,
)
