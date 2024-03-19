import pandas as pd
from new_scraper.base import BaseScraper, DatasetScrapeConfig, Dependency, Inheritance
from new_scraper.configs import (
    CareerStatsTableConfig,
    GamelogScrapeConfig,
    PlayerInfoTableConfig,
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


player_info_scraper = BaseScraper()

player_info_scrape_config = DatasetScrapeConfig(
    config=PlayerInfoTableConfig(),
    dependencies=[],
    inheritances=[
        Inheritance(
            source_name="CareerStats",
            inheritance_function=get_team_id_from_career_stats,
        )
    ],
)

career_stats_scrape_config = DatasetScrapeConfig(
    config=CareerStatsTableConfig(),
    dependencies=[
        Dependency(
            source_name="PlayerInfo",
            query_set_provider=lambda dataset: [
                {"player_last_initial": player_id[0], "player_id": player_id}
                for player_id in dataset.index.values
            ],
        )
    ],
)


gamelog_scrape_config = DatasetScrapeConfig(
    config=GamelogScrapeConfig(),
    dependencies=[
        Dependency(
            source_name="CareerStats",
            query_set_provider=lambda dataset: [
                {
                    "player_last_initial": row["player_id"][0],
                    "player_id": row["player_id"],
                    "year": str(
                        int(
                            row["Season"],
                        )
                    ),
                }
                for index, row in dataset[["player_id", "Season"]].iterrows()
            ],
        )
    ],
)

player_info_scraper.add_dataset("PlayerInfo", player_info_scrape_config)
player_info_scraper.add_dataset("CareerStats", career_stats_scrape_config)
player_info_scraper.add_dataset("Gamelog", gamelog_scrape_config)

player_info_scraper.daemon = True
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
