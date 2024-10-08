import pandas as pd
import requests
from bs4 import BeautifulSoup, element
from nbastats import constants
from nbastats.db.register import Teams


def scrape_data(url: str) -> list[pd.DataFrame] | None:
    page: requests.Response = requests.get(url)
    soup: BeautifulSoup = BeautifulSoup(page.content, "html.parser")

    table = soup.find("table", id="data-table")

    if type(table) != element.Tag:
        return None

    header = table.thead
    body = table.tbody

    if type(body) != element.Tag:
        return None

    dataframe = pd.DataFrame(
        columns=["id", "team_id", "pos", "PTS", "REB", "AST", "THP", "STL", "BLK", "TO"]
    )

    class_base = "GC-0"
    positions = ["ALL"] + constants.BASKETBALL_POSITIONS
    df_index = 0
    for position in positions:  # type: ignore
        defenses = body.find_all("tr", class_=f"{class_base} {position}")

        for defense in defenses:
            if type(defense) != element.Tag:
                continue

            row_cells = defense.find_all("td")

            if len(row_cells) == 10:
                team_abbr = row_cells[0].span.text

                data = {
                    "team_id": Teams.get_team_id_or_nan(team_abbr),
                    "pos": position,
                    "PTS": float(row_cells[2].text),
                    "REB": float(row_cells[3].text),
                    "AST": float(row_cells[4].text),
                    "THP": float(row_cells[5].text),
                    "STL": float(row_cells[6].text),
                    "BLK": float(row_cells[7].text),
                    "TO": float(row_cells[8].text),
                }

                data_row = pd.DataFrame(data, index=[df_index])
                data_row["OVR"] = data_row.sum(axis=1, numeric_only=True)

                dataframe = pd.concat([dataframe, data_row])

                df_index += 1

    stat_categories = ["PTS", "REB", "AST", "THP", "STL", "BLK", "TO", "OVR"]
    stat_tables = []
    for stat in stat_categories:
        stat_table = dataframe.pivot_table(
            values=stat, index=["team_id"], columns=["pos"]
        )

        for position in positions:
            stat_table[position] = stat_table[position].sort_values().rank().astype(int)

        stat_table["stat"] = stat
        stat_tables.append(stat_table)

    result = pd.concat(stat_tables).reset_index()
    return [result]


NAME = "DefVsPos"

BASE_DOWNLOAD_URL = (
    "https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position"
)

CONFIG = {
    "extract_tables": scrape_data,
}
