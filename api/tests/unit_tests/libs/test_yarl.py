import pytest
from yarl import URL


def test_yarl_urls():
    expected_1 = "//api"
    assert str(URL("/") / "api") == expected_1
    assert str(URL("//") / "api") == expected_1

    expected_2 = "http://orqivium.local:12345/api"
    assert str(URL("http://orqivium.local:12345") / "api") == expected_2
    assert str(URL("http://orqivium.local:12345/") / "api") == expected_2

    expected_3 = "//api/v1"
    assert str(URL("/") / "api" / "v1") == expected_3
    assert str(URL("/") / "api/v1") == expected_3
    assert str(URL("//") / "api/v1") == expected_3
    assert str(URL("//api") / "v1") == expected_3
    assert str(URL("//api/") / "v1") == expected_3

    expected_4 = "api"
    assert str(URL("") / "api") == expected_4

    expected_5 = "/api"
    assert str(URL("/") / "api") == expected_5

    with pytest.raises(ValueError) as e1:
        str(URL("/") / "/api")
    assert str(e1.value) == "Appending path '/api' starting from slash is forbidden"
