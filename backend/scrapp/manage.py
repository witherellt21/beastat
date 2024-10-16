import configparser
import os
from pathlib import Path
from time import sleep

SCRAPERS_DIR = str(Path(__file__).parent) + os.sep + "scrapers"
APP_EXAMPLE_DIR = "{}/{}".format(Path(__file__).parent, "example")


def create_app(app_name, *, prefix=""):
    import os
    import shutil

    destination = "{}/{}".format(os.getcwd(), app_name)

    if os.path.exists(destination):
        raise Exception(
            "Path {} already exists in the current directory".format(app_name)
        )

    shutil.copytree(APP_EXAMPLE_DIR, destination)

    config = configparser.ConfigParser()
    config["DEFAULT"] = {"API_PREFIX": app_name}

    with open("{}/{}".format(destination, "config.ini"), "w") as configfile:
        config.write(configfile)


if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument("action")
    parser.add_argument("-n", "--name", required=True)
    parser.add_argument("-p", "--prefix", default="")

    args = parser.parse_args()

    if args.action == "createapp":
        create_app(args.name, prefix=args.prefix)
