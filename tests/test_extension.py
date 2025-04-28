from flask import Flask

from bootlace.extension import Bootlace
from bootlace.extension import context
from bootlace.util import as_tag
from bootlace.util import render


def test_extension(app: Flask) -> None:
    bootlace = Bootlace(app)

    with app.app_context():
        bootstrap = bootlace.bootstrap()

    with app.test_client() as client:
        for resource in bootstrap.iter_resources(extension=None):
            with client.get(resource) as response:
                assert response.status_code == 200

    with app.test_request_context("/"):
        tags = bootstrap.css()
        assert str(tags).strip() == '<link href="/static/bootstrap/bootstrap.min.css" rel="stylesheet">'

        tags = bootstrap.js()
        assert str(tags).strip() == '<script src="/static/bootstrap/bootstrap.min.js"></script>'

        assert len(list(bootstrap.iter_resources(extension="css"))) == 1


def test_extension_configuration(app: Flask) -> None:
    app.config["BOOTLACE_CONTEXT_PROCESSORS"] = False
    bootlace = Bootlace(app)  # noqa: F841

    assert len(app.template_context_processors[None]) == 1


def test_extension_context_processor() -> None:
    ctx = context()
    assert ctx["render"] is render
    assert ctx["as_tag"] is as_tag
