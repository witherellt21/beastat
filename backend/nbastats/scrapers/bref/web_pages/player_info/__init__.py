from string import ascii_lowercase

NAME = "PlayerInfo"

BASE_DOWNLOAD_URL = "http://www.basketball-reference.com/players/{player_last_initial}/"

CONFIG = {
    "default_query_set": [
        {"player_last_initial": letter} for letter in ascii_lowercase
    ],
}
