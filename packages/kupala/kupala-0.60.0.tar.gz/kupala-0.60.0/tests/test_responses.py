import json
import os
import typing as t

import jinja2
import pytest
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route, Router
from starlette.testclient import TestClient

from kupala import Kupala, responses
from kupala.templating import Templates


class TestText:
    def test_response(self) -> None:
        http_response = responses.text("ok")
        client = TestClient(http_response)
        response = client.get("/")
        assert response.text == "ok"

    def test_with_status(self) -> None:
        http_response = responses.text("ok", status_code=201)
        client = TestClient(http_response)
        response = client.get("/")
        assert response.status_code == 201

    def test_with_headers(self) -> None:
        http_response = responses.text("ok", headers={"X-Header": "value"})
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["x-header"] == "value"


class TestHTML:
    def test_response(self) -> None:
        http_response = responses.html("ok", status_code=201, headers={"X-Header": "value"})
        client = TestClient(http_response)
        response = client.get("/")
        assert response.status_code == 201
        assert response.headers["x-header"] == "value"
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.text == "ok"

    def test_with_status(self) -> None:
        http_response = responses.html("ok", status_code=201)
        client = TestClient(http_response)
        response = client.get("/")
        assert response.status_code == 201

    def test_with_headers(self) -> None:
        http_response = responses.html("ok", headers={"X-Header": "value"})
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["x-header"] == "value"


class TestEmpty:
    def test_response(self) -> None:
        http_response = responses.empty()
        client = TestClient(http_response)
        response = client.get("/")
        assert response.status_code == 204

    def test_with_headers(self) -> None:
        http_response = responses.empty(headers={"X-Header": "value"})
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["x-header"] == "value"


class TestRedirect:
    def test_response(self) -> None:
        http_response = responses.redirect("/about")
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.status_code == 302
        assert response.headers["location"] == "/about"

    def test_with_headers(self) -> None:
        http_response = responses.redirect("/about", headers={"X-Header": "value"})
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.headers["x-header"] == "value"

    def test_with_code(self) -> None:
        http_response = responses.redirect("/about", status_code=307)
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.status_code == 307


class TestRedirectToRoute:
    @pytest.fixture
    def http_request(self) -> Request:
        return Request(
            {
                "type": "http",
                "method": "GET",
                "url": "http://testserver/",
                "headers": [],
                "server": ("testserver", 80),
                "router": Router(
                    routes=[
                        Route("/about", endpoint=lambda r: Response(), name="about"),
                        Route("/page/{name}", endpoint=lambda r: Response(), name="page"),
                    ]
                ),
            }
        )

    def test_response(self, http_request: Request) -> None:
        http_response = responses.redirect_to_route(http_request, "about")
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.status_code == 302
        assert response.headers["location"] == "http://testserver/about"

    def test_with_params(self, http_request: Request) -> None:
        http_response = responses.redirect_to_route(http_request, "page", {"name": "about"})
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.headers["location"] == "http://testserver/page/about"

    def test_with_headers(self, http_request: Request) -> None:
        http_response = responses.redirect_to_route(http_request, "about", headers={"X-Header": "value"})
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.headers["x-header"] == "value"
        assert response.headers["location"] == "http://testserver/about"

    def test_with_code(self, http_request: Request) -> None:
        http_response = responses.redirect_to_route(http_request, "about", status_code=307)
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.status_code == 307
        assert response.headers["location"] == "http://testserver/about"


class TestJSON:
    def test_response(self) -> None:
        http_response = responses.json({"a": "b"})
        client = TestClient(http_response)
        response = client.get("/")
        assert response.text == '{\n  "a":"b"\n}'

    def test_with_status(self) -> None:
        http_response = responses.json({"a": "b"}, status_code=201)
        client = TestClient(http_response)
        response = client.get("/")
        assert response.status_code == 201

    def test_with_headers(self) -> None:
        http_response = responses.json({"a": "b"}, headers={"X-Header": "value"})
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["x-header"] == "value"

    def test_with_indent(self) -> None:
        http_response = responses.json({"a": "b"}, indent=4)
        client = TestClient(http_response)
        response = client.get("/")
        assert response.text == '{\n    "a":"b"\n}'

    def test_with_encoder(self) -> None:
        class _Encoder(json.JSONEncoder):
            def default(self, o: object) -> object:
                return "[]"

        http_response = responses.json(set(), encoder_class=_Encoder)
        client = TestClient(http_response)
        response = client.get("/")
        assert response.text == '"[]"'


