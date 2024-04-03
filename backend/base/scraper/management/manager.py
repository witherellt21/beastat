import imp
import os
from csv import excel_tab
from pathlib import Path
from pprint import PrettyPrinter
from typing import Callable, Optional

import pandas as pd
from base.scraper.base import (
    BaseHTMLDatasetConfig,
    BaseScraper,
    DatasetConfigDependencyKwargs,
    DatasetConfigKwargs,
    ScraperKwargs,
    TableConfig,
    TableConfigArgs,
)
from base.scraper.base.table_entry_serializers import BaseTableEntrySerializer
from base.scraper.util.util import camel_to_snake_case
from base.sql_app.register.base_table import BaseTable
from pydantic import BaseModel, ValidationError
from typing_extensions import TypedDict

pp = PrettyPrinter(depth=4)


class TableConfigFileParams(BaseModel):
    IDENTIFICATION_FUNCTION: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]]
    SQL_TABLE: BaseTable
    NAME: str
    TABLE_SERIALIZER: BaseTableEntrySerializer
    CONFIG: TableConfigArgs = {}


class DatasetConfigFileParams(BaseModel):
    BASE_DOWNLOAD_URL: str
    NAME: str
    # DEPENDENCIES: list[str]
    CONFIG: DatasetConfigKwargs = {}


class FileConfigDependencyType(TypedDict):
    source_name: str
    source_table_name: str
    query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]]


class FileConfigInheritanceType(TypedDict):
    source: tuple[str, str]
    inheritance_function: Callable[[pd.DataFrame], pd.DataFrame]


class ScraperConfigFileParams(BaseModel):
    NAME: str
    DEPENDENCIES: dict[str, FileConfigDependencyType] = {}
    INHERITANCES: dict[tuple[str, str], FileConfigInheritanceType] = {}
    CONFIG: ScraperKwargs = {}


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


def load_tables(path: str) -> dict[str, TableConfig]:
    tables: dict[str, TableConfig] = {}

    list_modules = os.listdir(path)
    list_modules = ignore_modules(modules=list_modules)

    for module_name in list_modules:
        is_file = is_file_module(module_name=module_name)
        is_dir = is_dir_module(module_path=path + os.sep + module_name)

        # print(module_name)

        if is_dir:
            table_settings = imp.load_source(
                "module", path + os.sep + module_name + os.sep + "__init__.py"
            )

        elif is_file:
            table_settings = imp.load_source("module", path + os.sep + module_name)

        table_settings_config = table_settings.__dict__.copy()

        try:
            obj = TableConfigFileParams(**table_settings_config)

        except ValidationError as exc:
            raise Exception(f"ConfigurationError for file {module_name}: {exc}")

        table = TableConfig(
            identification_function=obj.IDENTIFICATION_FUNCTION,
            sql_table=obj.SQL_TABLE,
            name=obj.NAME,
            table_serializer=obj.TABLE_SERIALIZER,
            **obj.CONFIG,
        )

        tables[table.name] = table

    # print(tables)

    return tables


def load_datasets(path: str = ".") -> dict[str, BaseHTMLDatasetConfig]:
    datasets: dict[str, BaseHTMLDatasetConfig] = {}

    list_modules = os.listdir(path)
    list_modules = ignore_modules(modules=list_modules)

    for module_name in list_modules:
        is_dir = is_dir_module(module_path=path + os.sep + module_name)
        is_file = is_file_module(module_name=module_name)

        # print(module_name)

        if is_dir:
            tables = load_tables(path + os.sep + module_name + os.sep + "tables")

            dataset_settings = imp.load_source(
                "module", path + os.sep + module_name + os.sep + "__init__.py"
            )

        elif is_file:
            dataset_settings = imp.load_source("module", path + os.sep + module_name)
            tables = []

        dataset_settings_config = dataset_settings.__dict__.copy()
        # dataset_settings_config = tables
        # dataset_settings_config[]

        # pp.pprint(dataset_settings_config)

        try:
            obj = DatasetConfigFileParams(**dataset_settings_config)
            obj.CONFIG["table_configs"] = tables
            # pp.pprint(obj.model_dump())

        except ValidationError as exc:
            raise exc

        dataset = BaseHTMLDatasetConfig(
            base_download_url=obj.BASE_DOWNLOAD_URL,
            name=obj.NAME,
            **obj.CONFIG,
        )

        datasets[dataset.name] = dataset

    # print(datasets)

    return datasets


