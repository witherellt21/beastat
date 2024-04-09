import collections.abc
import datetime
import logging

import numpy as np
import pandas as pd
from fastapi import APIRouter
from nbastats import constants
from nbastats.sql_app.register import BasicInfo, PlayerBoxScores, PlayerProps
from nbastats.sql_app.register.gamelog import GamelogQuery
from nbastats.sql_app.serializers import ReadPlayerPropSerializer
from nbastats.sql_app.util.db_helpers import GamelogFilter, filter_gamelog

logger = logging.getLogger("main")


router = APIRouter()


def update(og, u):
    d = og.copy()
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def get_hitrate(
    player_id, filters: dict, stat, value, over_implied, under_implied
) -> pd.Series:
    """
    Get a players hitrate for a stat.
    """

    over_query = update(
        filters, {"equal_to": {"player_id": player_id}, "greater_than": {stat: value}}
    )

    under_query = update(
        filters, {"equal_to": {"player_id": player_id}, "less_than": {stat: value}}
    )

    over_count = PlayerBoxScores.count_records(query=GamelogQuery(**over_query))
    under_count = PlayerBoxScores.count_records(query=GamelogQuery(**under_query))

    total_count = over_count + under_count

    over_value = (
        over_count / total_count * 100 - over_implied if total_count else np.nan
    )
    under_value = (
        under_count / total_count * 100 - under_implied if total_count else np.nan
    )

    return pd.Series({"over": over_value, "under": under_value})


############################
# ListAllActiveProps
############################


@router.get("/")
def list_all_active_props():
    player_props = PlayerProps.get_all_records(as_df=True)
    player_lines = player_props.groupby("player")
    result = []

    for player_id, lines in player_lines:

        avg_mp = PlayerBoxScores.average_column(player_id, "MP", 10)

        if not avg_mp:
            print(player_id)
            continue

        filters = {
            "greater_than": {
                "MP": avg_mp * 0.8,
                "Date": datetime.datetime(
                    year=constants.CURRENT_SEASON - 1, month=6, day=1
                ),
            },
            "less_than": {"MP": avg_mp * 1.2},
            "equal_to": {"GS": 1},
        }

        lines[["over_value", "under_value"]] = lines.apply(
            lambda row: get_hitrate(
                player_id,
                filters,
                row["stat"],
                row["line"],
                row["over_implied"],
                row["under_implied"],
            ),
            axis=1,
        )

        player_data = (
            lines[["stat", "line", "over_value", "under_value"]]
            .set_index("stat")
            .fillna("")
            .to_dict(orient="index")
        )

        player_info = BasicInfo.get_record(query={"id": player_id})

        if player_info:
            player_data["player"] = player_info.model_dump()
            result.append(player_data)

    return result


############################
# GetPropsByPlayerID
############################


@router.get("/{player_id}")
async def get_props_by_player_id(player_id: str):
    lines: list[ReadPlayerPropSerializer] = PlayerProps.filter_records(query={"player_id": player_id})  # type: ignore

    new_lines = {}
    for line in lines:
        new_lines[line.stat] = {
            "line": line.line,
            "over": line.over,
            "under": line.under,
            "over_implied": line.over_implied,
            "under_implied": line.under_implied,
        }

    return [new_lines]


@router.post("/{player_id}/hitrates")
async def get_player_hitrates(
    player_id: str,
    query: GamelogFilter,
):
    lines: list[ReadPlayerPropSerializer] = PlayerProps.filter_records(query={"player_id": player_id})  # type: ignore

    if not lines:
        print(f"No prop lines for player: {player_id}")
        return {}

    gamelog = filter_gamelog(player_id=player_id, query=query)  # type: ignore

    if gamelog.empty:
        return {}

    res = {
        "PTS": {
            "2024": int,
            "last_20": int,
            "last_10": int,
            "last_5": int,
            "last_3": int,
            "line": float,
            "gamelog": [],
        }
    }

    total_number_of_games = len(gamelog)

    # hitrates = {}
    # for limit in [total_number_of_games, 30, 20, 10, 5, 3]:
    #     hitrates_per_limit = {}

    #     for line in lines:
    #         sublog = gamelog.tail(limit)
    #         stat_overs = sublog[sublog[line.stat] >= line.line]
    #         hitrates_per_limit[line.stat] = round(
    #             len(stat_overs) / len(sublog) * 100, ndigits=2
    #         )
    #     identifier = "all" if limit == total_number_of_games else f"last_{limit}"
    #     hitrates[identifier] = hitrates_per_limit

    hitrates = {}
    for line in lines:
        line_hitrate = {}

        for limit in [total_number_of_games, 30, 20, 10, 5, 3]:
            sublog = gamelog.tail(limit)
            stat_overs = sublog[sublog[line.stat] >= line.line]
            # line_hitrate[
            #     "all" if limit == total_number_of_games else f"last_{limit}"
            # ] = round(len(stat_overs) / len(sublog) * 100, ndigits=2)
            hitrate = round(len(stat_overs) / len(sublog) * 100, ndigits=2)
            average = sublog[line.stat].sum() / len(sublog)
            line_hitrate[
                "all" if limit == total_number_of_games else f"last_{limit}"
            ] = {"hitrate": hitrate, "average": average}

        line_hitrate["line"] = line.line
        # line_hitrate["gamelog"] = [
        #     gamelog[["Date", line.stat]]
        #     .rename(columns={line.stat: "value"})
        #     .to_dict(orient="records")
        # ]
        line_hitrate["gamelog"] = {
            "labels": list(gamelog["Date"].dt.date.values.astype(str)),
            "values": list(gamelog[line.stat].values),
        }
        hitrates[line.stat] = line_hitrate

    return hitrates
