import logging

import pandas as pd
from nbastats.sql_app.register import PlayerProps

from .utils import PlayerPropsTableEntrySerializer

logger = logging.getLogger("main")

NAME = "PlayerPropsTable"

SQL_TABLE = PlayerProps

IDENTIFICATION_FUNCTION = lambda tables: pd.concat(tables, ignore_index=True)

TABLE_SERIALIZER = PlayerPropsTableEntrySerializer()