def load_scrapers(path: str = ".") -> list[BaseScraper]:
    scrapers: list[BaseScraper] = []

    if path == ".":
        path = str(Path(__file__).parent)

    list_modules = os.listdir(path)
    list_modules = ignore_modules(modules=list_modules)

    for module_name in list_modules:

        if module_name != "players":
            continue

        is_dir = is_dir_module(module_path=path + os.sep + module_name)
        is_file = is_file_module(module_name=module_name)

        if is_dir:
            datasets = load_datasets(path + os.sep + module_name + os.sep + "datasets")

            scraper_settings = imp.load_source(
                "module", path + os.sep + module_name + os.sep + "__init__.py"
            )

        elif is_file:
            scraper_settings = imp.load_source("module", path + os.sep + module_name)
            datasets = {}

        scraper_settings_config = scraper_settings.__dict__.copy()
        try:
            scraper_config = ScraperConfigFileParams(**scraper_settings_config)

        except ValidationError as exc:
            raise exc

        for base_dataset_name, dependency_config in scraper_config.DEPENDENCIES.items():
            base_dataset = datasets[base_dataset_name]
            source_dataset = datasets[dependency_config["source_name"]]

            base_dataset.add_dependency(
                source=source_dataset,
                meta_data={
                    "table_name": dependency_config["source_table_name"],
                    "query_set_provider": dependency_config["query_set_provider"],
                },
            )

        for base_table_name, inheritance_config in scraper_config.INHERITANCES.items():
            base_table = datasets[base_table_name[0]]._table_configs[base_table_name[1]]
            source_table = datasets[inheritance_config["source"][0]]._table_configs[
                inheritance_config["source"][1]
            ]

            base_table.add_inheritance(
                source=source_table,
                inheritance_function=inheritance_config["inheritance_function"],
            )

        scraper_config.CONFIG["datasets"] = datasets

        scraper = BaseScraper(
            name=scraper_config.NAME,
            **scraper_config.CONFIG,
        )

        scrapers.append(scraper)

    return scrapers


def add_scraper(name: str, path: str = "."):
    # os.makedirs()
    snake_case_name = camel_to_snake_case(name)
    scraper_dir = path + os.sep + snake_case_name
    os.mkdir(scraper_dir)

    with open(scraper_dir + os.sep + "__init__.py", "w") as init_file:
        with open(
            str(Path(__file__).parent)
            + os.sep
            + "file_configs"
            + os.sep
            + "scraper.config",
            "r",
        ) as example_init_file:
            example_config = example_init_file.read()

        init_file.write(example_config)
        init_file.close()

    os.mkdir(scraper_dir + os.sep + "datasets")


def add_dataset(scraper_name: str, name: str, path: str = "."):
    # os.makedirs()
    scraper_dir = path + os.sep + camel_to_snake_case(scraper_name)
    if not os.path.isdir(scraper_dir):
        raise Exception(f"Scraper {scraper_name} does not exist in the path: {path}.")

    datasets_dir = scraper_dir + os.sep + "datasets"
    if not os.path.isdir(datasets_dir):
        os.mkdir(datasets_dir)

    dataset_name = camel_to_snake_case(name)
    dataset_dir = datasets_dir + os.sep + dataset_name

    os.mkdir(dataset_dir)

    with open(dataset_dir + os.sep + "__init__.py", "w") as init_file:
        with open(
            str(Path(__file__).parent)
            + os.sep
            + "file_configs"
            + os.sep
            + "dataset.config",
            "r",
        ) as example_init_file:
            example_config = example_init_file.read()

        init_file.write(example_config)
        init_file.close()

    os.mkdir(dataset_dir + os.sep + "tables")


def add_table(scraper_name: str, dataset_name: str, name: str, path: str = "."):
    # os.makedirs()
    scraper_dir = path + os.sep + camel_to_snake_case(scraper_name)
    if not os.path.isdir(scraper_dir):
        raise Exception(f"Scraper {scraper_name} does not exist in the path: {path}.")

    dataset_dir = (
        scraper_dir + os.sep + "datasets" + os.sep + camel_to_snake_case(dataset_name)
    )
    if not os.path.isdir(dataset_dir):
        raise Exception(
            f"Dataset {dataset_name} does not exist for the scraper {scraper_name} in the path: {path}."
        )

    tables_dir = dataset_dir + os.sep + "tables"
    if not os.path.isdir(tables_dir):
        os.mkdir(tables_dir)

    table_name = camel_to_snake_case(name)
    table_dir = tables_dir + os.sep + table_name

    os.mkdir(table_dir)

    with open(table_dir + os.sep + "__init__.py", "w") as init_file:
        with open(
            str(Path(__file__).parent)
            + os.sep
            + "file_configs"
            + os.sep
            + "table.config",
            "r",
        ) as example_init_file:
            example_config = example_init_file.read()

        init_file.write(example_config)
        init_file.close()

    # os.mkdir(dataset_dir + os.sep + "tables")
