import datetime
import math
from typing import Optional
import numpy as np
import pandas as pd
from sql_app.register.gamelog import Gamelogs, GamelogQuery
from sql_app.register.player_info import Players
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import Lasso, LinearRegression
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeClassifier

# import matplotlib.pyplot as plt


"""
Basic idea:
- Create a one-hot encoding of all players in DB
- Create a one-hot encoding of all teams in DB
- Do something with the date
- Include starting status, days rest, age
- Train and test

"""


def predict_result():
    def get_closest_game(date, data: pd.DataFrame) -> Optional[int]:
        # Get the closest last game the player played in
        date_differences: pd.Series[datetime.timedelta] = (
            date - data[data["Date"] < date]["Date"]
        )

        sorted_dates = date_differences.sort_values()

        if not sorted_dates.empty:
            return sorted_dates.iloc[0].days
        else:
            return None

    start = datetime.datetime(year=2023, month=6, day=1)
    games = Gamelogs.filter_records_advanced(
        query=GamelogQuery(**{"greater_than": {"Date": start}}),  # type: ignore
        confuse=True,
        limit=100,
    )

    games = games[["Date", "Tm", "Opp", "result"]]
    games = games.drop_duplicates(subset=["Date", "Tm"])

    # games = games.sort_values("Date")
    for idx, row in games.iterrows():
        team_games = games[games["Tm"] == row["Tm"]]
        # games.loc[idx, :] = team_games[-1]
        games.loc[idx, "days_rest"] = get_closest_game(  # type:ignore
            row["Date"], team_games
        )

    print(games)

    games["days_rest"] = games["Date"].apply(lambda date: get_closest_game(date, games))

    games["Date"] = pd.to_datetime(games["Date"])
    games["day"] = games["Date"].dt.day
    games["month"] = games["Date"].dt.month
    games["year"] = games["Date"].dt.year
    games = games.drop("Date", axis=1)

    # Transform data into
    games[["Tm", "Opp", "result"]] = games[["Tm", "Opp", "result"]].apply(
        LabelEncoder().fit_transform  # type: ignore
    )  # type: ignore

    X = games.drop(["result"], axis=1)
    y = games["result"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)

    print(f"X_train: {X_train.shape}")
    print(f"X_train: {y_train.shape}")
    print(f"X_train: {X_test.shape}")
    print(f"X_train: {y_test.shape}")

    # cv_score = cross_val_score(DecisionTreeClassifier(), X, y, cv=4)
    # print(cv_score)

    lasso = DecisionTreeClassifier(random_state=14)
    # grid = GridSearchCV(lasso, params, scoring="explained_variance")
    # grid.fit(X, y)
    # scores = cross_val_score(lasso, X, y, scoring="f1_weighted")
    lasso.fit(X_train, y_train)
    y_pred = lasso.predict(X_test)
    score = lasso.score(X_test, y_test)

    print(f"Prediction accuracy: {score}")

    result = X_test.copy()

    result["result_pred"] = y_pred.round(2)
    result["result_actual"] = y_test


def predict_margin():

    start = datetime.datetime(year=2023, month=6, day=1)
    games = Gamelogs.filter_records_advanced(
        query=GamelogQuery(**{"greater_than": {"Date": start}}),  # type: ignore
        confuse=True,
        columns=["Date", "Tm", "Opp", "margin"],
    )
    # print(games)
    games = games[["Date", "Tm", "Opp", "margin"]]

    games["Date"] = pd.to_datetime(games["Date"])
    games["day"] = games["Date"].dt.day
    games["month"] = games["Date"].dt.month
    games["year"] = games["Date"].dt.year
    games = games.drop("Date", axis=1)

    # Transform data into
    games[["Tm", "Opp"]] = games[["Tm", "Opp"]].apply(
        LabelEncoder().fit_transform  # type: ignore
    )  # type: ignore

    X = games.drop(["margin"], axis=1)
    y = games["margin"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)

    print(f"X_train: {X_train.shape}")
    print(f"X_train: {y_train.shape}")
    print(f"X_train: {X_test.shape}")
    print(f"X_train: {y_test.shape}")

    # cv_score = cross_val_score(DecisionTreeClassifier(), X, y, cv=4)
    # print(cv_score)

    # lasso = DecisionTreeClassifier(random_state=14)
    le = LinearRegression()
    # grid = GridSearchCV(lasso, params, scoring="explained_variance")
    # grid.fit(X, y)
    # scores = cross_val_score(lasso, X, y, scoring="f1_weighted")
    le.fit(X_train, y_train)
    y_pred = le.predict(X_test)
    score = le.score(X_test, y_test)

    print(f"Prediction accuracy: {score}")

    result = X_test.copy()

    result["margin_pred"] = y_pred.round(2)
    result["margin_actual"] = y_test

    print(result)


