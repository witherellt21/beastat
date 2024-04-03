import logging
from typing import Optional

import peewee
from base.sql_app.register import BaseTable
from nbastats.sql_app.models import Team
from nbastats.sql_app.serializers import ReadTeamSerializer, TeamSerializer
from playhouse.shortcuts import model_to_dict

logger = logging.getLogger("main")


class TeamTable(BaseTable):
    MODEL_CLASS = Team
    SERIALIZER_CLASS = TeamSerializer
    READ_SERIALIZER_CLASS = ReadTeamSerializer
    PKS = ["name"]

    def get_team_by_abbr(self, team_abbr: str) -> Optional[ReadTeamSerializer]:
        try:
            db_row = Team.get(
                (team_abbr == Team.abbr) | (Team.alt_abbrs.contains(team_abbr))
            )

            return ReadTeamSerializer(**model_to_dict(db_row))

        except peewee.DoesNotExist as e:
            return None
