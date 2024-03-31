# import imp
# import os
# from pathlib import Path
# from typing import Generator

# from base.scraper import BaseScraper


# def __load_all__(dir=".") -> dict[str, BaseScraper]:
#     scrapers: dict[str, BaseScraper] = {}

#     if dir == ".":
#         dir = str(Path(__file__).parent)

#     list_modules = os.listdir(dir)
#     list_modules.remove("__init__.py")
#     list_modules.remove("__pycache__")
#     list_modules.remove("util")
#     for module_name in list_modules:
#         is_dir_module: bool = os.path.isdir(
#             dir + "/" + module_name
#         ) and "__init__.py" in os.listdir(dir + "/" + module_name)

#         is_file_module: bool = module_name.split(".")[-1] == "py"

#         if is_dir_module:
#             scraper = imp.load_source(
#                 "module", dir + os.sep + module_name + os.sep + "__init__.py"
#             )

#         elif is_file_module:
#             scraper = imp.load_source("module", dir + os.sep + module_name)

#         else:
#             continue

#         scrapers[scraper.SCRAPER.name] = scraper.SCRAPER

#     return scrapers


# _scrapers = __load_all__(dir=".")


# def __iter__() -> Generator[tuple[str, BaseScraper], int, None]:
#     i = 0
#     n = len(_scrapers)
#     for scraper_name, scraper in _scrapers.items():
#         yield scraper_name, scraper
