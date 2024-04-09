import logging
from typing import Literal, Optional, overload

import numpy as np
import peewee
from core.sql_app.register import BaseTable
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

    @overload
    def get_team_id_or_nan(self, team_abbr: str) -> str: ...

    @overload
    def get_team_id_or_nan(
        self, team_abbr: str, raise_exception: Literal[True]
    ) -> str: ...

    @overload
    def get_team_id_or_nan(
        self, team_abbr: str, raise_exception: Literal[False]
    ) -> str | float: ...

    def get_team_id_or_nan(
        self, team_abbr: str, raise_exception: bool = True
    ) -> str | float:
        if type(team_abbr) != str and np.isnan(team_abbr):
            return np.nan

        team_abbr = team_abbr.split(",")[0]

        team = self.get_team_by_abbr(team_abbr=team_abbr)

        if not team:
            return np.nan

        return str(team.id)
