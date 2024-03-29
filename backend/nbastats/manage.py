import imp
import os
from pathlib import Path
from pprint import PrettyPrinter
from typing import Callable, Optional

import pandas as pd
from base.scraper.base import (
    BaseHTMLDatasetConfig,
    BaseScraper,
    DatasetConfigKwargs,
    ScraperKwargs,
    TableConfig,
    TableConfigArgs,
)
from base.sql_app.register.base_table import BaseTable
from pydantic import BaseModel, ValidationError

pp = PrettyPrinter(depth=4)


class TableConfigFileParams(BaseModel):
    IDENTIFICATION_FUNCTION: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]]
    SQL_TABLE: BaseTable
    NAME: str
    CONFIG: TableConfigArgs = {}


class DatasetConfigFileParams(BaseModel):
    BASE_DOWNLOAD_URL: str
    NAME: str
    CONFIG: DatasetConfigKwargs = {}
    TABLES: list[TableConfig]


class ScraperConfigFileParams(BaseModel):
    NAME: str
    CONFIG: ScraperKwargs = {}
    DATASETS: list[BaseHTMLDatasetConfig]


module_ignore = ["__init__.py", "__pycache__", "util"]


def ignore_modules(*, modules: list[str]):
    for module in module_ignore:
        if module in modules:
            modules.remove(module)
    return modules


def is_dir_module(*, module_path: str) -> bool:
    return os.path.isdir(module_path) and "__init__.py" in os.listdir(module_path)


def is_file_module(*, module_name: str) -> bool:
    return module_name.split(".")[-1] == "py"


def load_tables(path: str) -> list[TableConfig]:
    tables: list[TableConfig] = []

    list_modules = os.listdir(path)
    list_modules = ignore_modules(modules=list_modules)

    for module_name in list_modules:
        is_file = is_file_module(module_name=module_name)
        is_dir = is_dir_module(module_path=path + os.sep + module_name)

        if is_dir:
            table_settings = imp.load_source(
                "module", path + os.sep + module_name + os.sep + "__init__.py"
            )

        elif is_file:
            table_settings = imp.load_source("module", path + os.sep + module_name)

        table_settings_config = table_settings.__dict__

        try:
            obj = TableConfigFileParams(**table_settings_config)

        except ValidationError as exc:
            print(exc)
            raise exc

        table = TableConfig(
            identification_function=obj.IDENTIFICATION_FUNCTION,
            sql_table=obj.SQL_TABLE,
            name=obj.NAME,
            **obj.CONFIG,
        )

        tables.append(table)

    return tables


def load_datasets(path: str = ".") -> list[BaseHTMLDatasetConfig]:
    datasets: list[BaseHTMLDatasetConfig] = []

    list_modules = os.listdir(path)
    list_modules = ignore_modules(modules=list_modules)

    for module_name in list_modules:
        print(module_name)

        is_dir = is_dir_module(module_path=path + os.sep + module_name)
        is_file = is_file_module(module_name=module_name)

        if is_dir:
            dataset_settings = imp.load_source(
                "module", path + os.sep + module_name + os.sep + "__init__.py"
            )
            tables = load_tables(path + os.sep + module_name + os.sep + "tables")

        elif is_file:
            dataset_settings = imp.load_source("module", path + os.sep + module_name)
            tables = []

        dataset_settings_config = dataset_settings.__dict__

        dataset_settings_config["TABLES"] = tables

        try:
            obj = DatasetConfigFileParams(**dataset_settings_config)

        except ValidationError as exc:
            print(exc)
            raise exc

        dataset = BaseHTMLDatasetConfig(
            base_download_url=obj.BASE_DOWNLOAD_URL,
            name=obj.NAME,
            **obj.CONFIG,
        )

        datasets.append(dataset)

    return datasets


def load_scrapers(path: str = ".") -> list[BaseScraper]:
    scrapers: list[BaseScraper] = []

    if path == ".":
        path = str(Path(__file__).parent)

    list_modules = os.listdir(path)
    list_modules = ignore_modules(modules=list_modules)

    for module_name in list_modules:
        print(module_name)

        if not module_name == "player_props":
            continue

        is_dir = is_dir_module(module_path=path + os.sep + module_name)
        is_file = is_file_module(module_name=module_name)

        if is_dir:
            scraper_settings = imp.load_source(
                "module", path + os.sep + module_name + os.sep + "__init__.py"
            )
            datasets = load_datasets(path + os.sep + module_name + os.sep + "datasets")

        elif is_file:
            scraper_settings = imp.load_source("module", path + os.sep + module_name)
            datasets = []

        scraper_settings_config = scraper_settings.__dict__

        scraper_settings_config["DATASETS"] = datasets

        try:
            obj = DatasetConfigFileParams(**scraper_settings_config)

        except ValidationError as exc:
            print(exc)
            raise exc

        scraper = BaseScraper(
            name=obj.NAME,
            **obj.CONFIG,
        )

        scrapers.append(scraper)

    return scrapers


from sql_app.register import *


def run_scrapers():
    scrapers = load_scrapers(str(Path(__file__).parent) + os.sep + "scrapers")

    for scraper in scrapers:
        scraper.daemon = True
        scraper.configure(nested_download=True)
        scraper.start()


if __name__ == "__main__":
    import sys

    if sys.argv[0] == "scrape":
        run_scrapers()
