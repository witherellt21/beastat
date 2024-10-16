import uuid

from nbastats.db.register import DefenseRankings

NAME = "DefVsPos"

SQL_TABLE = DefenseRankings

IDENTIFICATION_FUNCTION = lambda tables: tables[0]

CONFIG = {
    "transformations": {("stat", "id"): lambda x: uuid.uuid4()},
}
