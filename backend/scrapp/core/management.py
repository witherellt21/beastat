import argparse
import os
from time import sleep
from typing import Optional

import scrapp
from scrapp.utils.file_management import enforce_file_type, find_file


def loaddata(file_name: str, extension: str = "json"):
    """
    Load fixture by file name.
    """
    from scrapp.tables.fixtures.util import load_fixture

    file_name = enforce_file_type(file_name, extension)
    file_path = find_file(file_name=file_name, path=".")

    if not file_path:
        raise Exception("Fixture '{}' does not exist.".format(file_name))

    return load_fixture(file_path=file_path)


def runScrapers(apps: list[str]):
    from scrapp.scraper import ScraperManager

    for app in apps:
        ScraperManager.get_instance(app).run()

    running = True
    while running:
        sleep(1)

    for app in apps:
        ScraperManager.get_instance(app).kill()


class ManagementUtility:

    def __init__(self):

        self.parser = argparse.ArgumentParser(
            description="This program allows you to manage resources within a scraper app.",
        )

        subparsers = self.parser.add_subparsers(dest="command", required=True)

        load_parser = subparsers.add_parser("loaddata")

        load_parser.add_argument(
            "file_name", type=str, help="Name of fixture file. File must be valid json."
        )

        dump_parser = subparsers.add_parser("dumpdata")
        dump_parser.add_argument(
            "file_name",
            type=str,
            help="Name of fixture file to dump data to.",
        )

        scrape_parser = subparsers.add_parser("runscrapers")
        scrape_parser.add_argument(
            "apps",
            type=str,
            help="Name of app to start scraping on.",
            nargs="*",
        )

    def execute(self):
        args = self.parser.parse_args()

        scrapp.setup()

        if args.command == "loaddata":
            loaddata(args.file_name)

        if args.command == "runscrapers":
            from scrapp.apps import apps

            # Get the app config objects
            # If no list specified run all apps
            app_list = [
                apps.get_app_config(app_name) for app_name in args.apps
            ] or apps.get_app_configs()

            # Import the scrapers to add them to the registry
            for app_config in app_list:
                app_config.import_scrapers()

            runScrapers([app_config.name for app_config in app_list])


command_line_manager = ManagementUtility()


def execute_from_command_line():
    command_line_manager.execute()
