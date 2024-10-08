import datetime

import pandas as pd
from sklearn.linear_model import Lasso, LinearRegression
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import (
    LabelEncoder,
    MultiLabelBinarizer,
    OneHotEncoder,
    StandardScaler,
)
from sklearn.tree import DecisionTreeClassifier
from sql_app.tables import Gamelogs, Games
from sql_app.tables.gamelog import GamelogQuery


def get_teammate_played(player_id, date, team):
    # query = GamelogQuery(equal_to={"player_id": player_id, "Date": date, "Tm": team})

    player_game_report = Gamelogs.get_record(
        query={"player_id": player_id, "Date": date, "Tm": team}
    )

    return bool(player_game_report)


def get_teammates_in_game(player_id, date, team):
    df = Gamelogs.filter_records(
        query={"Date": date, "Tm": team}, as_df=True, recurse=False
    )

    df: pd.DataFrame = df[df["player"] != player_id]
    df = df.dropna(subset="G")

    return df["player"].dropna().unique()


def predict_player_prop(player_id: str, stat: str, line: float) -> bool:
    query = GamelogQuery(
        equal_to={"player_id": player_id},
        greater_than={"Date": datetime.datetime(2023, 6, 1)},
    )
    df = Gamelogs.filter_records_advanced(query=query)
    df = df.dropna(subset=["GS"])
    df = df.sort_values("Date")

    df = df[["Date", "Tm", "Opp", "home", "GS", "days_rest", stat]]

    # get_teammates_in_game(player_id, datetime.datetime(2015, 3, 6), "LAL")
    df["lineup"] = df.apply(
        lambda row: get_teammates_in_game(player_id, row["Date"], row["Tm"]), axis=1
    )

    mlb = MultiLabelBinarizer(sparse_output=True)

    df = df.join(
        pd.DataFrame.sparse.from_spmatrix(
            mlb.fit_transform(df.pop("lineup")), index=df.index, columns=mlb.classes_
        )
    )

    df["Date"] = pd.to_datetime(df["Date"])
    df["day"] = df["Date"].dt.day
    df["month"] = df["Date"].dt.month
    df["year"] = df["Date"].dt.year
    df = df.drop("Date", axis=1)

    df["last_game_home"] = df["home"].shift()
    df[stat] = df[stat] > line

    df[["Tm", "Opp"]] = df[["Tm", "Opp"]].apply(
        LabelEncoder().fit_transform  # type: ignore
    )

    df = pd.get_dummies(df, columns=["last_game_home", "days_rest", "Opp"])

    X = df.drop(stat, axis=1).values
    y = df[stat].values

    best_scores = []
    best_params = []

    X = StandardScaler().fit_transform(X, y)

    params = {
        "n_neighbors": range(1, 10),
        "algorithm": ["auto", "ball_tree", "kd_tree", "brute"],
        # "leaf_size": range(1, 30, 5),
        "weights": ["uniform", "distance", None],
    }

    params = {
        "criterion": ["gini", "entropy", "log_loss"],
        "splitter": ["best", "random"],
        "max_features": ["auto", "sqrt", "log2", None],
    }

    for i in range(2, 10):
        kn = DecisionTreeClassifier()
        # kn = KNeighborsClassifier()

        search = GridSearchCV(kn, params, cv=i)
        search.fit(X, y)

        best_scores.append(search.best_score_)
        best_params.append(search.best_params_)

    for score, params, cv in zip(best_scores, best_params, range(2, 10)):
        print(round(score, 2), params, cv)
    # print(df.shape)
    # print(df.isna().sum().sort_values())
    return True


if __name__ == "__main__":
    predict_player_prop("jamesle01", "PTS", 26.5)
    pass
