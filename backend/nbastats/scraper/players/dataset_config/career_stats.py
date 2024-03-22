import re
import uuid
from typing import Optional

import numpy as np
import pandas as pd
from base.scraper import BaseHTMLDatasetConfig, QueryArgs, TableConfig
from nbastats.scraper.util.string_helpers import convert_season_to_year
from nbastats.scraper.util.team_helpers import get_team_id_by_abbr
from nbastats.sql_app.register import CareerStatss
from pandas.core.api import DataFrame as DataFrame

IS_SEASON = re.compile(r"^\d{4}")


def has_season_column(tables: list[pd.DataFrame]) -> Optional[pd.DataFrame]:
    data = next(
        (table for table in tables if "Season" in table.columns),
        None,
    )
    return data


class CareerStatsTableConfig(TableConfig):
    """
    Here we will include the cleaning function stuff as class attributes
    """

    STAT_AUGMENTATIONS = {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
    }

    TRANSFORMATIONS = {
        "Season": lambda season: convert_season_to_year(season=season),
        ("PTS", "id"): lambda x: uuid.uuid4(),
        ("Tm", "Tm_id"): get_team_id_by_abbr,
    }

    # DROP_ROWS = {"Tm": }
    PRE_FILTERS = [lambda dataframe: bool(IS_SEASON.match(dataframe["Season"]))]

    _exception_msgs = {
        "load_data": f"Error reading saved player overview from csv.",
        "download_data": f"Error fetching (http) player overview from html.",
    }

    RENAME_COLUMNS = {
        "FG%": "FG_perc",
        "3P": "THP",
        "3PA": "THPA",
        "3P%": "THP_perc",
        "2P": "TWP",
        "2PA": "TWPA",
        "2P%": "TWP_perc",
        "eFG%": "eFG_perc",
        "FT%": "FT_perc",
    }
    RENAME_VALUES = {
        "Tm": {"TOT": np.nan},
        "TWP_perc": {"": np.nan},
        "THP_perc": {"": np.nan},
        "FT_perc": {"": np.nan},
        "FG_perc": {"": np.nan},
        "eFG_perc": {"": np.nan},
    }

    QUERY_SAVE_COLUMNS = {"player_id": "player_id"}
    REQUIRED_FIELDS = ["Season", "G", "Tm"]

    def __init__(self, **kwargs):
        super().__init__(
            identification_function=has_season_column,
            sql_table=CareerStatss,
            **kwargs,
        )

    def cached_data(self, *, query_args: Optional[QueryArgs] = None) -> pd.DataFrame:
        if query_args == None:
            return super().cached_data(query_args=query_args)

        else:

            data = CareerStatss.filter_records(
                query={"player_id": query_args.get("player_id")}, as_df=True
            )

            foreign_keys = CareerStatss.get_foreign_relationships()

            foreign_keys_remap = {
                foreign_key: f"{foreign_key}_id" for foreign_key in foreign_keys
            }

            data = data.rename(columns=foreign_keys_remap)

            return data


class CareerStatsDatasetConfig(BaseHTMLDatasetConfig):

    def __init__(self, **kwargs):
        kwargs.setdefault("name", "CareerStats")

        super().__init__(**kwargs)

    @property
    def base_download_url(self):
        return "http://www.basketball-reference.com/players/{player_last_initial}/{player_id}.html"
