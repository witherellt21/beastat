import pandas as pd

from global_implementations import constants
from helpers.string_helpers import get_player_id_from_name
from data_scrape.abstract_base_scraper import AbstractBaseScraper
from data_scrape.test.main_tester_functions import test_scraper_thread
from unidecode import unidecode
import logging

from sql_app.register.player_info import PlayerInfos
from sql_app.register.player_info import Players
from string import ascii_lowercase

from typing import Optional
import requests
from bs4 import BeautifulSoup, element, ResultSet


def get_player_ids(*, source_table: pd.DataFrame, id_from_column: str) -> pd.Series:
    source_table["player_id"] = source_table.apply(
        lambda row: get_player_id_from_name(player_name=row[id_from_column]), axis=1
    )
    duplicate_ids: list[str] = list(source_table["player_id"].unique())

    # For each player id, we will have to append the necessary duplicate value
    for id in duplicate_ids:
        id_rows: pd.DataFrame = source_table[
            source_table["player_id"] == id
        ].sort_values("active_from")

        occurence_value = 1
        for index, row in id_rows.iterrows():
            # Add a leading zeros for duplicates under 10
            unique_identifier: str = (
                f"0{occurence_value}" if occurence_value < 10 else str(occurence_value)
            )

            # Append the unique identifier to the player id to create the unique id
            source_table.loc[index, "player_id"] = row["player_id"] + unique_identifier  # type: ignore
            occurence_value += 1

    return source_table["player_id"]


def convert_height_to_inches(*, height: str) -> int:
    feet, inches = height.split("-")
    return int(feet) * 12 + int(inches)


class PlayerInfoScraper(AbstractBaseScraper):
    class Constants:
        QUERY_SET = [{"player_last_initial": letter} for letter in ascii_lowercase]

    # TODO: Lets see if we can speed up how a lot of the post download logic is done
    # STAT_AUGMENTATIONS = {
    #     "player_id": lambda dataset: get_player_ids(
    #         source_table=dataset, id_from_column="name"
    #     )
    # }
    TRANSFORMATIONS = {
        "name": lambda name: unidecode(name),
        "height": lambda height: convert_height_to_inches(height=height),
        ("player_link", "id"): lambda link: link.rsplit("/", 1)[1].split(".")[0],
    }

    FILTERS = [lambda dataframe: dataframe["active_to"] == constants.CURRENT_SEASON]
    DATETIME_COLUMNS = {"birth_date": "%B %d, %Y"}
    RENAME_COLUMNS = {
        "Player": "name",
        "From": "active_from",
        "To": "active_to",
        "Pos": "position",
        "Ht": "height",
        "Wt": "weight",
        "Birth Date": "birth_date",
    }
    # RENAME_VALUES = {"": "0"}
    HREF_SAVE_MAP = {"Player": "player_link"}

    TABLE = Players
    LOG_LEVEL = logging.WARNING

    @property
    def download_url(self) -> str:
        return "http://www.basketball-reference.com/players/{player_last_initial}/"

    def get_query_set(self) -> Optional[list[dict[str, str]]]:
        return self.Constants.QUERY_SET

    def select_dataset_from_html_tables(
        self, *, datasets: "list[pd.DataFrame]"
    ) -> pd.DataFrame:
        return datasets[0]

    def scrape_data(self, *, url: str) -> list[pd.DataFrame] | None:
        try:
            datasets: list[pd.DataFrame] = pd.read_html(url, extract_links="body")
        except ValueError as e:
            self.logger.warning(f"{e} at url: {url}")
            return None

        return datasets

    def configure_data(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data["Wt"] = data["Wt"].replace("", 0)
        return super().configure_data(data=data)


if __name__ == "__main__":

    # for letter in ascii_lowercase:
    #     player_info: PlayerInfo = PlayerInfo(last_initial=letter)
    #     data: pd.DataFrame = player_info.get_data()

    #     print(data)

    player_info_scraper: PlayerInfoScraper = PlayerInfoScraper()
    player_info_scraper.get_data(query={"player_last_initial": "a"})
    # test_scraper_thread(scraper_class=PlayerInfoScraper)
