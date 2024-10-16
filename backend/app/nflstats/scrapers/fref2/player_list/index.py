from string import ascii_uppercase

import pandas as pd
import requests
from bs4 import BeautifulSoup, element
from scrapp.scraper import BaseWebPage

from .player_info_table import player_info_table


def scrape_data(url: str) -> list[pd.DataFrame]:
    page: requests.Response = requests.get(url)
    soup: BeautifulSoup = BeautifulSoup(page.content, "html.parser")

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


player_list_page = BaseWebPage(
    name="NFLPlayersList",
    base_download_url="http://www.pro-football-reference.com/players/{player_last_initial}/",
    default_query_set=[{"player_last_initial": letter} for letter in ascii_uppercase],
    extract_tables=scrape_data,
    html_tables={player_info_table.name: player_info_table},
)

player_list_page.configure()
