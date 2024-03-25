import enum


class ColorClass(enum.Enum):
    """Bootstrap color classes"""

    #: Default foreground (color) and background, including components.
    BODY = None

    #: Main theme color, used for hyperlinks, focus styles, and component and form active states.
    PRIMARY = "primary"

    #: Secondary theme color, used for secondary buttons and form elements.
    SECONDARY = "secondary"

    #: Tertiary theme color, used for tertiary buttons and form elements.
    TERTIARY = "tertiary"

    #: Success state color, used for success messages and indicators.
    SUCCESS = "success"

    #: Danger state color, used for error messages and indicators.
    DANGER = "danger"

    #: Warning state color, used for warning messages and indicators.
    WARNING = "warning"

    #: Info state color, used for informational messages and indicators.
    INFO = "info"

    #: Additional theme option for less contrasting colors.
    LIGHT = "light"

    #: Additional theme option for higher contrasting colors.
    DARK = "dark"

    def add_to_class(self, cls: str) -> str:
        """Add the color class name to the given class."""
        if self.value:
            return f"{cls}-{self.value}"
        return cls
