import requests
from bs4 import BeautifulSoup
from bs4 import element
from requests.models import Response

from sql_app.register.lineup import Lineups
from sql_app.register.matchup import Matchups
import threading
import time

from helpers.db_helpers import get_matchups
from helpers.db_helpers import get_player_id


RUNNING = True


def get_team_lineup(*, lineup_div: element.ResultSet) -> dict:
    """
    Parse the lineup div to get an object containing the lineup information
    """
    team_players: element.ResultSet = lineup_div.find_all("a", "player-popup")
    team_lineup: dict[str : str | "list[str]"] = {
        "PG": team_players[0].text,
        "SG": team_players[1].text,
        "SF": team_players[2].text,
        "PF": team_players[3].text,
        "C": team_players[4].text,
        # "Bench": list(map(lambda player_name_div: player_name_div.text, team_players[5:]))
    }
    return team_lineup


def get_lineups() -> None:
    # Get the raw html for today's lineups and create a bs4 parser
    page: Response = requests.get("http://rotogrinders.com/lineups/nba")
    soup: BeautifulSoup = BeautifulSoup(page.content, "html.parser")

    # Get all the matchup cards
    matchup_divs: element.ResultSet = soup.find_all("div", class_="blk crd lineup")

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
        away_team_lineup_div: element.Tag = matchup_div.find("div", "blk away-team")
        home_team_lineup_div: element.Tag = matchup_div.find("div", "blk home-team")

        # Get confirmation statuses
        # away_team_lineup_confirmed: bool = not bool(away_team_lineup_div.find("div", "show-unconfirmed-message"))
        # home_team_lineup_confirmed: bool = not bool(home_team_lineup_div.find("div", "show-unconfirmed-message"))
        away_team_lineup_confirmed: bool = not bool(
            away_team_lineup_div.find("div", "lineup__status is-confirmed")
        )
        home_team_lineup_confirmed: bool = not bool(
            home_team_lineup_div.find("div", "lineup__status is-confirmed")
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
        # lineups.loc[len(lineups)]: pd.Series = away_team_data
        Lineups.update_or_insert_record(data=away_team_data)

        home_team_data: dict = {
            "game_id": game_id,
            "team": home_team_name,
            "opp": away_team_name,
            "home": True,
            "confirmed": home_team_lineup_confirmed,
        }
        home_team_lineup = get_team_lineup(lineup_div=home_team_lineup_div)
        home_team_data.update(home_team_lineup)
        # lineups.loc[len(lineups)]: pd.Series = home_team_data
        Lineups.update_or_insert_record(data=home_team_data)

        for key, value in home_team_lineup.items():
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
        if record.team not in lineups:
            Lineups.delete_record(query={"team": record.team})

    for record in Matchups.get_all_records():
        if record.game_id >= game_id:
            Matchups.delete_record(query={"id": record.id})


class LineupDataScraper(threading.Thread):
    def __init__(self) -> None:
        self.RUNNING: bool = True
        super().__init__()

    def run(self) -> None:
        while self.RUNNING:
            get_lineups()

            time.sleep(1)


if __name__ == "__main__":
    lineups = get_lineups()
    print(lineups)