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


class PlayerInfoTableEntrySerializer(BaseDataframeValidator):
    id = CharField()
    name = TransformationField(str, lambda name: unidecode(name))
    # team_id = CharField(post_validated=True, from_column="inherited_team_id")
    pos = ListField(str)
    active_from = IntegerField()
    active_to = IntegerField(filters=[lambda x: x == 2024])


table = DataframeController(
    "NFLPlayersInfo",
    PlayerInfoTableEntrySerializer(),
    db_table=schema.table("nflplayers"),
)
