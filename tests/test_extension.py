from flask import Flask

from bootlace.extension import Bootlace


def test_extension(app: Flask) -> None:

    bootlace = Bootlace(app)

    with app.test_request_context("/"):

        assert bootlace.icons == "/static/bootstrap/icons/bootstrap-icons.svg"
        assert bootlace.css == "/static/bootstrap/css/bootstrap.min.css"
        assert bootlace.js == "/static/bootstrap/js/bootstrap.min.js"

    with app.test_client() as client:

        with client.get("/static/bootstrap/icons/bootstrap-icons.svg") as response:
            assert response.status_code == 200

        with client.get("/static/bootstrap/css/bootstrap.min.css") as response:
            assert response.status_code == 200

        with client.get("/static/bootstrap/js/bootstrap.min.js") as response:
            assert response.status_code == 200
