import logging
import threading
import traceback
from time import sleep, time
from typing import Literal, NotRequired, Optional, Union, Unpack

import numpy as np
import pandas as pd
from core.scraper.base.table import TableConfig
from core.scraper.base.util import QueryArgs, QuerySet
from core.scraper.util.dependency_tree_helpers import topological_sort_dependency_tree
from typing_extensions import TypedDict

from .dataset import BaseHTMLDatasetConfig

DEFAULT_LOG_FORMATTER = logging.Formatter(
    "[{levelname:^10}] [ {asctime} ] [{threadName:^20}]  {message}",
    "%I:%M:%S %p",
    style="{",
)
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(DEFAULT_LOG_FORMATTER)


class ScraperKwargs(TypedDict):
    datasets: NotRequired[dict[str, BaseHTMLDatasetConfig]]
    log_level: NotRequired[int]
    download_rate: NotRequired[int]
    active: NotRequired[bool]
    align: NotRequired[Union[Literal["nested"], Literal["inline"]]]


class BaseScraper(threading.Thread):

    def __init__(self, *, name: str, **kwargs: Unpack[ScraperKwargs]) -> None:
        threading.Thread.__init__(self, name=name)

        self._dataset_configs: dict[str, BaseHTMLDatasetConfig] = (
            kwargs.get("datasets") or {}
        )
        self._configured: bool = False

        self.RUNNING: Literal[False, True] = kwargs.get("active", True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(kwargs.get("log_level", logging.INFO))
        self.logger.addHandler(STREAM_HANDLER)

        self.download_rate = kwargs.get("download_rate", 5)
        self.last_download_time = time()

        self.alignment = kwargs.get("align", "inline")

    def __str__(self):
        return f"{self.name}Scraper"

    def set_log_level(self, log_level: int):
        self.logger.setLevel(log_level)

    def add_dataset_config(self, dataset_config: BaseHTMLDatasetConfig):
        """
        Add a dataset configuration to the scraper.
        """
        self._dataset_configs[dataset_config.name] = dataset_config

    def configure(self):
        """
        Configure the dataset_configurations based on dependency tree.
        Must be run before the datascraper starts.
        """
        sorted = topological_sort_dependency_tree(dependency_tree=self._dataset_configs)  # type: ignore

        dataset_configs: dict[str, BaseHTMLDatasetConfig] = {}

        for dataset_name in sorted:
            self._dataset_configs[dataset_name]._configure()

        if self.alignment == "nested":
            current_config = dataset_configs[sorted[0]] = self._dataset_configs[
                sorted[0]
            ]
            for dataset_name in sorted[1:]:
                nested_config = self._dataset_configs[dataset_name]
                current_config.add_nested_dataset(dataset=nested_config)
                current_config = nested_config

        else:
            for dataset_name in sorted:
                dataset_configs[dataset_name] = self._dataset_configs[dataset_name]

        self._dataset_configs = dataset_configs

        self._configured = True

    def identify_table(
        self, table_config: TableConfig, tables: list[pd.DataFrame]
    ) -> Optional[pd.DataFrame]:
        data = table_config._identification_function(tables)
        # data = next(
        #     (table for table in tables if table_config._identification_function(table)),
        #     None,
        # )
        return data

    def download_and_process_query(
        self, *, config: BaseHTMLDatasetConfig, query_args: Optional[QueryArgs] = None
    ) -> None:

        # get the download url from the query args
        url = (
            config._get_download_url(query_args=query_args)
            if query_args
            else config.base_download_url
        )

        # if this specific query is already save in the database, fetch that instead
        config.load_data_from_cache(query_args=query_args)
        if all(
            [
                table_config.data_source == "cached"
                for table_config in config._table_configs.values()
            ]
        ):
            config.data_source = "cached"

        else:
            config.data_source = "downloaded"

            # self.logger.info(f"Downloading data for {config.name}.")
            if self.last_download_time:
                wait = max(self.last_download_time - time() + self.download_rate, 0)
            else:
                wait = 0

            if wait:
                sleep(wait)

            tables = config.extract_tables(url=url)
            self.last_download_time = time()

            # find the table matching the identification function. Error if not found
            for table_name, table_config in config._table_configs.items():
                data = self.identify_table(table_config=table_config, tables=tables)

                if data is None:
                    # print(tables)
                    raise ValueError(f"No matching table found for {table_name}.")

                # Add any of the query arguments to the dataframe if desired.
                for (
                    df_column,
                    query_key,
                ) in table_config.table_serializer.query_arg_fields.items():
                    if query_args and query_key in query_args:
                        data[df_column] = query_args[query_key]

                # Apply each cleaning function
                try:
                    table_config.data = table_config._clean_data(data=data)
                    # table_config.data_source = "downloaded"
                    self.logger.info(f"Downloaded data for {table_config.name}.")
                except Exception as e:
                    raise Exception(f"{table_config.name}: {e}")

                # return data

    def save_data(self, dataset_config: BaseHTMLDatasetConfig) -> None:
        """
        Save the data for the dataset and any nested datasets.
        """
        self.logger.info("Saving data to database.")

        # Use staging if there is backed up data that needs to be saved that was
        # waiting for a dependency
        for table_config in dataset_config._table_configs.values():
            if table_config.data_source != "cached":
                self.save_table(table_config=table_config)

        # recurse into nested datatsets
        for nested_config in dataset_config.nested_datasets:
            self.save_data(dataset_config=nested_config)

    def save_table(self, table_config: TableConfig) -> None:
        """
        Save the data for the dataset and any nested datasets.
        """
        self.logger.info(f"Saving data for table {table_config.name}.")

        # Use staging if there is backed up data that needs to be saved that was
        # waiting for a dependency
        data = (
            table_config.data
            if table_config.staged_data.empty
            else table_config.staged_data
        )

        # reset the staged data as we have successfully downloaded
        table_config.staged_data = pd.DataFrame()

        data = data.fillna(np.nan).replace([np.nan], [None])

        for index, row in data.iterrows():
            row_data = row.to_dict()
            row_data["id"] = index
            if index == None:
                self.logger.warning(row)
            table_config._sql_table.update_or_insert_record(data=row_data)

        self.logger.debug(f"\n{data}")

    def perform_single_pass(
        self, dataset_config: BaseHTMLDatasetConfig, query_args: Optional[QueryArgs]
    ):
        """
        Perform a single pass through of a dataset using specific query args and
        nesting inside nested datasets.
        """
        self.download_and_process_query(config=dataset_config, query_args=query_args)

        for nested_dataset in dataset_config.nested_datasets:
            self.process_dataset(
                dataset_config=nested_dataset, query_set=nested_dataset.query_set
            )

    def resolve_inheritances(
        self, *, dataset_config: BaseHTMLDatasetConfig, set_data_source: bool = True
    ) -> Optional[bool]:
        """
        Backwards resolve any inherited fields after all dependencies have been exhausted.
        Specify confirm_update as True to return a boolean designating where there was any
        update performed on the dataset configuration.
        """
        for table_name, table_config in dataset_config._table_configs.items():
            if set_data_source:
                data = table_config.data.copy()

            for inheritance in table_config.inheritances:
                if not inheritance.source.staged_data.empty:
                    inherited_data = inheritance.inheritance_function(
                        inheritance.source.staged_data
                    )

                    table_config.data.update(inherited_data)

            if set_data_source:
                if not data.equals(table_config.data):
                    dataset_config.data_source = "downloaded"
                    table_config.data_source = "downloaded"

    def process_dataset(
        self, dataset_config: BaseHTMLDatasetConfig, query_set: Optional[QuerySet]
    ):
        """
        Process an entire dataset by iterating through its query set and
        performing a single pass, resolving inheritances, and then saving
        all data (including nested dataset functionality).
        """

        if query_set is None:
            if dataset_config.static:
                ready_for_save: bool = all(
                    [
                        dependency.source.data_source == "cached"
                        for dependency in dataset_config.dependencies
                    ]
                )

                self.perform_single_pass(dataset_config=dataset_config, query_args=None)

                self.resolve_inheritances(
                    dataset_config=dataset_config, set_data_source=True
                )

                self.logger.debug(
                    f"{dataset_config.name}: Ready for save = {ready_for_save} : Is already saved = {dataset_config.data_source == 'cached'}"
                )

                if dataset_config.dependencies and not ready_for_save:
                    for table_config in dataset_config._table_configs.values():
                        table_config.staged_data = pd.concat(
                            [table_config.staged_data, table_config.data]
                        )

                elif dataset_config.data_source != "cached":
                    self.save_data(dataset_config=dataset_config)

                else:
                    self.logger.info(
                        f"No new data to save for dataset: {dataset_config.name}."
                    )
        else:
            ready_for_save: bool = all(
                [
                    dependency.source.data_source == "cached"
                    for dependency in dataset_config.dependencies
                ]
            )

            idx, n = 0, len(query_set)

            self.logger.info(f"Beginning download of query set: {query_set}")
            for query in query_set:
                if self.RUNNING == False:
                    break

                self.perform_single_pass(
                    dataset_config=dataset_config, query_args=query
                )

                self.resolve_inheritances(
                    dataset_config=dataset_config, set_data_source=True
                )

                self.logger.debug(
                    f"{dataset_config.name}: Ready for save = {ready_for_save} : Is already saved = {dataset_config.data_source == 'cached'}"
                )

                if dataset_config.dependencies and not ready_for_save:
                    for table_config in dataset_config._table_configs.values():
                        table_config.staged_data = pd.concat(
                            [table_config.staged_data, table_config.data]
                        )

                elif dataset_config.data_source != "cached":
                    self.save_data(dataset_config=dataset_config)

                else:
                    self.logger.info(
                        f"No new data to save for dataset: {dataset_config.name}."
                    )

                idx += 1
                self.logger.info(
                    f"{dataset_config.name} query set {round(idx/n * 100, 2)}% complete."
                )

    def execute(self):
        """
        Make a forward pass downloading and saving each dataset in
        the scraper's configuration. To add more datasets, use the 'add_dataset'
        method.
        """
        if not self._dataset_configs:
            raise Exception(
                "No datasets defined - to add datasets, use the 'add_dataset' method."
            )

        for dataset_name, dataset_info in self._dataset_configs.items():
            if self.RUNNING == False:
                break

            dataset_info._configure()

            query_set = dataset_info.query_set

            self.process_dataset(dataset_info, query_set=query_set)

    def kill_process(self, *args):
        """
        Kill the running thread and stop the scraper.
        """
        self.RUNNING = False
        self.logger.critical(f"PROCESS KILLED FOR {self.name}.")

    def run(self):

        if not self._configured:
            raise Exception(
                "Must call '.configure()' on the scraper before running it."
            )

        self.logger.info(f"Starting scraper: {self.name}...")

        consecutive_failures: int = 0

        # this will include gamelog dataset
        while self.RUNNING:
            if consecutive_failures >= 10:
                self.kill_process()

            try:
                self.execute()
                consecutive_failures = 0
            except Exception as e:
                self.logger.warning(traceback.format_exc())
                consecutive_failures += 1
