import pytest

from bootlace.size import SizeClass


@pytest.mark.parametrize(
    "sizeclass,col",
    zip(SizeClass, ["col", "col-sm", "col-md", "col-lg", "col-xl", "col-xxl"], strict=True),
    ids=list(sc.name for sc in SizeClass),
)
def test_sizeclass(sizeclass: SizeClass, col: str) -> None:
    assert sizeclass.add_to_class("col") == col
