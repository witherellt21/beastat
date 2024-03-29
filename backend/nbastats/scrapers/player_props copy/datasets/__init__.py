import imp
import os
from pathlib import Path

from base.scraper import BaseHTMLDatasetConfig


def __load_all__(dir=".") -> list[BaseHTMLDatasetConfig]:
    datasets: list[BaseHTMLDatasetConfig] = []

    if dir == ".":
        dir = str(Path(__file__).parent)

    list_modules = os.listdir(dir)
    list_modules.remove("__init__.py")
    list_modules.remove("__pycache__")
    for module_name in list_modules:
        is_dir_module: bool = os.path.isdir(
            dir + "/" + module_name
        ) and "__init__.py" in os.listdir(dir + "/" + module_name)

        is_file_module: bool = module_name.split(".")[-1] == "py"

        if is_dir_module:
            dataset_config = imp.load_source(
                "module", dir + os.sep + module_name + os.sep + "__init__.py"
            )

        elif is_file_module:
            dataset_config = imp.load_source("module", dir + os.sep + module_name)

        dataset = BaseHTMLDatasetConfig(
            name=getattr(dataset_config, "NAME", None),
            default_query_set=getattr(dataset_config, "DEFAULT_QUERY_SET", None),
            base_download_url=getattr(dataset_config, "BASE_DOWNLOAD_URL", ""),
            table_configs=getattr(dataset_config, "TABLES", None),
        )

        datasets.append(dataset)

    return datasets


_datasets = __load_all__(dir=".")


def __iter__():
    i = 0
    print(_datasets)
    n = len(_datasets)
    for dataset in _datasets:
        yield dataset
