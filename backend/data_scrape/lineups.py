from data_scrape.abstract_base_scraper import AbstractBaseScraper
from helpers.db_helpers import get_player_id
from sql_app.register.lineup import Lineups
from sql_app.register.matchup import Matchups
from sql_app.register.game import Games
from sql_app.serializers.game import GameSerializer

import requests
import pandas as pd
import datetime
from dateutil import parser

from bs4 import BeautifulSoup, element
from typing import Optional
import logging
import re
import calendar
import uuid
from dateutil.tz import gettz
import string

date_regex = r"(?:%s)\s\d\d,\s\d{4}" % "|".join(calendar.month_name)
TZ_INFOS = {"ET": gettz("America/New York"), "EST": gettz("America/New York")}


def get_team_lineup(
    *, lineup_div: element.Tag
) -> dict[str, str | list[dict[str, str | None]]]:
    """
    Parse the lineup div to get an object containing the lineup information
    """
    # Get all the team player Tags from the lineup div.
    team_players: element.ResultSet[element.Tag] = lineup_div.find_all(
        "li", class_="lineup__player"
    )

    lineup: dict[str, str | list[dict[str, str | None]]] = {"injuries": []}
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

            if "has-injury-status" in player["class"]:
                lineup["injuries"].append(
                    {
                        "position": player.div.text,
                        "player_name": player_name,
                        "status": player.span.text if player.span else None,
                    }
                )
            else:
                lineup[player.div.text] = player_name

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


