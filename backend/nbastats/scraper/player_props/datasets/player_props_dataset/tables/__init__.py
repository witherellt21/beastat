from os import name

from base.scraper import TableConfig
from player_props_table import CONFIG

identification_function = CONFIG.pop("identification_function")
sql_table = CONFIG.pop("sql_table")
name = CONFIG.pop("name")

if not identification_function or not sql_table or not name:
    raise ValueError()

table = TableConfig(
    identification_function=identification_function,
    sql_table=sql_table,
    name=name,
    **CONFIG
)

TABLES: dict[str, TableConfig] = {table.name: table}
