from functools import reduce
from typing import Callable, Literal, NotRequired, Optional, Unpack

import pandas as pd
from base.scraper.base.table import TableConfig
from base.scraper.base.util import QueryArgs, QuerySet
from base.scraper.pydantic_validator import PydanticValidatorMixin
from base.scraper.util.dependency_tree_helpers import (
    DependencyKwargs,
    DependentObject,
    topological_sort_dependency_tree,
)
from typing_extensions import TypedDict


def combine_lists_of_dicts(*lists):
    # Combine the lists of dictionaries
    combined_list = [
        reduce(lambda d1, d2: {**d1, **d2}, dicts) for dicts in zip(*lists)
    ]
    return combined_list


class DatasetConfigKwargs(TypedDict):
    table_configs: NotRequired[Optional[dict[str, "TableConfig"]]]
    default_query_set: NotRequired[Optional[QuerySet]]


class DatasetConfigDependencyKwargs(DependencyKwargs):
    table_name: str
    query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]]


class BaseHTMLDatasetConfig(
    DependentObject["BaseHTMLDatasetConfig", "DatasetConfigDependencyKwargs"],
    PydanticValidatorMixin,
):

    def __init__(
        self,
        *,
        name: str,
        base_download_url: str,
        **kwargs: Unpack[DatasetConfigKwargs],
    ):
        super().__init__(name=name, validator=DatasetConfigDependencyKwargs)

        self._base_download_url: str = base_download_url

        # constants specified in intantiation
        self._table_configs: dict[str, TableConfig] = kwargs.get("table_configs") or {}
        self._default_query_set: Optional[QuerySet] = (
            kwargs.get("default_query_set") or []
        )
        self.nested_datasets: list["BaseHTMLDatasetConfig"] = []

        self.data_source: Literal["cached", "downloaded"] = "downloaded"

        args_expected: int = self.base_download_url.count("{}")

        if args_expected:
            self.static = False
        else:
            self.static = True

    def __str__(self):
        return self.name

    @property
    def base_download_url(self) -> str:
        return self._base_download_url
        # raise NotImplementedError(
        #     "Must specify a base download url property in your subclass."
        # )

    @property
    def name(self) -> str:
        return self._name

    def add_table_config(self, *, table_config: TableConfig):
        self._table_configs[table_config.name] = table_config

    def add_nested_dataset(
        self,
        *,
        dataset: "BaseHTMLDatasetConfig",
    ):
        self.nested_datasets.append(dataset)

    @property
    def query_set(self) -> Optional[QuerySet]:
        if self.dependencies:
            query_set_extractions = []
            for dependency in self.dependencies:
                # source_table = dependency.source
                # TODO: verify these links are accurate in configure
                dependency_data = dependency.source._table_configs[
                    dependency.meta.table_name
                ].data

                if dependency_data.empty:
                    raise Exception(
                        f"Dataset {self.__class__.__name__} processed before dependency {dependency.source.__class__.__name__}."
                    )

                query_set_extractions.append(
                    dependency.meta.query_set_provider(dependency_data)
                )

            return combine_lists_of_dicts(*query_set_extractions)

        elif self._default_query_set:
            return self._default_query_set

        elif self.static:
            return None

        else:
            raise Exception(
                "Must specify a default query set if no dependencies are provided."
            )

    def _configure(self):
        sorted = topological_sort_dependency_tree(dependency_tree=self._table_configs)  # type: ignore

        table_configs: dict[str, TableConfig] = {}

        for table_name in sorted:
            table_configs[table_name] = self._table_configs[table_name]

        self._table_configs = table_configs

        self._configured = True

    def _get_download_url(self, *, query_args: QueryArgs) -> str:
        return self.base_download_url.format(**query_args)

    def load_data_from_cache(self, *, query_args: Optional[QueryArgs] = None) -> None:
        for table_name, table_config in self._table_configs.items():
            table_config.data = table_config.cached_data(query_args=query_args)

            if not table_config.data.empty:
                table_config.data_source = "cached"
            else:
                table_config.data_source = "downloaded"

    def extract_tables(self, url: str) -> list[pd.DataFrame]:
        return pd.read_html(url, extract_links="body")