class LineupScraper(AbstractBaseScraper):

    TABLE = Lineups
    LOG_LEVEL = logging.WARNING

    @property
    def download_url(self) -> str:
        return "http://www.rotowire.com/basketball/nba-lineups.php"

    def get_query_set(self) -> Optional[list[dict[str, str]]]:
        return None

    def select_dataset_from_html_tables(
        self, *, datasets: list[pd.DataFrame]
    ) -> pd.DataFrame:
        return datasets[0]

    def scrape_data(self, *, url: str) -> Optional[list[pd.DataFrame]]:
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
            "div", class_="lineup"
        )

        game_entries = []
        for game_div in game_divs:
            if "is-tools" in game_div["class"]:
                continue

            # Get the tipoff time for the game
            game_time = get_game_time(game_div=game_div)
            game_date_time = datetime.datetime.combine(date=game_date, time=game_time)

            # Get the home and away team names (abbreviations)
            home_team_div = game_div.find("a", class_="lineup__team is-home")
            if type(home_team_div) == element.Tag:
                home_team_abbr = get_team_abbr(team_div=home_team_div)
            else:
                self.logger.debug("Tag for home team not found.")
                continue

            away_team_div = game_div.find("a", class_="lineup__team is-visit")
            if type(away_team_div) == element.Tag:
                away_team_abbr = get_team_abbr(team_div=away_team_div)
            else:
                self.logger.debug("Tag for away team not found.")
                continue

            game_entry = {
                "date_time": game_date_time,
                "home": home_team_abbr,
                "away": away_team_abbr,
            }

            game: GameSerializer = Games.update_or_insert_record(data=game_entry)  # type: ignore

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
            else:
                continue

            home_team_data: dict = {
                "game_id": game.id,
                "team": home_team_abbr,
                "status": home_lineup_status,
                **home_team_lineup,
            }
            away_team_data: dict = {
                "game_id": game.id,
                "team": away_team_abbr,
                "status": away_lineup_status,
                **away_team_lineup,
            }

            home_lineup = Lineups.update_or_insert_record(data=home_team_data)
            away_lineup = Lineups.update_or_insert_record(data=away_team_data)
            # game_entries.append(game_entry)

        # games_df = pd.DataFrame(game_entries)

        # row_dicts = games_df.to_dict(orient="records")
        # for row in row_dicts:
        #     Games.update_or_insert_record(data=row)

    def scrape_data2(self, *, url: str) -> Optional[list[pd.DataFrame]]:
        page: requests.Response = requests.get("http://rotogrinders.com/lineups/nba")

        soup: BeautifulSoup = BeautifulSoup(page.content, "html.parser")

        # Get all the matchup cards
        matchup_divs: element.ResultSet[element.Tag] = soup.find_all(
            "div", class_="blk crd lineup"
        )

        # Initialize a dataframe to contain all of the matchups lineup info for the day
        # lineups: pd.DataFrame = pd.DataFrame(columns=["game_id", "team", "opp", "home", "confirmed", "PG","SG","SF","PF","C","Bench"])
        lineups = []

        game_id: int = 0
        for matchup_div in matchup_divs:

            # Get the home and away team abbreviations
            away_team_span, home_team_span = matchup_div.find_all("span", class_="shrt")
            away_team_name: str = away_team_span.text
            home_team_name: str = home_team_span.text

            lineups.append(away_team_name)
            lineups.append(home_team_name)

            # Get the divs containing the lineup info for the home and away teams
            away_team_lineup_div = matchup_div.find("div", class_="blk away-team")
            home_team_lineup_div = matchup_div.find("div", class_="blk home-team")

            if not isinstance(away_team_lineup_div, element.Tag) or not isinstance(
                home_team_lineup_div, element.Tag
            ):
                self.logger.warning("Could not find team lineups.")
                continue

            # Get confirmation statuses
            # away_team_lineup_confirmed: bool = not bool(away_team_lineup_div.find("div", "show-unconfirmed-message"))
            # home_team_lineup_confirmed: bool = not bool(home_team_lineup_div.find("div", "show-unconfirmed-message"))
            away_team_lineup_confirmed: bool = not bool(
                away_team_lineup_div.find("div", class_="lineup__status is-confirmed")
            )
            home_team_lineup_confirmed: bool = not bool(
                home_team_lineup_div.find("div", class_="lineup__status is-confirmed")
            )

            # Append the matchup lineups to the list of matchups
            away_team_data: dict = {
                "game_id": game_id,
                "team": away_team_name,
                "opp": home_team_name,
                "home": False,
                "confirmed": away_team_lineup_confirmed,
            }
            away_team_lineup = get_team_lineup(lineup_div=away_team_lineup_div)
            away_team_data.update(away_team_lineup)

            # if away_team_data:
            #     Lineups.update_or_insert_record(data=away_team_data)
            # else:
            #     self.logger.warning("No home team lineup data found.")
            #     continue

            # Repeat for the home team
            home_team_data: dict = {
                "game_id": game_id,
                "team": home_team_name,
                "opp": away_team_name,
                "home": True,
                "confirmed": home_team_lineup_confirmed,
            }
            home_team_lineup = get_team_lineup(lineup_div=home_team_lineup_div)
            home_team_data.update(home_team_lineup)

            # if home_team_lineup:
            #     Lineups.update_or_insert_record(data=home_team_data)
            # else:
            #     self.logger.warning("No home team lineup data found.")
            #     continue

            for key, value in home_team_lineup.items():
                home_player_id = get_player_id(player_name=value)
                away_player_id = get_player_id(player_name=away_team_lineup[key])

                if not home_player_id or not away_player_id:
                    continue

                matchup = {
                    "game_id": game_id,
                    "position": key,
                    "home_player": value,
                    "away_player": away_team_lineup[key],
                    "home_player_id": home_player_id,
                    "away_player_id": away_player_id,
                }

                # try:
                #     Matchups.update_or_insert_record(
                #         data=matchup, id_fields=["game_id", "position"]
                #     )
                # except Exception as e:
                #     print("MATCHUP ERROR ", e)

            game_id += 1

        for record in Lineups.get_all_records():
            if record.team not in lineups:  # type: ignore
                Lineups.delete_record(query={"team": record.team})  # type: ignore

        for record in Matchups.get_all_records():
            if record.game_id >= game_id:  # type: ignore
                Matchups.delete_record(query={"id": record.id})  # type: ignore


if __name__ == "__main__":
    scraper = LineupScraper()
    scraper.scrape_data(url="http://www.rotowire.com/basketball/nba-lineups.php")