class TestSendFile:
    def test_response(self, tmpdir: os.PathLike[str]) -> None:
        file_path = os.path.join(tmpdir, "file.bin")
        with open(str(file_path), "wb") as f:
            f.write(b"content")

        http_response = responses.send_file(file_path)

        client = TestClient(http_response)
        response = client.get("/")
        assert response.content == b"content"
        assert response.headers["content-type"] == "application/octet-stream"

    def test_with_filename(self, tmpdir: os.PathLike[str]) -> None:
        file_path = os.path.join(tmpdir, "file.bin")
        with open(str(file_path), "wb") as f:
            f.write(b"content")

        http_response = responses.send_file(file_path, filename="file.bin")

        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["content-disposition"] == 'attachment; filename="file.bin"'

    def test_with_headers(self, tmpdir: os.PathLike[str]) -> None:
        file_path = os.path.join(tmpdir, "file.bin")
        with open(str(file_path), "wb") as f:
            f.write(b"content")

        http_response = responses.send_file(file_path, headers={"X-Header": "value"})

        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["x-header"] == "value"

    def test_with_media_type(self, tmpdir: os.PathLike[str]) -> None:
        file_path = os.path.join(tmpdir, "file.bin")
        with open(str(file_path), "wb") as f:
            f.write(b"content")

        http_response = responses.send_file(file_path, media_type="image/jpeg")

        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["content-type"] == "image/jpeg"

    def test_send_inline(self, tmpdir: os.PathLike[str]) -> None:
        file_path = os.path.join(tmpdir, "file.bin")
        with open(str(file_path), "wb") as f:
            f.write(b"content")

        http_response = responses.send_file(file_path, inline=True, filename="file.bin")

        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["content-disposition"] == 'inline; filename="file.bin"'


class TestStreaming:
    def test_response(self) -> None:
        async def content() -> t.AsyncGenerator[str, None]:
            yield "1"
            yield "2"
            yield "3"

        http_response = responses.stream(content())
        client = TestClient(http_response)
        response = client.get("/")
        assert response.text == "123"

    def test_with_headers(self) -> None:
        async def content() -> t.AsyncGenerator[str, None]:
            yield "1"
            yield "2"
            yield "3"

        http_response = responses.stream(content(), headers={"X-Header": "value"})
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["x-header"] == "value"

    def test_with_status(self) -> None:
        async def content() -> t.AsyncGenerator[str, None]:
            yield "1"
            yield "2"
            yield "3"

        http_response = responses.stream(content(), status_code=201)
        client = TestClient(http_response)
        response = client.get("/")
        assert response.status_code == 201

    def test_with_media_type(self) -> None:
        async def content() -> t.AsyncGenerator[str, None]:
            yield "1"
            yield "2"
            yield "3"

        http_response = responses.stream(content(), media_type="image/jpeg")
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["content-type"] == "image/jpeg"


class TestGoBack:
    @pytest.fixture
    def http_request(self) -> Request:
        return Request(
            {
                "type": "http",
                "method": "GET",
                "url": "http://testserver/",
                "headers": [],
                "server": ("testserver", 80),
                "path": "/",
                "router": Router(
                    routes=[
                        Route("/about", endpoint=lambda r: Response(), name="about"),
                    ]
                ),
            }
        )

    def test_response(self, http_request: Request) -> None:
        http_request.scope["headers"].append((b"referer", b"http://testserver/somepage"))
        http_response = responses.back(http_request)
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.status_code == 302
        assert response.headers["location"] == "http://testserver/somepage"

    def test_bad_referer(self, http_request: Request) -> None:
        http_request.scope["headers"].append((b"referer", b"http://example.com/somepage"))
        http_response = responses.back(http_request)
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.headers["location"] == "http://testserver/"

    def test_no_referer(self, http_request: Request) -> None:
        http_response = responses.back(http_request)
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.headers["location"] == "http://testserver/"

    def test_with_code(self, http_request: Request) -> None:
        http_response = responses.back(http_request, status_code=307)
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.status_code == 307

    def test_with_headers(self, http_request: Request) -> None:
        http_response = responses.back(http_request, headers={"X-Header": "value"})
        client = TestClient(http_response, follow_redirects=False)
        response = client.get("/")
        assert response.headers["x-header"] == "value"


class TestTemplate:
    @pytest.fixture
    def http_request(self) -> Request:
        return Request(
            {
                "type": "http",
                "method": "GET",
                "url": "http://testserver/",
                "headers": [],
                "server": ("testserver", 80),
                "path": "/",
                "router": Router(
                    routes=[
                        Route("/about", endpoint=lambda r: Response(), name="about"),
                    ]
                ),
                "app": Kupala(
                    secret_key="key!",
                    extensions=[
                        Templates(
                            template_loaders=[
                                jinja2.DictLoader(
                                    {
                                        "index.html": "Hello, {{ name }}!",
                                        "nocontext.html": "Hello!",
                                    }
                                )
                            ]
                        ),
                    ],
                ),
            }
        )

    def test_response(self, http_request: Request) -> None:
        http_response = responses.template(http_request, "nocontext.html")
        client = TestClient(http_response)
        response = client.get("/")
        assert response.text == "Hello!"

    def test_with_context(self, http_request: Request) -> None:
        http_response = responses.template(http_request, "index.html", {"name": "world"})
        client = TestClient(http_response)
        response = client.get("/")
        assert response.text == "Hello, world!"

    def test_with_code(self, http_request: Request) -> None:
        http_response = responses.template(http_request, "index.html", {"name": "world"}, status_code=201)
        client = TestClient(http_response)
        response = client.get("/")
        assert response.status_code == 201

    def test_with_headers(self, http_request: Request) -> None:
        http_response = responses.template(http_request, "index.html", {"name": "world"}, headers={"X-Header": "value"})
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["x-header"] == "value"

    def test_with_media_type(self, http_request: Request) -> None:
        http_response = responses.template(http_request, "index.html", {"name": "world"}, media_type="image/jpeg")
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["content-type"] == "image/jpeg"


