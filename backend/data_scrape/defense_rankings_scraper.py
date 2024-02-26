import pandas as pd
from data_scrape.abstract_base_scraper import AbstractBaseScraper
from sql_app.register.defense_ranking import DefenseRankings

from bs4 import BeautifulSoup, ResultSet, element
import requests


class DefenseRankingsScraper(AbstractBaseScraper):
    TABLE = DefenseRankings

    TEAM_ABR_REMAPS = {"NOR": "NOP"}

    @property
    def download_url(self) -> str:
        return (
            "https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position"
        )

    def get_query_set(self) -> list[dict[str, str]] | None:
        return None

    def select_dataset_from_html_tables(
        self, *, datasets: list[pd.DataFrame]
    ) -> pd.DataFrame:
        return datasets[0]

    def scrape_data(self, *, url: str) -> list[pd.DataFrame] | None:
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
            columns=[
                "team",
                "team_abr",
                "pos",
                "PTS",
                "REB",
                "AST",
                "THP",
                "STL",
                "BLK",
                "TO",
            ]
        )

        class_base = "GC-0"
        positions = ["ALL", "PG", "SG", "SF", "PF", "C"]
        df_index = 0
        for position in positions:  # type: ignore
            defenses = body.find_all("tr", class_=f"{class_base} {position}")

            for defense in defenses:
                if type(defense) != element.Tag:
                    continue

                row_cells = defense.find_all("td")

                if len(row_cells) == 10:
                    team_abr = self.__class__.TEAM_ABR_REMAPS.get(
                        row_cells[0].span.text, row_cells[0].span.text
                    )

                    data = {
                        "team": row_cells[0].contents[1],
                        "team_abr": team_abr,
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
                values=stat, index=["team", "team_abr"], columns=["pos"]
            )

            for position in positions:
                stat_table[position] = (
                    stat_table[position].sort_values().rank().astype(int)
                )

            stat_table["stat"] = stat
            stat_tables.append(stat_table)

        result = pd.concat(stat_tables).reset_index()
        return [result]


if __name__ == "__main__":
    scraper = DefenseRankingsScraper()
    scraper.get_data()
