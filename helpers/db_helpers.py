
import pandas as pd
from global_implementations import constants
from helpers.string_helpers import find_closest_match
from sql_app.register.lineup import Lineups
from sql_app.register.player_info import PlayerInfos
from sql_app.serializers.player_info import PlayerInfoSerializer


def get_matchups() -> list[tuple[str, str]]:
    current_lineups = Lineups.get_all_records()
        # print(current_lineups)

    lineup_data = pd.DataFrame(current_lineups)
    
    # Merge the lineups for each game to get the opposing teams lineup
    lineups_matchups: pd.DataFrame = lineup_data.merge(lineup_data, left_on=["game_id", "team"], right_on=["game_id", "opp"]).drop(labels=[
        "team_x", "opp_x", "home_x", "confirmed_x", "Bench_x", "team_y", "opp_y", "home_y", "confirmed_y", "Bench_y"
    ], axis="columns").drop_duplicates(subset="game_id")

    matchups: list = []
    for index, row in lineups_matchups.iterrows():
        matchups.extend(list(map(lambda position: (row[f"{position}_x"], row[f"{position}_y"]), constants.BASKETBALL_POSITIONS)))

    return matchups

def get_player_id(*, player_name: str):
    player: PlayerInfoSerializer = PlayerInfos.get_record(id=player_name, id_field="name")

    if not player:
        player_names: list[str] = PlayerInfos.get_column_values(column="name")
        player_name_match: str = find_closest_match(value=player_name, search_list=player_names)
        player: PlayerInfoSerializer = PlayerInfos.get_record(id=player_name_match, id_field="name")

    return player.player_id


if __name__ == "__main__":
    get_player_id(player_name="Luka Doncic")