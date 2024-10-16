from typing import Callable, Optional

import pandas as pd
from pydantic import BaseModel
from scrapp.scraper import (
    BaseHTMLTableSerializer,
    HTMLTableArgs,
    WebPageKwargs,
    WebScraperKwargs,
)
from scrapp.tables import BaseTable
from typing_extensions import TypedDict


class HTMLTableFileConfig(BaseModel):
    IDENTIFICATION_FUNCTION: Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]]
    SQL_TABLE: BaseTable
    NAME: str
    TABLE_SERIALIZER: BaseHTMLTableSerializer
    CONFIG: HTMLTableArgs = {}


class WebPageFileConfig(BaseModel):
    BASE_DOWNLOAD_URL: str
    NAME: str
    CONFIG: WebPageKwargs = {}


class WebScraperDependencyType(TypedDict):
    source_name: str
    source_table_name: str
    query_set_provider: Callable[[pd.DataFrame], list[dict[str, str]]]


class WebScraperInheritanceType(TypedDict):
    source: tuple[str, str]
    inheritance_function: Callable[[pd.DataFrame], pd.DataFrame]


class WebScraperFileConfig(BaseModel):
    NAME: str
    DEPENDENCIES: dict[str, WebScraperDependencyType] = {}
    INHERITANCES: dict[tuple[str, str], WebScraperInheritanceType] = {}
    CONFIG: WebScraperKwargs = {}
