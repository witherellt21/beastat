from base.scraper.util.util import camel_to_snake_case


def test_camel_to_snake_case():
    res = camel_to_snake_case("camelCase")

    assert res == "camel_case"
