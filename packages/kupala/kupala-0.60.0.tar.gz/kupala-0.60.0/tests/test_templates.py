import pathlib
import typing

import jinja2
import pytest
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

from kupala import Kupala
from kupala.routing import Route
from kupala.templating import Templates

jinja_env = jinja2.Environment(
    loader=jinja2.DictLoader(
        {
            "index.html": "Hello, {{ name }}!",
            "macro.html": "{% macro hello(name) %}Hello, {{ name }}!{% endmacro %}",
            "block.html": "{% block content %}Hello, {{ name }}!{% endblock %}",
            "request.html": "{{ request }}",
            "app.html": "{{ app }}",
            "url_matches.html": "{{ url_matches('/test') }} - {{ url_matches('/no-test') }}",
            "route_matches.html": "{{ route_matches('test') }} - {{ route_matches('no-test') }}",
        }
    ),
)


def test_directories(tmp_path: pathlib.Path) -> None:
    (tmp_path / "index.html").write_text("Hello, world!")
    templates = Templates(directories=[tmp_path])
    assert templates.render("index.html") == "Hello, world!"


def test_template_loaders() -> None:
    templates = Templates(template_loaders=[jinja2.DictLoader({"index.html": "Hello, world!"})])
    assert templates.render("index.html") == "Hello, world!"


def test_globals() -> None:
    templates = Templates(
        template_loaders=[jinja2.DictLoader({"index.html": "Hello, {{ name }}!"})],
        globals={"name": "world"},
    )
    assert templates.render("index.html") == "Hello, world!"


def test_filters() -> None:
    templates = Templates(
        template_loaders=[jinja2.DictLoader({"index.html": "Hello, {{ name|up }}!"})],
        filters={"up": str.upper},
    )
    assert templates.render("index.html", {"name": "world"}) == "Hello, WORLD!"


def test_tests() -> None:
    templates = Templates(
        template_loaders=[jinja2.DictLoader({"index.html": "Hello, {{ 'UP' if name is up else 'up' }}!"})],
        tests={"up": lambda x: x.isupper()},
    )
    assert templates.render("index.html", {"name": "WORLD"}) == "Hello, UP!"


def test_undefined_on() -> None:
    templates = Templates(
        allow_undefined=True, template_loaders=[jinja2.DictLoader({"index.html": "Hello, {{ value }}!"})]
    )
    assert templates.render("index.html") == "Hello, !"


def test_undefined_off() -> None:
    templates = Templates(
        allow_undefined=False, template_loaders=[jinja2.DictLoader({"index.html": "Hello, {{ value }}!"})]
    )
    with pytest.raises(jinja2.exceptions.UndefinedError):
        assert templates.render("index.html") == "Hello, <world>!"


def test_autoescape_on() -> None:
    templates = Templates(auto_escape=True, template_loaders=[jinja2.DictLoader({"index.html": "Hello, {{ value }}!"})])
    assert templates.render("index.html", {"value": "<world>"}) == "Hello, &lt;world&gt;!"


def test_autoescape_off() -> None:
    templates = Templates(
        auto_escape=False, template_loaders=[jinja2.DictLoader({"index.html": "Hello, {{ value }}!"})]
    )
    assert templates.render("index.html", {"value": "<world>"}) == "Hello, <world>!"


def test_context_processors() -> None:
    def context_processor(request: Request) -> dict[str, typing.Any]:
        return {"name": "world"}

    templates = Templates(
        template_loaders=[jinja2.DictLoader({"index.html": "Hello, {{ name }}!"})],
        context_processors=[context_processor],
    )
    request = Request({"type": "http", "method": "GET", "url": "http://testserver/", "app": Kupala("key")})
    assert templates.render_to_response(request, "index.html", {"name": "world"}).body == b"Hello, world!"


def test_render() -> None:
    templates = Templates(jinja_env=jinja_env)
    assert templates.render("index.html", {"name": "world"}) == "Hello, world!"


def test_render_macro() -> None:
    templates = Templates(jinja_env=jinja_env)
    assert templates.render_macro("macro.html", "hello", {"name": "world"}) == "Hello, world!"


def test_render_block() -> None:
    templates = Templates(jinja_env=jinja_env)
    assert templates.render_block("block.html", "content", {"name": "world"}) == "Hello, world!"


def test_render_to_response() -> None:
    templates = Templates(jinja_env=jinja_env)
    request = Request({"type": "http", "method": "GET", "url": "http://testserver/", "app": Kupala("key")})
    assert templates.render_to_response(request, "index.html", {"name": "world"}).body == b"Hello, world!"


async def view(request: Request) -> Response:
    return PlainTextResponse("ok")


class TestStandardContextProcessor:
    def test_request(self) -> None:
        templates = Templates(jinja_env=jinja_env)
        request = Request(
            {"type": "http", "method": "GET", "url": "http://testserver/", "app": Kupala(secret_key="secret")}
        )
        assert b"starlette.requests.Request" in templates.render_to_response(request, "request.html").body

    def test_app(self) -> None:
        templates = Templates(jinja_env=jinja_env)
        request = Request(
            {"type": "http", "method": "GET", "url": "http://testserver/", "app": Kupala(secret_key="secret")}
        )
        assert b"kupala.applications.Kupala" in templates.render_to_response(request, "app.html").body

    def test_url_matches(self) -> None:
        templates = Templates(jinja_env=jinja_env)
        request = Request(
            {
                "type": "http",
                "method": "GET",
                "url": "http://testserver/",
                "headers": ((b"host", b"testserver"),),
                "path": "/test",
                "app": Kupala(
                    secret_key="secret",
                    routes=[
                        Route("/test", view),
                    ],
                ),
            }
        )
        assert b"True - False" in templates.render_to_response(request, "url_matches.html").body

    def test_route_matches(self) -> None:
        templates = Templates(jinja_env=jinja_env)
        request = Request(
            {
                "type": "http",
                "method": "GET",
                "url": "http://testserver/",
                "headers": ((b"host", b"testserver"),),
                "path": "/test",
                "app": Kupala(
                    secret_key="secret",
                    routes=[
                        Route("/test", view, name="test"),
                        Route("/no-test", view, name="no-test"),
                    ],
                ),
            }
        )
        assert b"True - False" in templates.render_to_response(request, "route_matches.html").body
