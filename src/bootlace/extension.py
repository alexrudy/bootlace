from flask import Blueprint
from flask import current_app
from flask import Flask
from flask import url_for


class Bootlace:
    """Flask extension for bootlace"""

    def __init__(self, app: Flask | None = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize the extension with the Flask app"""

        app.extensions["bootlace"] = self
        app.jinja_env.globals["bootlace"] = self

        name = app.config.setdefault("BOOTLACE_BLUEPRINT_NAME", "bootlace")

        blueprint = Blueprint(
            name,
            __name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/static/bootstrap",
        )

        app.register_blueprint(blueprint)

    @property
    def static_view(self) -> str:
        bp = current_app.config["BOOTLACE_BLUEPRINT_NAME"]
        return f"{bp}.static"

    @property
    def icons(self) -> str:
        """The URL for the SVG source for the icons"""
        return url_for(self.static_view, filename="icons/bootstrap-icons.svg")

    @property
    def css(self) -> str:
        """The URL for the Bootstrap CSS file"""
        return url_for(self.static_view, filename="css/bootstrap.min.css")

    @property
    def js(self) -> str:
        """The URL for the Bootstrap JS file"""
        return url_for(self.static_view, filename="js/bootstrap.min.js")
