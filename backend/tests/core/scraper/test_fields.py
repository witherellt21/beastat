import numpy as np
import pytest
from scrapp.scraper.fields import *


@pytest.mark.parametrize(
    "field, dataframe, expected",
    (
        (
            BaseField(int, field_name="key"),
            pd.DataFrame({"key": ["1", "3", "5"]}),
            pd.DataFrame({"key": [1, 3, 5]}),
        ),
        (
            BaseField(int, field_name="key"),
            pd.DataFrame({"key": ["1", "3", "5", None]}),
            pd.DataFrame({"key": [1, 3, 5]}),
        ),
        # (
        #     BaseField(str, null=True, field_name="key"),
        #     pd.DataFrame({"key": [1, 3, 5, None]}),
        #     pd.DataFrame({"key": ["1", "3", "5", np.nan]}),
        # ),
    ),
)
def test_base_field_execute(
    field: BaseField, dataframe: pd.DataFrame, expected: pd.DataFrame
):
    # print(dataframe)
    # print(dataframe.dtypes)

    result = field.execute(dataframe)

    # print(result)
    # print(result.dtypes)

    assert result.equals(expected)
