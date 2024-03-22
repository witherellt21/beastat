import calendar
import datetime
import logging
import re
import string
import uuid
from typing import Optional

import pandas as pd
import requests
from base.scraper import BaseHTMLDatasetConfig, TableConfig
from bs4 import BeautifulSoup, element
from click import Option
from dateutil import parser
from dateutil.tz import gettz
from nbastats.sql_app.register import Games, Lineups, Matchups
from nbastats.sql_app.util.db_helpers import get_player_id

date_regex = r"(?:%s)\s\d\d,\s\d{4}" % "|".join(calendar.month_name)
TZ_INFOS = {"ET": gettz("America/New York"), "EST": gettz("America/New York")}
logger = logging.getLogger("main")


def get_team_lineup(
    *, lineup_div: element.Tag
) -> Optional[dict[str, str | list[dict[str, str | None]]]]:
    """
    Parse the lineup div to get an object containing the lineup information
    """
    # Get all the team player Tags from the lineup div.
    team_players: element.ResultSet[element.Tag] = lineup_div.find_all(
        "li", class_="lineup__player"
    )

    lineup: dict[str, str | list[dict[str, str | None]]] = {"injuries": []}

    player_idx = 0
    for player in team_players:
        if player.div and player.a:
            player_link = player.a["href"]

            if type(player_link) == str:
                player_id = player_link.rsplit("/", 1)[1]
                player_name_component = player_id.rsplit("-", 1)[0]
                player_name_lower = " ".join(player_name_component.split("-"))
                player_name = string.capwords(player_name_lower)
            else:
                player_name = player.a.text.split("\n")[-1]

            if player_idx <= 4:
                player_id = get_player_id(player_name=player_name)

                if not player_id:
                    logger.error(
                        f"Could not get lineup because there was an error getting the player id for {player_name}"
                    )
                    return None

                lineup[f"{player.div.text}_id"] = player_id

            elif "has-injury-status" in player["class"]:
                lineup["injuries"].append(  # type: ignore
                    {
                        "position": player.div.text,
                        "player_name": player_name,
                        "status": player.span.text if player.span else None,
                    }
                )

        player_idx += 1

    return lineup


def get_game_time(*, game_div: element.Tag) -> datetime.time:
    """
    Get the tipoff time for the game.
    """
    game_time_div = game_div.find("div", class_="lineup__time")

    if not game_time_div:
        raise AttributeError("No game time found.")

    return parser.parse(game_time_div.text, tzinfos=TZ_INFOS).time()


def get_team_abbr(*, team_div: element.Tag) -> str:
    home_team_abbr_div = team_div.find("div", class_="lineup__abbr")

    if not home_team_abbr_div:
        raise AttributeError("Could not find home team abbreviation.")

    return home_team_abbr_div.text


class GameTableConfig(TableConfig):
    TRANSFORMATIONS = {
        ("name", "id"): lambda x: uuid.uuid4(),
    }

    def __init__(self, **kwargs):
        super().__init__(
            identification_function=self.identify,
            sql_table=Games,
            **kwargs,
        )

    def identify(self, tables: list[pd.DataFrame]) -> Optional[pd.DataFrame]:
        data = next(
            (table for table in tables if "date_time" in table.columns),
            None,
        )
        return data


class LineupTableConfig(TableConfig):
    TRANSFORMATIONS = {
        ("name", "id"): lambda x: uuid.uuid4(),
    }

    def __init__(self, **kwargs):
        super().__init__(
            identification_function=self.identify,
            sql_table=Lineups,
            **kwargs,
        )

    def identify(self, tables: list[pd.DataFrame]) -> Optional[pd.DataFrame]:
        data = next(
            (table for table in tables if "status" in table.columns),
            None,
        )
        return data


class MatchupTableConfig(TableConfig):
    TRANSFORMATIONS = {
        ("name", "id"): lambda x: uuid.uuid4(),
    }

    def __init__(self, **kwargs):
        super().__init__(
            identification_function=self.identify,
            sql_table=Matchups,
            **kwargs,
        )

    def identify(self, tables: list[pd.DataFrame]) -> Optional[pd.DataFrame]:
        data = next(
            (table for table in tables if "position" in table.columns),
            None,
        )
        return data


