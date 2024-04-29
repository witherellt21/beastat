import pytest
from lib.util import camel_to_snake_case


@pytest.mark.parametrize(
    "string, expected",
    (
        ("camelCase", "camel_case"),
        ("snake_case", "snake_case"),
        ("ALLCAPS", "a_l_l_c_a_p_s"),
        ("ThisCamel", "this_camel"),
        ("_something", "_something"),
        ("something_", "something_"),
    ),
)
def test_camel_to_snake_case(string, expected):
    res = camel_to_snake_case(string)

    assert res == expected


@pytest.mark.parametrize(
    "string",
    (10, 10.5, object(), dict(), list()),
)
def test_camel_to_snake_case_illegal_arguments(string):
    with pytest.raises(TypeError) as e:
        res = camel_to_snake_case(string)


# @pytest.mark.parametrize(
#     "dataframe, column_order, expected",
#     (
#         (
#             pd.DataFrame({"PTS": [1, 2, 3], "REB": [5, 3, 4], "COL": [None, 2, ""]}),
#             ["COL", "REB"],
#             pd.DataFrame({"COL": [None, 2, ""], "REB": [5, 3, 4], "PTS": [1, 2, 3]}),
#         ),
#         (
#             pd.DataFrame({"PTS": [1, 2, 3], "REB": [5, 3, 4], "COL": [None, 2, ""]}),
#             ["COL", "COL"],
#             pd.DataFrame({"COL": [None, 2, ""], "PTS": [1, 2, 3], "REB": [5, 3, 4]}),
#         ),
#         (
#             pd.DataFrame({"PTS": [1, 2, 3], "REB": [5, 3, 4], "COL": [None, 2, ""]}),
#             ["COL", "PTS", "COL"],
#             pd.DataFrame({"COL": [None, 2, ""], "PTS": [1, 2, 3], "REB": [5, 3, 4]}),
#         ),
#     ),
# )
# def test_reorder_columns(
#     dataframe: pd.DataFrame, column_order: list[str], expected: pd.DataFrame
# ):
#     reordered = reorder_columns(dataframe, column_order)

#     assert reordered.equals(expected)


# @pytest.mark.parametrize(
#     "dataframe, column_order",
#     (
#         (
#             pd.DataFrame({"PTS": [1, 2, 3], "REB": [5, 3, 4], "COL": [None, 2, ""]}),
#             ["COL", "DNE"],
#         ),
#         (
#             pd.DataFrame({"PTS": [1, 2, 3], "REB": [5, 3, 4], "COL": [None, 2, ""]}),
#             ["COL", 1],
#         ),
#     ),
# )
# def test_reorder_columns_raises_value_error(
#     dataframe: pd.DataFrame, column_order: list[str]
# ):
#     with pytest.raises(ValueError) as error:
#         reorder_columns(dataframe, column_order)
