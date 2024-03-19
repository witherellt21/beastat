import json
import logging
import os
import uuid
from typing import Optional

import peewee
from playhouse.shortcuts import model_to_dict
from sql_app.database import DB
from sql_app.models import Team
from sql_app.register.base import BaseTable
from sql_app.serializers import ReadTeamSerializer, TeamSerializer

logger = logging.getLogger("main")


class TeamTable(BaseTable):
    MODEL_CLASS = Team
    SERIALIZER_CLASS = TeamSerializer
    READ_SERIALIZER_CLASS = ReadTeamSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = TeamSerializer
    PKS = ["name"]

    def get_team_by_abbr(self, team_abbr: str) -> Optional[ReadTeamSerializer]:
        try:
            db_row = Team.get(
                (team_abbr == Team.abbr) | (Team.alt_abbrs.contains(team_abbr))
            )

            return ReadTeamSerializer(**model_to_dict(db_row))

        except peewee.DoesNotExist as e:
            return None


Teams = TeamTable(DB)

# print(os.getcwd())
with open("sql_app/static_data/teams.json", "r") as teams_file:
    new_data = {}
    team_data = json.load(teams_file)
    for name, abbreviations in team_data.items():
        Teams.update_or_insert_record(
            data={
                "id": uuid.uuid4(),
                "abbr": abbreviations[0],
                "name": name,
                "alt_abbrs": abbreviations[1:],
            }
        )
# with open("./sql_app/static_data/teams_new.json", "w") as teams_new:
#     json.dump(new_data, teams_new)
