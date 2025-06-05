# coding: utf-8

import pytest
from nocodb.updaters import ResourceTypeUpdater

# ResourceTypeUpdater


@pytest.mark.parametrize(
    "url, expected",
    [
        ("foo.01", {"resource_type": "web"}),
        ("bar.000001", {"resource_type": "web"}),
        ("bar.aspx", {"resource_type": "web"}),
        ("bar.htm", {"resource_type": "web"}),
        ("bar.htm#", {"resource_type": "web"}),
        ("bar.html", {"resource_type": "web"}),
        ("bar.html#", {"resource_type": "web"}),
        ("bar.shtml", {"resource_type": "web"}),
        ("bar.htmlx", {"resource_type": "web"}),
        ("foobar.02", {"resource_type": "web"}),
        ("foobar.02&", {"resource_type": "web"}),
        ("foobar.01/", {"resource_type": "dir"}),
        ("foobar.01%2F", {"resource_type": "dir"}),
        ("bar./foo", {"resource_type": "web"}),
        ("bar.foo/foo", {"resource_type": "web"}),
        ("foobar.01.zip", {"resource_type": "zip"}),
        ("foobar.01.geojson", {"resource_type": "geojson"}),
        ("foobar.01.geojsonx", {"resource_type": "web"}),
        ("https://taz.org/10.1190/tle36121018.1", {"resource_type": "web"}),
        ("https://taz.org/10.1190/tle36121018.1010002", {"resource_type": "web"}),
        (
            "https://taz.org%2F10.5067%2FISS%2FSAGEIII%2FLUNAR_BINARY_L2-V6.0",
            {"resource_type": "web"},
        ),
    ],
)
def test_parse_record(url, expected):
    updater = ResourceTypeUpdater(None)
    assert updater.parse_record({"dg_dataset_id": "foobar", "dg_url": url}) == expected
