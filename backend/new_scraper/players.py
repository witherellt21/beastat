from collections.abc import Callable
from new_scraper.base import BaseHTMLDatasetConfig, BaseScraper, TableConfig
from sql_app.register.base import BaseTable
from sql_app.register import Players
import pandas as pd
from string import ascii_lowercase
from unidecode import unidecode
from global_implementations import constants


def has_season_column(dataset: pd.DataFrame) -> bool:
    return True


def convert_height_to_inches(*, height: str) -> int:
    feet, inches = height.split("-")
    return int(feet) * 12 + int(inches)


class PlayerInfoTableConfig(TableConfig):
    """
    Here we will include the cleaning function stuff as class attributes
    """

    # TODO: Lets see if we can speed up how a lot of the post download logic is done
    TRANSFORMATIONS = {
        "name": lambda name: unidecode(name),
        "height": lambda height: convert_height_to_inches(height=height),
        ("player_link", "id"): lambda link: link.rsplit("/", 1)[1].split(".")[0],
        ("name", "team_id"): lambda row: None,
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
    # RENAME_VALUES = {"weight": {"": 0}}
    HREF_SAVE_MAP = {"Player": "player_link"}

    # TABLE = Players
    # LOG_LEVEL = logging.WARNING

    def __init__(self):
        super().__init__(identification_function=has_season_column, sql_table=Players)


class PlayerInfoDatasetConfig(BaseHTMLDatasetConfig):
    def __init__(self):
        table_configs: list[TableConfig] = [PlayerInfoTableConfig()]
        super().__init__(
            table_configs=table_configs,
            query_set=[{"player_last_initial": letter} for letter in ascii_lowercase],
        )

    @property
    def base_download_url(self):
        return "http://www.basketball-reference.com/players/{player_last_initial}/"


player_info_scraper = BaseScraper()
# player_info_scraper.add_dataset(PlayerInfoDatasetConfig())
# player_info_scraper.daemon = True
# player_info_scraper.start()
player_info_scraper.download_and_process_data(
    config=PlayerInfoDatasetConfig(), query_args={"player_last_initial": "a"}
)
