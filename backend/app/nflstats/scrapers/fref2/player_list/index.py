from scrapp import setup

setup()

import logging
from datetime import datetime, timedelta
from string import ascii_uppercase
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup, element
from scrapp.scraper import BaseWebPage
from scrapp.tables.base_table import AdvancedQuery

from .. import player_summary
from .player_info import player_info_table


def first(tables: list[pd.DataFrame]) -> Optional[pd.DataFrame]:
    if len(tables) < 1:
        return None

    return tables[0]


def scrape_data(url: str) -> list[pd.DataFrame]:
    page: requests.Response = requests.get(url)
    soup: BeautifulSoup = BeautifulSoup(page.content, "html.parser")

    # TODO: abstract status codes
    if page.status_code != 200:
        return []

    table = soup.find("div", id="div_players")

    dataframe = pd.DataFrame(
        columns=["id", "name", "pos", "start_season", "end_season"]
    )

    if not isinstance(table, element.Tag):
        return []

    players = table.find_all("p")

    df_index = 0
    for player in players:
        player_data = player.text

        player_link_tag: element.Tag = player.find("a")

        if not player_link_tag:
            return []

        player_link = player_link_tag.attrs.get("href")

        if not player_link:
            return []

        player_id = player_link.rsplit("/", 1)[1].split(".", 1)[0]

        name, rem = player_data.split("(")
        position, seasons = rem.split(")")

        name = name.strip(" ")
        seasons = seasons.strip(" ")
        start_season, end_season = seasons.split("-")
        positions = position.split("-")

        data = {
            "id": player_id,
            "name": name,
            "pos": positions,
            "active_from": start_season,
            "active_to": end_season,
        }

        data_row = pd.DataFrame([data], index=[df_index])
        dataframe = pd.concat([dataframe, data_row])

        df_index += 1

    return [dataframe]


players_page = BaseWebPage(
    name="NFLPlayersList",
    base_download_url="http://www.pro-football-reference.com/players/{player_last_initial}/",
    # default_query_set=[{"player_last_initial": letter} for letter in ascii_uppercase],
    default_query_set=[{"player_last_initial": "A"}],
    extract_tables=scrape_data,
    log_level=logging.DEBUG,
)


players_page.add_table(
    player_info_table,
    identification_function=first,
    stale_condition=AdvancedQuery(
        less_than={"timestamp": datetime.now() - timedelta(days=1)}
        # in_={"id": }
    ),
    # inheritances=[
    #     {
    #         "source": player_summary.kick_and_punt_return_splits_table,
    #         "fields": ["team_id"],
    #     }
    # ],
    # dependencies=[
    #     {
    #         "source": player_info_table,
    #         "fields": ["team_id"],
    #     }
    # ],
)


def load_query_set(web_page: BaseWebPage):
    # table = next(
    #     (
    #         table_config["table"]
    #         for table_config in web_page.table_configs
    #         if table_config["table"].name == "NFLPlayersInfo"
    #     ),
    #     None,
    # )

    # if not table:
    #     raise Exception()

    # if table:
    query_set = [
        {"player_id": player_id}
        for player_id in player_info_table.data.stage["id"].values
    ]

    return query_set


players_page.add_nested_web_page(
    web_page=player_summary.player_summary_page,
    query_set_provider=load_query_set,
    # dependencies=[
    #     {
    #         "source": player_info_table,
    #         "fields": ["team_id"],
    #     }
    # ],
)

# player_info_table.add_inheritance(
#     player_summary.kick_and_punt_return_splits_table.data, ["team_id"]
# )
player_summary.kick_and_punt_return_splits_table.add_dependency(
    source=player_info_table
)


# players_page.configure()
