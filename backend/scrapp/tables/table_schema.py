from typing import Optional

from .base_table import BaseTable


class TableSchema:

    def __new__(cls):
        raise Exception(
            "Cannot be directly instantiated. Instead call 'get_instance' with a specified name for the manager."
        )

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(TableSchema, cls).__new__(cls)
            cls.instance.__init__()
        return cls.instance

    def __init__(self) -> None:
        self.tables: dict[str, BaseTable] = {}

    def register(self, table: BaseTable, table_name: Optional[str] = None) -> None:
        if not table_name:
            table_name = table.name

        if table_name in self.tables:
            raise Exception("Table '{}' already exists.".format(table_name))

        self.tables[table_name] = table

    def table(self, table_name: str):
        if table_name not in self.tables:
            raise Exception("Table '{}' does not exist.".format(table_name))

        return self.tables[table_name]

    def get_table_registry(self) -> dict[str, BaseTable]:
        return self.tables


schema = TableSchema.get_instance()
