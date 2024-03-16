from pathlib import Path

from bootlace.nav import elements


def get_fixture(name: str) -> str:
    here = Path(__file__).parent

    if not name.endswith(".html"):
        name += ".html"

    return (here / "fixtures" / name).read_text()


class CurrentLink(elements.Link):

    @property
    def active(self) -> bool:
        return True


class DisabledLink(elements.Link):

    @property
    def enabled(self) -> bool:
        return False
