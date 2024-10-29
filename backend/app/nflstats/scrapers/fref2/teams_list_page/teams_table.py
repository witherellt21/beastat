from typing import Any

from pandas import DataFrame
from scrapp.core.dataframes import BaseDataframeValidator
from scrapp.core.dataframes.serializers.fields import CharField, TransformationField
from scrapp.scraper import DataframeController
from scrapp.tables import schema

from .util import extract_team_abbr_from_team_name, extract_team_id_from_team_link


class NFLTeamsDataframeValidator(BaseDataframeValidator):
    id = TransformationField(
        str,
        extract_team_id_from_team_link,
        from_columns=["Unnamed: 0_level_0_Tm_link"],
    )
    name = CharField(from_column="Unnamed: 0_level_0_Tm")
    abbr = TransformationField(
        str, extract_team_abbr_from_team_name, from_columns=["name"]
    )


table = DataframeController(
    "NFLTeams", NFLTeamsDataframeValidator(), db_table=schema.table("nflteams")
)
