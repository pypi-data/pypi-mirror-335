from unittest import mock

from starlette.types import Receive, Scope, Send

from kupala.contrib.sqlalchemy.manager import Database
from kupala.contrib.sqlalchemy.middleware import DbSessionMiddleware


empty_send = mock.AsyncMock()
empty_receive = mock.AsyncMock()


async def test_injects_dbsession() -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        pass

    middleware = DbSessionMiddleware(
        app,
        {
            "default": Database("sqlite+aiosqlite:///:memory:"),
        },
    )
    scope: Scope = {"type": "http"}
    await middleware(scope, empty_receive, empty_send)
    assert "dbsession" in scope["state"]
    assert "dbsession_default" in scope["state"]


async def test_injects_multiple_dbsessions() -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        pass

    middleware = DbSessionMiddleware(
        app,
        {
            "default": Database("sqlite+aiosqlite:///:memory:"),
            "read_only": Database("sqlite+aiosqlite:///:memory:"),
        },
    )
    scope: Scope = {"type": "http"}
    await middleware(scope, empty_receive, empty_send)
    assert "dbsession" in scope["state"]
    assert "dbsession_default" in scope["state"]
    assert "dbsession_read_only" in scope["state"]
