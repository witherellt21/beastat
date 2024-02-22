import pandas as pd

if __name__ == "__main__":
    datasets = pd.read_html(
        "http://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position",
        displayed_only=False,
    )

    print(datasets)