class TestTemplateBlock:
    @pytest.fixture
    def http_request(self) -> Request:
        return Request(
            {
                "type": "http",
                "method": "GET",
                "url": "http://testserver/",
                "headers": [],
                "server": ("testserver", 80),
                "path": "/",
                "router": Router(
                    routes=[
                        Route("/about", endpoint=lambda r: Response(), name="about"),
                    ]
                ),
                "app": Kupala(
                    secret_key="key!",
                    extensions=[
                        Templates(
                            template_loaders=[
                                jinja2.DictLoader(
                                    {
                                        "index.html": "{% block content %}Hello, {{ name }}!{% endblock %}",
                                        "nocontext.html": "{% block content %}Hello!{% endblock %}",
                                    }
                                )
                            ]
                        ),
                    ],
                ),
            }
        )

    def test_response(self, http_request: Request) -> None:
        http_response = responses.template_block(http_request, "nocontext.html", "content")
        client = TestClient(http_response)
        response = client.get("/")
        assert response.text == "Hello!"

    def test_with_context(self, http_request: Request) -> None:
        http_response = responses.template_block(http_request, "index.html", "content", {"name": "world"})
        client = TestClient(http_response)
        response = client.get("/")
        assert response.text == "Hello, world!"

    def test_with_code(self, http_request: Request) -> None:
        http_response = responses.template_block(
            http_request, "index.html", "content", {"name": "world"}, status_code=201
        )
        client = TestClient(http_response)
        response = client.get("/")
        assert response.status_code == 201

    def test_with_headers(self, http_request: Request) -> None:
        http_response = responses.template_block(
            http_request, "index.html", "content", {"name": "world"}, headers={"X-Header": "value"}
        )
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["x-header"] == "value"

    def test_with_media_type(self, http_request: Request) -> None:
        http_response = responses.template_block(
            http_request, "index.html", "content", {"name": "world"}, media_type="image/jpeg"
        )
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["content-type"] == "image/jpeg"


class TestTemplateMacro:
    @pytest.fixture
    def http_request(self) -> Request:
        return Request(
            {
                "type": "http",
                "method": "GET",
                "url": "http://testserver/",
                "headers": [],
                "server": ("testserver", 80),
                "path": "/",
                "router": Router(
                    routes=[
                        Route("/about", endpoint=lambda r: Response(), name="about"),
                    ]
                ),
                "app": Kupala(
                    secret_key="key!",
                    extensions=[
                        Templates(
                            template_loaders=[
                                jinja2.DictLoader(
                                    {
                                        "index.html": "{% macro content(name) %}Hello, {{ name }}!{% endmacro %}",
                                        "nocontext.html": "{% macro content(name) %}Hello!{% endmacro %}",
                                    }
                                )
                            ]
                        ),
                    ],
                ),
            }
        )

    def test_response(self, http_request: Request) -> None:
        http_response = responses.template_macro(http_request, "nocontext.html", "content")
        client = TestClient(http_response)
        response = client.get("/")
        assert response.text == "Hello!"

    def test_with_context(self, http_request: Request) -> None:
        http_response = responses.template_macro(http_request, "index.html", "content", {"name": "world"})
        client = TestClient(http_response)
        response = client.get("/")
        assert response.text == "Hello, world!"

    def test_with_code(self, http_request: Request) -> None:
        http_response = responses.template_macro(
            http_request, "index.html", "content", {"name": "world"}, status_code=201
        )
        client = TestClient(http_response)
        response = client.get("/")
        assert response.status_code == 201

    def test_with_headers(self, http_request: Request) -> None:
        http_response = responses.template_macro(
            http_request, "index.html", "content", {"name": "world"}, headers={"X-Header": "value"}
        )
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["x-header"] == "value"

    def test_with_media_type(self, http_request: Request) -> None:
        http_response = responses.template_macro(
            http_request, "index.html", "content", {"name": "world"}, media_type="image/jpeg"
        )
        client = TestClient(http_response)
        response = client.get("/")
        assert response.headers["content-type"] == "image/jpeg"
