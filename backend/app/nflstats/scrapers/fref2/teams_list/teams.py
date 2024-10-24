from scrapp.core.dataframes import BaseDataframeValidator
from scrapp.core.dataframes.serializers.fields import CharField, TransformationField
from scrapp.scraper import DataframeController
from scrapp.tables import schema


class NFLTeamsDataframeValidator(BaseDataframeValidator):
    id = TransformationField(
        str,
        lambda link: link.rsplit("/", 2)[1].split(".")[0] if link else None,
        from_columns=["Unnamed: 0_level_0_Tm_link"],
        null=False,
    )
    name = CharField(from_column="Unnamed: 0_level_0_Tm")
    abbr = TransformationField(
        str, lambda name: name[:3].upper(), from_columns=["name"]
    )


teams_table = DataframeController(
    "NFLTeams", NFLTeamsDataframeValidator(), db_table=schema.table("nflteams")
)
