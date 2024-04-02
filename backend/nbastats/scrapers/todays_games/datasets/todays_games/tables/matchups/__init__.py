import uuid

from nbastats.sql_app.register import Matchups

# from .util import *

NAME = "Matchups"

SQL_TABLE = Matchups

IDENTIFICATION_FUNCTION = lambda tables: next(
    (table for table in tables if "position" in table.columns),
    None,
)

CONFIG = {
    "transformations": {("position", "id"): lambda x: uuid.uuid4()},
}