class TodaysGamesDatasetConfig(BaseHTMLDatasetConfig):

    def __init__(self, **kwargs):
        super().__init__(default_query_set=None, **kwargs)

    @property
    def base_download_url(self) -> str:
        return "http://www.rotowire.com/basketball/nba-lineups.php"

    def extract_tables(self, *, url: str) -> list[pd.DataFrame]:
        page: requests.Response = requests.get(url)

        soup: BeautifulSoup = BeautifulSoup(page.content, "html.parser")

        # Get the date for the games
        page_title_div = soup.find("div", class_="page-title__secondary")

        if not page_title_div:
            game_date = datetime.datetime.today().date()
        else:
            page_title = page_title_div.text
            matched_dates = re.findall(date_regex, page_title)

            if matched_dates:
                game_date = datetime.datetime.strptime(
                    matched_dates[0], "%B %d, %Y"
                ).date()
            else:
                game_date = datetime.datetime.today().date()

        # Get all the matchup cards
        game_divs: element.ResultSet[element.Tag] = soup.find_all(
            "div", class_="lineup is-nba"
        )

        games = pd.DataFrame()
        lineups = pd.DataFrame()
        matchups = pd.DataFrame()

        # game_entries = []
        for game_div in game_divs:
            if "is-tools" in game_div["class"]:
                continue

            # Get the tipoff time for the game
            try:
                game_time = get_game_time(game_div=game_div)
            except AttributeError as e:
                # self.logger.error(game_div)
                continue

            game_date_time = datetime.datetime.combine(date=game_date, time=game_time)

            # Get the home and away team names (abbreviations)
            home_team_div = game_div.find("a", class_="lineup__team is-home")
            if type(home_team_div) == element.Tag:
                home_team_abbr = get_team_abbr(team_div=home_team_div)
            else:
                # self.logger.debug("Tag for home team not found.")
                continue

            away_team_div = game_div.find("a", class_="lineup__team is-visit")
            if type(away_team_div) == element.Tag:
                away_team_abbr = get_team_abbr(team_div=away_team_div)
            else:
                # self.logger.debug("Tag for away team not found.")
                continue

            # home_team_id = get_team_id_by_abbr(home_team_abbr)
            # away_team_id = get_team_id_by_abbr(away_team_abbr)

            game_entry = {
                "date_time": game_date_time,
                "home_id": home_team_abbr,
                "away_id": away_team_abbr,
            }

            game_line_divs = game_div.findAll("div", class_="lineup__odds-item")

            for game_line_div in game_line_divs:
                label = game_line_div.b.text.strip(" ").lower()

                if "o/u" in label:
                    label = "over_under"

                line = game_line_div.find("span", class_="composite").text

                game_entry[label] = line

            # print(game_entry)
            # print(pd.DataFrame(game_entry, index=[0]))
            games = pd.concat(
                [games, pd.DataFrame(game_entry, index=[0])], ignore_index=True
            )
            # print(games)

            # game: GameSerializer = Games.update_or_insert_record(data=game_entry)  # type: ignore

            # Get the home and away team starting lineups
            home_lineup_div = game_div.find("ul", class_="lineup__list is-home")
            if type(home_lineup_div) == element.Tag:
                lineup_status = home_lineup_div.find("li", class_="lineup_status")
                home_lineup_status = (
                    lineup_status.text if lineup_status else "Expected Lineup"
                )
                home_team_lineup = get_team_lineup(lineup_div=home_lineup_div)

            else:
                continue

            away_lineup_div = game_div.find("ul", class_="lineup__list is-visit")
            if type(away_lineup_div) == element.Tag:
                lineup_status = away_lineup_div.find("li", class_="lineup_status")
                away_lineup_status = (
                    lineup_status.text if lineup_status else "Expected Lineup"
                )
                away_team_lineup = get_team_lineup(lineup_div=away_lineup_div)
                print(away_team_lineup)
            else:
                continue

            # lineups = pd.DataFrame()

            if home_team_lineup:
                home_team_data: dict = {
                    "id": uuid.uuid4(),
                    # "game_id": game.id,
                    "team_id": home_team_abbr,
                    "status": home_lineup_status,
                    **home_team_lineup,
                }

                lineups = pd.concat([lineups, pd.DataFrame(**home_team_data)])

                # Lineups.update_or_insert_record(data=home_team_data)

            if away_team_lineup:
                away_team_data: dict = {
                    "id": uuid.uuid4(),
                    # "game_id": game.id,
                    "team_id": away_team_abbr,
                    "status": away_lineup_status,
                    **away_team_lineup,
                }

                lineups = pd.concat([lineups, pd.DataFrame(**away_team_data)])

                # Lineups.update_or_insert_record(data=away_team_data)

            if not home_team_lineup or not away_team_lineup:
                # return []
                continue

            for position, player_id in home_team_lineup.items():
                if position == "injuries" or type(player_id) != str:
                    continue

                matchup = {
                    "id": uuid.uuid4(),
                    # "game_id": game.id,
                    "position": position.split("_")[0],
                    "home_player_id": player_id,
                    "away_player_id": away_team_lineup[position],
                }

                matchups = pd.concat([matchups, pd.DataFrame(**matchup)])

                # try:
                #     Matchups.update_or_insert_record(data=matchup)
                # except Exception as e:
                #     print("MATCHUP ERROR ", e)

        return [games, lineups, matchups]


# if __name__ == "__main__":
#     scraper = LineupScraper()
#     scraper.extract_tables(url="http://www.rotowire.com/basketball/nba-lineups.php")
