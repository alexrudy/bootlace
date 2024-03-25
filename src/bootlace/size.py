import enum


class SizeClass(enum.Enum):
    """Bootstrap size classes"""

    #: Extra-small is the default size class used when none is specified. < 576px
    EXTRA_SMALL = None

    #: Small size class <768px
    SMALL = "sm"

    #: Medium size class <992px
    MEDIUM = "md"

    #: Large size class <1200px
    LARGE = "lg"

    #: Extra-large size class <1400px
    EXTRA_LARGE = "xl"

    #: Extra-extra-large size class >=1400px
    EXTRA_EXTRA_LARGE = "xxl"

    def add_to_class(self, cls: str) -> str:
        """Add the size class to the given class."""
        if self.value:
            return f"{cls}-{self.value}"
        else:
            return cls
