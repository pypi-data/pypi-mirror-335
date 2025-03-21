import contextlib
import typing
from unittest import mock

import click
import pytest
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from starlette.types import Scope

from kupala import Kupala


class TestApp:
    async def test_sets_current_app(self) -> None:
        app = Kupala(secret_key="key!")
        async with app.initialize():
            assert Kupala.current() is app
        assert Kupala.current() is None

    async def test_initializers(self) -> None:
        value = 0

        @contextlib.asynccontextmanager
        async def initializer(app: Kupala) -> typing.AsyncGenerator[None, None]:
            nonlocal value
            value = 1
            yield None
            value = 0

        app = Kupala(secret_key="key!", initializers=[initializer])
        async with app.initialize():
            assert value == 1
        assert value == 0

    def test_extensions(self) -> None:
        configure_callback = mock.MagicMock()
        extension = mock.MagicMock(configure=configure_callback)
        app = Kupala(secret_key="key!", extensions=[extension])
        configure_callback.assert_called_once_with(app)


class TestASGIApp:
    async def test_injects_app_into_scope(self) -> None:
        app = Kupala(secret_key="key!")
        scope: Scope = {"type": "http", "path": "/", "method": "GET", "headers": []}
        await app(scope, mock.AsyncMock(), mock.AsyncMock())
        assert scope["app"] is app


class TestCommandLineApp:
    def test_initializers(self) -> None:
        stack: list[int] = []

        @contextlib.asynccontextmanager
        async def initializer(app: Kupala) -> typing.AsyncGenerator[None, None]:
            stack.append(1)
            yield None
            stack.append(2)

        app = Kupala(secret_key="key!", initializers=[initializer])
        app.run_cli()
        assert stack == [1, 2]

    def test_calls_sync_command(self) -> None:
        spy = mock.MagicMock()

        @click.command("call-me")
        def command() -> None:
            spy()

        app = Kupala(secret_key="key!", commands=[command])
        app.run_cli("call-me")
        spy.assert_called_once()

    def test_calls_async_command(self) -> None:
        spy = mock.MagicMock()

        @click.command("call-me")
        async def command() -> None:
            spy()

        app = Kupala(secret_key="key!", commands=[command])
        app.run_cli("call-me")
        spy.assert_called_once()

    def test_unknown_command(self) -> None:
        spy = mock.MagicMock()

        app = Kupala(secret_key="key!")
        with pytest.raises(SystemExit):
            app.run_cli("call-me")
            spy.assert_called_once()

    def test_injects_app_as_obj(self) -> None:
        spy = mock.MagicMock()

        @click.command("call-me")
        @click.pass_obj
        def command(obj: Kupala) -> None:
            spy(obj)

        app = Kupala(secret_key="key!", commands=[command])
        app.run_cli("call-me")
        spy.assert_called_once_with(app)


class TestTrustedHosts:
    def test_trusted_hosts(self) -> None:
        app = Kupala(
            secret_key="key!",
            trusted_hosts=["example.com", "*.example.com"],
            routes=[
                Route("/", PlainTextResponse("OK")),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/", headers={"host": "example.com"})
            assert response.status_code == 200

            response = client.get("/", headers={"host": "sub.example.com"})
            assert response.status_code == 200

            response = client.get("/", headers={"host": "another.org"})
            assert response.status_code == 400


class TestCompressResponse:
    def test_compression_on(self) -> None:
        app = Kupala(
            secret_key="key!",
            compress_response=True,
            routes=[
                Route("/", PlainTextResponse("0" * 512)),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert response.headers["content-encoding"] == "gzip"

    def test_compression_off(self) -> None:
        app = Kupala(
            secret_key="key!",
            compress_response=False,
            routes=[
                Route("/", PlainTextResponse("0" * 512)),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert "content-encoding" not in response.headers
