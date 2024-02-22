from data_scrape.abstract_base_scraper import AbstractBaseScraper
from helpers.db_helpers import get_player_id
from sql_app.register.lineup import Lineups
from sql_app.register.matchup import Matchups

import requests
import pandas as pd

from bs4 import BeautifulSoup, element
from typing import Optional
import logging


def get_team_lineup(*, lineup_div: element.Tag) -> dict[str, str]:
    """
    Parse the lineup div to get an object containing the lineup information
    """
    # Get all the team player Tags from the lineup div.
    team_players: element.ResultSet[element.Tag] = lineup_div.find_all(
        "a", "player-popup"
    )

    # Assemble a dict of the players by position
    team_lineup: dict[str, str] = {
        "PG": team_players[0].text,
        "SG": team_players[1].text,
        "SF": team_players[2].text,
        "PF": team_players[3].text,
        "C": team_players[4].text,
        # "Bench": list(map(lambda player_name_div: player_name_div.text, team_players[5:]))
    }
    return team_lineup


class LineupScraper(AbstractBaseScraper):

    TABLE = Lineups
    LOG_LEVEL = logging.WARNING

    @property
    def download_url(self) -> str:
        return "http://rotogrinders.com/lineups/nba"

    def get_query_set(self) -> Optional[list[dict[str, str]]]:
        return None

    def select_dataset_from_html_tables(
        self, *, datasets: list[pd.DataFrame]
    ) -> pd.DataFrame:
        return datasets[0]

    def scrape_data(self, *, url: str) -> Optional[list[pd.DataFrame]]:
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

            if away_team_data:
                Lineups.update_or_insert_record(data=away_team_data)
            else:
                self.logger.warning("No home team lineup data found.")
                continue

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

            if home_team_lineup:
                Lineups.update_or_insert_record(data=home_team_data)
            else:
                self.logger.warning("No home team lineup data found.")
                continue

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
                    "home_player_id": get_player_id(player_name=value),
                    "away_player_id": get_player_id(player_name=away_team_lineup[key]),
                }

                try:
                    Matchups.update_or_insert_record(
                        data=matchup, id_fields=["game_id", "position"]
                    )
                except Exception as e:
                    print("MATCHUP ERROR ", e)

            game_id += 1

        for record in Lineups.get_all_records():
            if record.team not in lineups:  # type: ignore
                Lineups.delete_record(query={"team": record.team})  # type: ignore

        for record in Matchups.get_all_records():
            if record.game_id >= game_id:  # type: ignore
                Matchups.delete_record(query={"id": record.id})  # type: ignore


if __name__ == "__main__":
    scraper = LineupScraper()
    scraper.get_data()
