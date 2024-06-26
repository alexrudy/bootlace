from typing import Any

import pytest
from dominate import tags

from bootlace.util import as_tag
from bootlace.util import Tag


class Taggable:
    def __tag__(self) -> tags.html_tag:
        return tags.div()


@pytest.mark.parametrize(
    "tag,expected",
    [
        (tags.div(), "<div></div>"),
        (Taggable(), "<div></div>"),
        ("test", "test"),
        (["test", "test2"], "testtest2"),
        (["test", tags.div()], "test\n<div></div>\n"),
    ],
    ids=["tag", "taggable", "str", "list", "list-tag"],
)
def test_as_tag(tag: Any, expected: str) -> None:
    assert as_tag(tag).render() == expected


def test_as_tag_warning() -> None:
    with pytest.warns(UserWarning):
        assert as_tag(1).render() == "1\n<!--Rendered type int not supported-->\n"  # type: ignore


def test_classes() -> None:

    div = tags.div()

    div.classes.add("test")
    div.classes.add("test")

    assert "test" in div.classes

    assert div.render() == '<div class="test"></div>'

    div.classes.swap("test", "other")
    div.classes.swap("test", "other")

    assert div.render() == '<div class="other"></div>'

    assert len(div.classes) == 1

    div.classes.remove("other")

    assert div.render() == '<div class=""></div>'

    div.classes.add("test")
    div.classes.add("other")
    div.classes.discard("test")
    assert div.render() == '<div class="other"></div>'


@pytest.mark.parametrize("prefix", ["data", "aria", "hx"])
def test_accessors(prefix: str) -> None:
    div = tags.div(other="ignored")

    pa = getattr(div, prefix)
    assert pa is not None

    pa["test"] = "test"
    assert div[f"{prefix}-test"] == "test"
    assert pa["test"] == "test"

    del pa["test"]
    assert f"{prefix}-test" not in div.attributes

    tag = pa.set("other-test", "other-value")
    assert tag == div
    assert tag[f"{prefix}-other-test"] == "other-value"

    tag = pa.remove("other-test")
    assert tag == div
    assert f"{prefix}-other-test" not in div.attributes

    div[f"{prefix}-parent-test"] = "test-4"
    assert pa["parent-test"] == "test-4"
    del div[f"{prefix}-parent-test"]

    pa["test1"] = "value-1"
    pa["test2"] = "value-2"
    assert len(pa) == 2
    assert set(pa) == {"test1", "test2"}


def test_tag_configurator() -> None:

    a = Tag(tags.a, classes={"test"}, attributes={"href": "#"})

    assert a["href"] == "#"
    a["href"] = "/test"
    a.classes.add("other")
    a.classes.discard("test")

    assert as_tag(a).render() == '<a class="other" href="/test"></a>'
