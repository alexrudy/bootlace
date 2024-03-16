import enum


class ColorClass(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    LIGHT = "light"
    DARK = "dark"
    WHITE = "white"
    TRANSPARENT = "transparent"

    def add_to_class(self, cls: str) -> str:
        return f"{cls}-{self.value}"
