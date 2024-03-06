import numpy as np
import pandas as pd
from sql_app.register.gamelog import Gamelogs
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import Lasso, LinearRegression
from sklearn.model_selection import GridSearchCV


def main():
    gamelog = Gamelogs.filter_records(query={"player": "bookede01"}, as_df=True)
    gamelog = gamelog.drop(["id", "Date", "Age", "Tm", "Opp", "player"], axis=1)

    gamelog["days_rest"] = gamelog["days_rest"].fillna(30)
    gamelog = gamelog.dropna(subset="G")

    gamelog = gamelog.fillna(
        {stat: 0 for stat in ["FG_perc", "TWP_perc", "THP_perc", "FT_perc"]}
    )

    gamelog["result"] = gamelog["result"].replace("W", 1)
    gamelog["result"] = gamelog["result"].replace("L", -1)

    gamelog["home"] = gamelog["home"].replace(False, -1)
    gamelog["home"] = gamelog["home"].replace(True, 1)

    # We can take smaller slices, just want to be 99.9% accurate
    gamelog = gamelog.loc[:70, :]

    X_train, X_test, y_train, y_test = train_test_split(
        gamelog.drop(["PTS"], axis=1),
        gamelog["PTS"],
        test_size=0.4,
    )

    lasso = Lasso(alpha=1)
    lasso.fit(X_train, y_train)
    y_pred = lasso.predict(X_test)
    print(
        cross_val_score(lasso, X=gamelog.drop(["PTS"], axis=1), y=gamelog["PTS"], cv=7)
    )


if __name__ == "__main__":
    res = main()

    print(res)
