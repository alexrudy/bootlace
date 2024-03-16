import enum


class SizeClass(enum.Enum):
    EXTRA_SMALL = None
    SMALL = "sm"
    MEDIUM = "md"
    LARGE = "lg"
    EXTRA_LARGE = "xl"
    EXTRA_EXTRA_LARGE = "xxl"

    def add_to_class(self, cls: str) -> str:
        if self.value:
            return f"{cls}-{self.value}"
        else:
            return cls
