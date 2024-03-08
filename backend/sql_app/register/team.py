from sql_app.models import Team
from sql_app.serializers import TeamSerializer, ReadTeamSerializer

from sql_app.database import DB
from sql_app.register.base import BaseTable

import logging

logger = logging.getLogger("main")


class TeamTable(BaseTable):
    MODEL_CLASS = Team
    SERIALIZER_CLASS = TeamSerializer
    READ_SERIALIZER_CLASS = ReadTeamSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = TeamSerializer
    PKS = ["id"]


Teams = TeamTable(DB)
