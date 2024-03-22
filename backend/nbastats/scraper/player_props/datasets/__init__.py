from os import name

from base.scraper import BaseHTMLDatasetConfig

# from .tables import TABLES
from . import config, player_props_dataset

dataset = BaseHTMLDatasetConfig(
    name=getattr(player_props_dataset, "NAME", None),
    default_query_set=getattr(player_props_dataset, "DEFAULT_QUERY_SET", None),
    base_download_url=getattr(player_props_dataset, "BASE_DOWNLOAD_URL", ""),
    table_configs=player_props_dataset.TABLES,
)

DATASETS: dict[str, BaseHTMLDatasetConfig] = {dataset.name: dataset}
