# coding: utf-8

import pytest
from datagov.ckan.resource import Directory, Empty, File, Resource, WebPage

# ResourceTypeUpdater


@pytest.mark.parametrize(
    "url, expected",
    [
        (" ", Empty),
        ("", Empty),
        (None, Empty),
        ("https://www.foo.com/foo.01", WebPage),
        ("https://www.foo.com/bar.000001", WebPage),
        ("https://www.foo.com/bar.aspx", WebPage),
        ("https://www.foo.com/bar.htm", WebPage),
        ("https://www.foo.com/bar.html", WebPage),
        ("https://www.foo.com/bar.shtml", WebPage),
        ("https://www.foo.com/bar.htmlx", WebPage),
        ("https://www.foo.com/bar.html#", WebPage),
        ("https://www.foo.com/foobar.02", WebPage),
        ("https://www.foo.com/foobar.02&", WebPage),
        ("https://www.foo.com/foobar.01/", Directory),
        ("https://www.foo.com/foobar.01%2F", Directory),
        ("https://www.foo.com/bar./foo", WebPage),
        ("https://www.foo.com/bar.foo/foo", WebPage),
        ("https://www.foo.com/foobar.01.zip", File),
        ("https://www.foo.com/foobar.01.geojson", File),
        ("https://www.foo.com/foobar.01.geojsonx", WebPage),
        ("https://www.foo.com", WebPage),
        ("https://www.foo.com/", Directory),
        ("https://www.foo.com/bar", WebPage),
        ("https://taz.org/10.1190/tle36121018.1", WebPage),
        ("https://taz.org/10.1190/tle36121018.1010002", WebPage),
        ("https://taz.org%2F10.5067%2FISS%2FSAGEIII%2FLUNAR_BINARY_L2-V6.0", WebPage),
    ],
)
def test_parse_record(url, expected):
    assert isinstance(Resource.get_type_from_url(url), expected)
