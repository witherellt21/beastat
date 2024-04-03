# from typing import Any, Callable, NotRequired, Optional, TypeAlias

# import pandas as pd
# from typing_extensions import TypedDict

# # from .base import QuerySet, TableConfig

# QueryArgs: TypeAlias = dict[str, Any]
# QuerySet: TypeAlias = list[QueryArgs]


# class TableConfigArgs(TypedDict):
#     # identification_function: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]]
#     # sql_table: BaseTable

#     datetime_columns: NotRequired[dict[str, str]]

#     # Adds column labled by key using a synctatic string or a callable function with argument that accepts the full dataset.
#     stat_augmentations: NotRequired[
#         dict[str, str | Callable[[pd.DataFrame], pd.Series]]
#     ]

#     # Select specific rows from the dataset based on callable filter functions
#     filters: NotRequired[list[Callable]]
#     rename_columns: NotRequired[dict[str, str]]
#     rename_values: NotRequired[dict[str, dict[Any, Any]]]
#     nan_values: NotRequired[list[str]]

#     # A function to tranform a specific column (key) on a dataset by a callable function (value) uses apply method
#     transformations: NotRequired[dict[str | tuple[str, str], Callable[[Any], Any]]]
#     required_fields: NotRequired[list[str]]
#     query_save_columns: NotRequired[dict[str, str]]
#     href_save_map: NotRequired[dict[str, str]]


# class DatasetConfigKwargs(TypedDict):
#     # base_download_url: str
#     # name: str
#     table_configs: NotRequired[Optional[dict[str, TableConfig]]]
#     default_query_set: NotRequired[Optional[QuerySet]]


# class ScraperKwargs(TypedDict):
#     log_level: NotRequired[int]
#     download_rate: NotRequired[int]
