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
def test_camel_to_snake_case_illegal_arguments(string, expected):
    res = camel_to_snake_case(string)

    assert res == expected


@pytest.mark.parametrize(
    "string",
    (10, 10.5, object(), dict(), list()),
)
def test_camel_to_snake_case(string):
    with pytest.raises(TypeError) as e:
        res = camel_to_snake_case(string)