def predict_outcomes():
    games = Gamelogs.get_all_records(as_df=True, confuse=True, limit=10000)

    games = games[["Date", "Tm", "Opp", "margin"]]

    # Replace team names with new org name
    games = games.replace("NOK", "NOP")
    games = games.replace("NOH", "NOP")
    games = games.replace("CHA", "CHO")
    games = games.replace("SEA", "OKC")
    games = games.replace("NJN", "BRK")

    le = LabelEncoder()
    le.fit(games["Tm"])

    # use the same encoding for both home and away teams
    games["Tm"] = le.transform(games[["Tm"]].values)
    games["Opp"] = le.transform(games[["Opp"]].values)

    # one-hot encode the data for team/opponent
    games = pd.get_dummies(games, columns=["Tm", "Opp"], dtype=int)

    # return predict_result()

    # Transform the date column for use in the model
    games["Date"] = pd.to_datetime(games["Date"])
    games["day"] = games["Date"].dt.day
    games["month"] = games["Date"].dt.month
    games["year"] = games["Date"].dt.year
    games = games.drop("Date", axis=1)

    X = games.drop("margin", axis=1).values
    y = games["margin"].values

    print(games.drop("margin", axis=1))
    X_train, X_test, y_train, y_test = train_test_split(
        games.drop("margin", axis=1),
        games["margin"],
        test_size=0.4,
    )

    # tree = DecisionTreeClassifier(random_state=14)
    # tree.fit(X_train, y_train)
    # y_pred = tree.predict(X_test)

    # reconstruct the dataset
    result = X_test.copy()

    # result["player"] = result["player"].apply(
    #     lambda pid: players.loc[players["pid"] == pid, "player"].iloc[0]
    # )
    result["margin_pred"] = y_pred.round(2)
    result["margin_actual"] = y_test

    print(result)


def main():

    # Map all player id's to a categorical value
    players = Players.get_all_records(as_df=True)
    players["pid"] = players["id"].astype("category").cat.codes
    players = players.rename(columns={"id": "player"})

    # Obtain a random sample of gamelogs
    gamelog = Gamelogs.get_all_records(as_df=True, confuse=True, limit=100000)

    # Replace player id's with their categorical match
    gamelog = pd.merge(gamelog, players[["player", "pid"]], on="player")
    gamelog["player"] = gamelog["pid"]
    gamelog = gamelog.drop("pid", axis=1)

    gamelog["Age"] = gamelog["Age"].apply(
        lambda age: int(age.split("-")[0]) * 365 + int(age.split("-")[1])
    )

    # print(len(gamelog))

    # print(gamelog)

    # Encode the team column with integer mappings
    # le = LabelEncoder()
    # # df1 = gamelog[["Tm"]]
    # gamelog["Team"] = le.fit_transform(gamelog["Tm"])
    # gamelog["Opp"] = le.fit_transform(gamelog["Opp"])

    # Converts Tm and Opp columns to integer categories
    gamelog[["Tm", "Opp"]] = pd.DataFrame(
        {
            col: gamelog[col].astype("category").cat.codes
            for col in gamelog[["Tm", "Opp"]]
        },
        index=gamelog.index,
    )

    # for games not played, fill all stats with 0
    mask = gamelog["G"].isna()
    gamelog["active"] = (~mask).astype(int)
    gamelog.loc[mask, :] = gamelog.loc[mask, :].fillna(0)

    # print(gamelog)
    # return

    # gamelog = gamelog.drop(["id", "Date", "Age", "Tm", "Opp", "player"], axis=1)
    # drop non-feature columns
    gamelog = gamelog.drop(["id"], axis=1)

    # For uncalculated days_rest, fill with 10 to signify a full rest
    gamelog["days_rest"] = gamelog["days_rest"].fillna(30)
    gamelog = gamelog.dropna(subset="G")

    gamelog = gamelog.fillna(
        {stat: 0 for stat in ["FG_perc", "TWP_perc", "THP_perc", "FT_perc"]}
    )

    gamelog = gamelog[
        ["player", "active", "G", "Age", "Tm", "Opp", "home", "GS", "days_rest", "PTS"]
    ]

    # gamelog["result"] = gamelog["result"].replace("W", 1)
    # gamelog["result"] = gamelog["result"].replace("L", -1)

    gamelog["home"] = gamelog["home"].replace(False, -1)
    gamelog["home"] = gamelog["home"].replace(True, 1)

    X = gamelog.drop(["PTS"], axis=1).values
    y = gamelog["PTS"].values

    pipe = make_pipeline(StandardScaler(), Lasso(alpha=1))
    # lasso = Lasso(alpha=1)

    # best_score = 0
    # best_folds = 0
    # avg_scores = []
    # for n_folds in range(2, 15):
    # kfolds = StratifiedKFold(n_splits=3)
    # scores = []

    X_train, X_test, y_train, y_test = train_test_split(
        gamelog.drop(["PTS"], axis=1),
        gamelog["PTS"],
        test_size=0.4,
    )

    # for train_index, test_index in kfolds.split(X, y):
    # X_train, X_test = X[train_index], X[test_index]
    # y_train, y_test = y[train_index], y[test_index]

    pipe.fit(X_train, y_train)
    score = pipe.score(X_test, y_test)

    print(score)

    return

    # # Create a new dataset for tests.
    X_train, X_test, y_train, y_test = train_test_split(
        gamelog.drop(["PTS"], axis=1),
        gamelog["PTS"],
        test_size=0.4,
    )

    y_pred = pipe.predict(X_test)

    # reconstruct the dataset
    result = X_test.copy()

    result["player"] = result["player"].apply(
        lambda pid: players.loc[players["pid"] == pid, "player"].iloc[0]
    )
    result["PTS_pred"] = y_pred.round(2)
    result["PTS_actual"] = y_test

    print(result)


if __name__ == "__main__":
    # res = main()
    # res = predict_outcomes()
    res = predict_result()

    print(res)
