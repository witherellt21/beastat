import pandas as pd
import requests
from bs4 import BeautifulSoup, element


def get_player_list_page_tables(url: str) -> list[pd.DataFrame]:
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
