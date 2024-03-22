import config
from scraper import player_info_scraper, todays_games_scraper

# TODO: MASSIVE work needs to be done in keeping these scrapers asynchronous in case data is missing
if config.DATA_SCRAPE.get("Player", {}).get("status"):

    player_info_scraper.daemon = True
    player_info_scraper.configure(nested_download=True)
    player_info_scraper.start()

if config.DATA_SCRAPE.get("TodaysGames", {}).get("status"):

    todays_games_scraper.daemon = True
    todays_games_scraper.configure()
    todays_games_scraper.start()


from webapp.main import app

# if config.DATA_SCRAPE.get("Lineups", {}).get("status"):
#     lineup_scraper = LineupScraper()
#     lineup_scraper.setDaemon(True)
#     lineup_scraper.start()

# if config.DATA_SCRAPE.get("CareerStats", {}).get("status"):
#     career_stats_scraper = CareerStatsScraper(
#         **config.DATA_SCRAPE.get("CareerStats", {}).get("options", {})
#     )
#     career_stats_scraper.setDaemon(True)
#     career_stats_scraper.start()

# if config.DATA_SCRAPE.get("PlayerProps", {}).get("status"):
#     player_props_scraper = PlayerPropsScraper()
#     player_props_scraper.setDaemon(True)
#     player_props_scraper.start()

# if config.DATA_SCRAPE.get("DefenseRankings", {}).get("status"):
#     defense_rankings_scraper = DefenseRankingsScraper()
#     defense_rankings_scraper.setDaemon(True)
#     defense_rankings_scraper.start()

# if config.DATA_SCRAPE.get("Gamelogs", {}).get("status"):
#     gamelog_scraper = GamelogScraper(
#         **config.DATA_SCRAPE.get("Gamelogs", {}).get("options", {})
#     )
#     gamelog_scraper.setDaemon(True)
#     gamelog_scraper.start()
