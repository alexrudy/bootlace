import pytest

from bootlace.style import ColorClass


@pytest.mark.parametrize(
    "colorclass,name",
    zip(
        ColorClass,
        [
            "btn",
            "btn-primary",
            "btn-secondary",
            "btn-tertiary",
            "btn-success",
            "btn-danger",
            "btn-warning",
            "btn-info",
            "btn-light",
            "btn-dark",
        ],
        strict=True,
    ),
    ids=list(cc.name for cc in ColorClass),
)
def test_sizeclass(colorclass: ColorClass, name: str) -> None:
    assert colorclass.add_to_class("btn") == name
