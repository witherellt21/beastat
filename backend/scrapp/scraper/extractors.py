import pandas as pd


def href_table_extractor(url: str) -> list[pd.DataFrame]:
    """
    Base extractor that extracts links from the html
    """
    tables = pd.read_html(url, extract_links="body")

    for df in tables:
        for column in df.columns:

            # the columns are multi-indexed, append the _link identifier to the end
            # of the last value
            if isinstance(df.columns, pd.MultiIndex):
                link_column = (*column[:-1], f"{column[-1]}_link")

            # the column is singly-indexed
            else:
                link_column = f"{column}_link"

            column_split = df[column].apply(pd.Series)

            if len(column_split.columns) != 2:
                column_split[[1]] = pd.NA

            df[[column, link_column]] = column_split

            if df[link_column].isna().all():
                df.drop(link_column, axis=1, inplace=True)

    return tables
