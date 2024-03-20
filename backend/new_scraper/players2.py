import logging

import pandas as pd
from new_scraper.base2 import (
    BaseScraper,
    DatasetScrapeConfig,
    Dependency2,
    Inheritance2,
)
from new_scraper.configs import (
    CareerStatsTableConfig,
    CareerStatsTableConfig2,
    GamelogScrapeConfig,
    GamelogTableConfig2,
    PlayerInfoTableConfig,
    PlayerInfoTableConfig2,
)

# IS_SEASON = re.compile(r"^\d{4}")


def get_team_id_from_career_stats(career_stats_data: pd.DataFrame) -> pd.DataFrame:
    career_stats_data = (
        career_stats_data.sort_values("Season").groupby("player_id").tail(1)
    )
    career_stats_data = career_stats_data.rename(columns={"Tm_id": "team_id"})
    data = career_stats_data[["player_id", "team_id"]]
    data = data.set_index("player_id")

    return data


player_info_scraper = BaseScraper(log_level=logging.INFO)

player_table_config = PlayerInfoTableConfig2()
career_stats_table_config = CareerStatsTableConfig2()
gamelogs_table_config = GamelogTableConfig2()

player_info_scrape_config = DatasetScrapeConfig(
    dataset=player_table_config,
    dependencies=[],
    inheritances=[
        Inheritance2(
            source=career_stats_table_config,
            inheritance_function=get_team_id_from_career_stats,
        )
    ],
)

career_stats_scrape_config = DatasetScrapeConfig(
    dataset=career_stats_table_config,
    dependencies=[
        Dependency2(
            source=player_table_config,
            query_set_provider=lambda dataset: [
                {"player_last_initial": player_id[0], "player_id": player_id}
                for player_id in dataset.index.values
            ],
        )
    ],
    inheritances=[],
)

gamelogs_scrape_config = DatasetScrapeConfig(
    dataset=gamelogs_table_config,
    dependencies=[
        Dependency2(
            source=career_stats_table_config,
            query_set_provider=lambda dataset: [
                {
                    "player_last_initial": row["player_id"][0],
                    "player_id": row["player_id"],
                    "year": row["Season"],
                }
                for index, row in dataset[["player_id", "Season"]].iterrows()
            ],
        )
    ],
    inheritances=[],
)


# gamelogs_scrape_config = DatasetScrapeConfig(dataset=GamelogTableConfig2())
# career_stats_scrape_config = DatasetScrapeConfig(dataset=CareerStatsTableConfig2())
# player_info_scrape_config = DatasetScrapeConfig(
#     dataset=PlayerInfoTableConfig2(),
#     inheritances=[
#         Inheritance2(
#             source=career_stats_scrape_config.dataset,
#             inheritance_function=get_team_id_from_career_stats,
#         )
#     ],
# )

player_info_scrape_config.add_nested_dataset(
    dataset_config=career_stats_scrape_config,
    # query_set_provider=lambda dataset: [
    #     {"player_last_initial": player_id[0], "player_id": player_id}
    #     for player_id in dataset.index.values
    # ],
)

career_stats_scrape_config.add_nested_dataset(
    dataset_config=gamelogs_scrape_config,
    # query_set_provider=lambda dataset: [
    #     {
    #         "player_last_initial": row["player_id"][0],
    #         "player_id": row["player_id"],
    #         "year": row["Season"],
    #     }
    #     for index, row in dataset[["player_id", "Season"]].iterrows()
    # ],
)

player_info_scraper.add_dataset("PlayerInfo", player_info_scrape_config)


# from new_scraper.test.main_tester_functions import test_scraper_thread

# test_scraper_thread(scraper=player_info_scraper, timeout=20)

# player_info_scraper.start()

# print(player_info_scraper.datasets)
# career_stats_scrape_config = DatasetScrapeConfig(
#     config=CareerStatsTableConfig(),
#     dependencies=[],
#     inheritances=player_info_inheritances,
# )


# player_info_scraper.add_dataset(PlayerInfoDatasetConfig())


# player_info_scraper.forward_pass()
# player_info_scraper.resolve_backward_dependencies_and_save()
