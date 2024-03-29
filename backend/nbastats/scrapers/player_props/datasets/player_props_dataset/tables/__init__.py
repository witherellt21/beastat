# import imp
# import os
# from pathlib import Path

# from base.scraper import TableConfig


# def __load_all__(dir=".") -> dict[str, TableConfig]:
#     tables: dict[str, TableConfig] = {}

#     if dir == ".":
#         dir = str(Path(__file__).parent)

#     list_modules = os.listdir(dir)
#     list_modules.remove("__init__.py")
#     list_modules.remove("__pycache__")
#     for module_name in list_modules:
#         is_dir_module: bool = os.path.isdir(
#             dir + "/" + module_name
#         ) and "__init__.py" in os.listdir(dir + "/" + module_name)

#         is_file_module: bool = module_name.split(".")[-1] == "py"

#         if is_dir_module:
#             table = imp.load_source(
#                 "module", dir + os.sep + module_name + os.sep + "__init__.py"
#             )

#         elif is_file_module:
#             table = imp.load_source("module", dir + os.sep + module_name)

#         CONFIG = getattr(table, "CONFIG", None)

#         if not CONFIG:
#             raise ValueError(f"No configuration specified for {module_name}.")

#         identification_function = CONFIG.pop("identification_function", None)
#         sql_table = CONFIG.pop("sql_table", None)
#         name = CONFIG.pop("name", None)

#         if not identification_function or not sql_table or not name:
#             raise ValueError(f"Configuration for {module_name} is incorrect.")

#         table = TableConfig(
#             identification_function=identification_function,
#             sql_table=sql_table,
#             name=name,
#             **CONFIG,
#         )

#         tables[table.name] = table

#     return tables


# _tables = __load_all__(dir=".")


# def __iter__():
#     i = 0
#     print(_tables)
#     n = len(_tables)
#     for table in _tables:
#         yield table
