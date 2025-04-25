from typing import Any

import attrs
from flask import Blueprint
from flask import Flask
from flask import current_app

from .endpoint import Endpoint
from .resources import Resources
from .util import as_tag
from .util import render


@attrs.define(init=False, eq=False)
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

        if app.config.setdefault("BOOTLACE_CONTEXT_PROCESSORS", True):
            app.context_processor(context)

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

    def bootstrap(self) -> "Resources":
        return Resources(
            endpoint=Endpoint.from_name(self.static_view),
            resources=["bootstrap.min.js", "bootstrap.min.css"],
        )


def context() -> dict[str, Any]:
    return {
        "render": render,
        "as_tag": as_tag,
    }
