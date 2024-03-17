from typing import Any

import pytest
from dominate import tags

from bootlace.util import as_tag


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

    div.classes.remove("other")

    assert div.render() == '<div class=""></div>'
