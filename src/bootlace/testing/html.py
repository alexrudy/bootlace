import textwrap
from collections.abc import Callable
from xml.etree import ElementTree

import attrs
import html5lib

Element = ElementTree.Element

Filter = Callable[[Element], Element | None]

ATTRIBUTES = {
    "role",
}


@attrs.define(str=False)
class Difference:
    expected: str | None
    actual: str | None
    message: str

    def __str__(self) -> str:
        return f"{self.message}: \n Expected: {self.expected}\n Found: {self.actual}"


@attrs.define(str=False)
class TagDifference:
    expected: Element
    actual: Element | None
    differences: list[Difference] = attrs.field(factory=list)

    def __str__(self) -> str:
        differences = textwrap.indent("\n".join(str(difference) for difference in self.differences), prefix="  ")
        return f"Tag {self.expected.tag} differences:\n{differences}"

    def __bool__(self) -> bool:
        return bool(self.differences)

    def append(self, difference: Difference) -> None:
        self.differences.append(difference)


@attrs.define(str=False)
class Result:
    differences: list[TagDifference] = attrs.field(factory=list)

    def __bool__(self) -> bool:
        return bool(self.differences)

    def __str__(self) -> str:
        if not self.differences:
            return "No differences found"
        else:
            n = sum(len(differences.differences) for differences in self.differences)
            message = f"{n} differences found"
            details = "\n".join(textwrap.indent(str(difference), prefix="  ") for difference in self.differences)
            return f"{message}:\n{details}"


@attrs.define
class HTMLDiff:
    filters: list[Filter] = attrs.field(factory=list)
    attributes: set[str] = attrs.field(factory=set)

    def compare(self, expected_html: str, actual_html: str) -> Result:
        expected = html5lib.parse(expected_html, namespaceHTMLElements=False)
        actual = html5lib.parse(actual_html, namespaceHTMLElements=False)

        differences: list[TagDifference] = []
        actual = actual.iter()
        for element in expected.iter():
            element = self._filter(element)
            if element is None:
                continue

            tagdiff = self._compare(element, next(actual, None))
            if tagdiff:
                differences.append(tagdiff)
            if tagdiff.actual is None:
                # Ran out of tags to compare
                break

        return Result(differences)

    def _filter(self, element: Element) -> Element | None:
        for filter in self.filters:
            element = filter(element)  # type: ignore
            if element is None:
                return None
        return element

    def _compare(self, expected: Element, actual: Element | None) -> TagDifference:
        if actual is None:
            return TagDifference(expected, actual, [Difference(expected.tag, None, "Tag not found")])

        differences = TagDifference(expected, actual)
        if expected.tag != actual.tag:
            differences.append(Difference(expected.tag, actual.tag, "Tag mismatch"))

        classes = set(expected.get("class", "").split())
        actual_classes = set(actual.get("class", "").split())
        if classes != actual_classes:
            differences.append(Difference(",".join(classes), ",".join(actual_classes), "Class mismatch"))

        if "href" in expected.attrib:
            expected_href = expected.attrib["href"]
            actual_href = actual.attrib.get("href", "")

            if expected_href == "#":
                expected_href = ""
            if actual_href == "#":
                actual_href = ""
            if expected_href != actual_href:
                differences.append(Difference(expected_href, actual_href, "Href mismatch"))

        for attr, value in expected.attrib.items():
            if (attr in self.attributes) or (attr.startswith("aria-")):
                if attr not in actual.attrib:
                    differences.append(Difference(attr, None, "Attribute not found"))
                    continue
                if actual.get(attr) != value:
                    differences.append(
                        Difference(
                            value,
                            actual.get(attr),
                            f"Attribute {attr} mismatch",
                        )
                    )
                    continue

        for attr in actual.attrib:
            if (attr in self.attributes) or (attr.startswith("aria-")):
                if attr not in expected.attrib:
                    differences.append(Difference(None, actual.attrib.get(attr), f"Attribute {attr} not expected"))
                    continue

        return differences


def assert_same_html(expected_html: str, actual_html: str) -> None:
    __tracebackhide__ = True
    diff = HTMLDiff(attributes=ATTRIBUTES)
    result = diff.compare(expected_html, actual_html)
    assert not result, str(result)
