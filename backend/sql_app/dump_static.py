# from sql_app.register import Teams
import json
import os


def dump_teams():
    print(os.getcwd())
    with open("backend/sql_app/static_data/teams.json", "r") as teams_file:
        team_data = json.load(teams_file)
        print(team_data)


if __name__ == "__main__":
    dump_teams()
