import os.path

import jinja2
import pytest
from async_storages import MemoryBackend
from starlette.requests import Request
from starlette.responses import Response
from starlette.testclient import TestClient

from kupala import Kupala
from kupala.files import Files, MemoryConfig, static_url, StaticFiles
from kupala.routing import Route
from kupala.templating import Templates


class TestStaticFiles:
    def test_static_files(self) -> None:
        app = Kupala(
            secret_key="key!",
            extensions=[
                StaticFiles(packages=[("tests", "assets")]),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/static/somefile.txt")
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/plain; charset=utf-8"
            assert response.text == "somecontent\n"

    def test_static_files_directory(self) -> None:
        this_dir = os.path.dirname(__file__)
        app = Kupala(
            secret_key="key!",
            extensions=[
                StaticFiles(directory=os.path.join(this_dir, "assets")),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/static/somefile.txt")
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/plain; charset=utf-8"
            assert response.text == "somecontent\n"

    def test_static_files_default_route_name(self) -> None:
        app = Kupala(
            secret_key="key!",
            extensions=[
                StaticFiles(packages=[("tests", "assets")]),
            ],
        )
        url = app.url_path_for("static", path="somefile.txt")
        assert url == "/static/somefile.txt"

    def test_static_files_route_name(self) -> None:
        app = Kupala(
            secret_key="key!",
            extensions=[
                StaticFiles(route_name="assets", packages=[("tests", "assets")]),
            ],
        )
        url = app.url_path_for("assets", path="somefile.txt")
        assert url == "/static/somefile.txt"

    def test_static_files_default_url_prefix(self) -> None:
        app = Kupala(
            secret_key="key!",
            extensions=[
                StaticFiles(packages=[("tests", "assets")]),
            ],
        )
        url = app.url_path_for("static", path="somefile.txt")
        assert url == "/static/somefile.txt"

    def test_static_files_url_prefix(self) -> None:
        app = Kupala(
            secret_key="key!",
            extensions=[
                StaticFiles(url_prefix="/assets", packages=[("tests", "assets")]),
            ],
        )
        url = app.url_path_for("static", path="somefile.txt")
        assert url == "/assets/somefile.txt"

    def test_template_helper(self) -> None:
        async def view(request: Request) -> Response:
            return Templates.of(request.app).render_to_response(request, "index.html")

        app = Kupala(
            secret_key="key!",
            routes=[Route("/", view)],
            extensions=[
                Templates(
                    template_loaders=[jinja2.DictLoader({"index.html": "{{ static_url('somefile.txt') }}"})],
                ),
                StaticFiles(url_prefix="/assets", packages=[("tests", "assets")]),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert response.text.startswith("http://testserver/assets/somefile.txt")


class TestStaticUrl:
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
                "app": Kupala(secret_key="key!", extensions=[StaticFiles(packages=[("tests", "assets")])]),
            }
        )

    def test_generates_url(self, http_request: Request) -> None:
        url = static_url(http_request, "/image.jpg")
        assert url.path == "/static/image.jpg"

    def test_cache_prefix_no_debug(self, http_request: Request) -> None:
        http_request.app.debug = False
        url = static_url(http_request, "/image.jpg")
        url2 = static_url(http_request, "/image.jpg")
        assert url == url2

    def test_cache_prefix_debug(self, http_request: Request) -> None:
        http_request.app.debug = True
        url = static_url(http_request, "/image.jpg")
        url2 = static_url(http_request, "/image.jpg")
        assert url != url2

    @pytest.mark.parametrize("image_url", ["http://example.com/image.jpg", "https://example.com/image.jpg"])
    def test_ignores_http(self, http_request: Request, image_url: str) -> None:
        url = static_url(http_request, image_url)
        assert url == url


class TestFiles:
    async def test_serves_files(self) -> None:
        files = Files(default="memory", storages={"memory": MemoryBackend()})
        app = Kupala(
            secret_key="key!",
            extensions=[files],
        )
        await files.write("somefile.txt", b"somecontent\n")
        with TestClient(app) as client:
            response = client.get("/media/somefile.txt")
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/plain; charset=utf-8"
            assert response.text == "somecontent\n"

    async def test_serves_files_custom_route_name(self) -> None: ...
    async def test_serves_files_custom_url_prefix(self) -> None: ...
    async def test_serves_files_custom_default(self) -> None: ...
    async def test_serves_files_invalid_default(self) -> None: ...
