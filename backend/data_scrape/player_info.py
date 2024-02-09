import pandas as pd

from global_implementations import constants
from helpers.string_helpers import get_player_id_from_name
from data_scrape.abstract_base_scraper import AbstractBaseScraper
from unidecode import unidecode

from sql_app.register.player_info import PlayerInfo
from sql_app.register.player_info import PlayerInfos
from sql_app.register.player_info import Colleges


def get_player_ids(*, source_table: pd.DataFrame, id_from_column: str) -> pd.Series:
    source_table["player_id"] = source_table.apply(
        lambda row: get_player_id_from_name(player_name=row[id_from_column]), axis=1
    )
    duplicate_ids: list[str] = source_table["player_id"].unique()

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

            # Append the unique identifier to the player id to create the unique idS
            source_table.loc[index, "player_id"] = row["player_id"] + unique_identifier
            occurence_value += 1

    return source_table["player_id"]


def decode_player_name(*, source_table: pd.DataFrame, id_from_column: str) -> pd.Series:
    for index, row in source_table.iterrows():
        source_table.loc[index, id_from_column] = unidecode(row[id_from_column])

    return source_table[id_from_column]


def convert_height_to_inches(
    *, source_table: pd.DataFrame, id_from_column: str
) -> pd.Series:
    for index, row in source_table.iterrows():
        feet, inches = row[id_from_column].split("-")
        source_table.loc[index, id_from_column] = int(feet) * 12 + int(inches)

    return source_table[id_from_column]


def convert_colleges_to_list(
    *, source_table: pd.DataFrame, id_from_column: str
) -> pd.Series:
    source_table[id_from_column].loc[source_table[id_from_column].isnull()] = (
        source_table[id_from_column]
        .loc[source_table[id_from_column].isnull()]
        .apply(lambda x: [])
    )
    source_table[id_from_column] = list(
        map(
            lambda colleges: [colleges] if type(colleges) != list else colleges,
            source_table[id_from_column],
        )
    )

    return source_table[id_from_column]


class PlayerInfoScraper(AbstractBaseScraper):
    _exception_msgs: "dict[str:str]" = {
        "load_data": "Unable to load data.",
        "download_data": "Unable to download data.",
    }

    STAT_AUGMENTATIONS = {
        "player_id": lambda dataset: get_player_ids(
            source_table=dataset, id_from_column="name"
        ),
        "name": lambda dataset: decode_player_name(
            source_table=dataset, id_from_column="name"
        ),
        "height": lambda dataset: convert_height_to_inches(
            source_table=dataset, id_from_column="height"
        ),
        # "colleges": lambda dataset: convert_colleges_to_list(source_table=dataset, id_from_column="colleges")
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
        "Colleges": "colleges",
    }
    DROP_COLUMNS: "list[str]" = ["colleges"]
    TABLE: PlayerInfo = PlayerInfos

    def __init__(self, *, last_initial: str):
        super().__init__(player_id=last_initial)

    @property
    def download_url(self) -> str:
        return f"http://www.basketball-reference.com/players/{self.player_id}/"

    def select_dataset_from_html_tables(
        self, *, datasets: "list[pd.DataFrame]"
    ) -> pd.DataFrame:
        return datasets[0]


if __name__ == "__main__":

    # for letter in ascii_lowercase:
    #     player_info: PlayerInfo = PlayerInfo(last_initial=letter)
    #     data: pd.DataFrame = player_info.get_data()

    #     print(data)

    player_info: PlayerInfo = PlayerInfo(last_initial="j")
    data: pd.DataFrame = player_info.download_data()
    print(data)
