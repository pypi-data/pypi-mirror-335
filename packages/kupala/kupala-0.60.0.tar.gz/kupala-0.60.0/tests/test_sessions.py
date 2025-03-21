import pytest
from starlette.requests import Request
from starlette.responses import Response
from starlette.testclient import TestClient
from starsessions import CookieStore, load_session, SessionNotLoaded

from kupala import Kupala
from kupala.routing import Route
from kupala.sessions import Sessions


async def set_value_view(request: Request) -> Response:
    request.session["test"] = "test"
    return Response("ok")


async def get_value_view(request: Request) -> Response:
    return Response(request.session["test"])


async def set_load_value_view(request: Request) -> Response:
    await load_session(request)
    request.session["test"] = "test"
    return Response("ok")


async def get_load_value_view(request: Request) -> Response:
    await load_session(request)
    return Response(request.session["test"])


def test_sessions() -> None:
    app = Kupala(
        secret_key="key!",
        routes=[
            Route("/set", set_value_view),
            Route("/get", get_value_view),
            Route("/set-load", set_load_value_view),
            Route("/get-load", get_load_value_view),
        ],
        extensions=[
            Sessions(
                store=CookieStore("key!"),
                cookie_https_only=False,
            )
        ],
    )
    with TestClient(app) as client:
        with pytest.raises(SessionNotLoaded):
            response = client.get("/set")
            assert response.status_code == 500

        response = client.get("/set-load")
        assert response.status_code == 200

        response = client.get("/get-load")
        assert response.status_code == 200
        assert response.text == "test"


def test_sessions_autoload() -> None:
    app = Kupala(
        secret_key="key!",
        routes=[
            Route("/set", set_value_view),
            Route("/get", get_value_view),
        ],
        extensions=[
            Sessions(
                autoload=True,
                store=CookieStore("key!"),
                cookie_https_only=False,
            )
        ],
    )
    with TestClient(app) as client:
        response = client.get("/set")
        assert response.status_code == 200

        response = client.get("/get")
        assert response.status_code == 200
        assert response.text == "test"


def test_sessions_cookie_name() -> None:
    app = Kupala(
        secret_key="key!",
        routes=[
            Route("/set", set_value_view),
        ],
        extensions=[Sessions(autoload=True, store=CookieStore("key!"), cookie_https_only=False, cookie_name="sid")],
    )
    with TestClient(app) as client:
        response = client.get("/set")
        assert response.status_code == 200
        assert "sid" in response.cookies


def test_sessions_cookie_same_site() -> None:
    app = Kupala(
        secret_key="key!",
        routes=[
            Route("/set", set_value_view),
        ],
        extensions=[
            Sessions(autoload=True, store=CookieStore("key!"), cookie_https_only=False, cookie_same_site="lax")
        ],
    )
    with TestClient(app) as client:
        response = client.get("/set")
        assert response.status_code == 200
        assert "lax" in response.headers["set-cookie"]


def test_sessions_cookie_domain() -> None:
    app = Kupala(
        secret_key="key!",
        routes=[
            Route("/set", set_value_view),
        ],
        extensions=[
            Sessions(autoload=True, store=CookieStore("key!"), cookie_https_only=False, cookie_domain="testserver")
        ],
    )
    with TestClient(app) as client:
        response = client.get("/set")
        assert response.status_code == 200
        assert response.cookies.get("session", domain=".testserver")


def test_sessions_cookie_path() -> None:
    app = Kupala(
        secret_key="key!",
        routes=[
            Route("/set", set_value_view),
        ],
        extensions=[Sessions(autoload=True, store=CookieStore("key!"), cookie_https_only=False, cookie_path="/secure")],
    )
    with TestClient(app) as client:
        response = client.get("/set")
        assert response.status_code == 200
        assert response.cookies.get("session", path="/secure")
