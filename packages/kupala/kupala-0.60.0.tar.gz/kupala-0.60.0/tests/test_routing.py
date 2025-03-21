import functools
import typing

import anyio
import pytest
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Mount, Router
from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from kupala.applications import Kupala
from kupala.dependencies import FactoryResolver
from kupala.responses import JSONResponse
from kupala.routing import (
    abs_url_for,
    AsyncViewCallable,
    CallNext,
    Route,
    route_matches,
    RouteGroup,
    url_matches,
    WebSocketRoute,
    WebSocketViewCallable,
)


@pytest.fixture
def route_group() -> RouteGroup:
    return RouteGroup()


async def example_set_middleware(request: Request, call_next: CallNext) -> Response:
    request.state.value = "set"
    return await call_next(request)


async def example_two_middleware(request: Request, call_next: CallNext) -> Response:
    request.state.value = request.state.value + "-two"
    return await call_next(request)


async def example_three_middleware(request: Request, call_next: CallNext) -> Response:
    request.state.value = request.state.value + "-three"
    return await call_next(request)


class TestRouteGroup:
    def test_getattr(self, route_group: RouteGroup) -> None:
        @route_group.get("/test")
        @route_group.get("/test/2")
        async def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        route = route_group[0]
        assert isinstance(route, Route)
        assert route.path == "/test/2"

        route = route_group[1]
        assert isinstance(route, Route)
        assert route.path == "/test"

        routes = route_group[:2]
        assert len(routes) == 2

    def test_repr(self, route_group: RouteGroup) -> None:
        @route_group.get("/test")
        async def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        assert repr(route_group) == "<RouteGroup: 1 route>"

    def test_iter(self, route_group: RouteGroup) -> None:
        @route_group.get("/test/{injection}")
        async def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        assert len(route_group) == 1

    def test_common_middleware(self) -> None:
        route_group = RouteGroup(middleware=[example_set_middleware])

        @route_group.get("/")
        async def view(request: Request) -> Response:
            return PlainTextResponse(request.state.value)

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert response.text == "set"

    def test_common_middleware_with_route_middleware(self) -> None:
        route_group = RouteGroup(middleware=[example_set_middleware])

        @route_group.get("/", middleware=[example_two_middleware])
        async def view(request: Request) -> Response:
            return PlainTextResponse(request.state.value)

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert response.text == "set-two"

    def test_app_middleware_only(self) -> None:
        route_group = RouteGroup(middleware=[])

        @route_group.get("/")
        async def view(request: Request) -> Response:
            return PlainTextResponse(request.state.value)

        app = Kupala(secret_key="key!", routes=route_group, middleware=[example_set_middleware])
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert response.text == "set"

    def test_app_route_group_middleware(self) -> None:
        route_group = RouteGroup(middleware=[example_two_middleware])

        @route_group.get("/")
        async def view(request: Request) -> Response:
            return PlainTextResponse(request.state.value)

        app = Kupala(secret_key="key!", routes=route_group, middleware=[example_set_middleware])
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert response.text == "set-two"

    def test_app_route_group_route_middleware(self) -> None:
        route_group = RouteGroup(middleware=[example_two_middleware])

        @route_group.get("/", middleware=[example_three_middleware])
        async def view(request: Request) -> Response:
            return PlainTextResponse(request.state.value)

        app = Kupala(secret_key="key!", routes=route_group, middleware=[example_set_middleware])
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert response.text == "set-two-three"

    def test_children(self) -> None:
        child_group = RouteGroup()

        @child_group.get("/test")
        def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        app = Kupala(secret_key="key!", routes=RouteGroup(children=[child_group]))
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.post("/test").status_code == 405

    def test_children_with_route(self) -> None:
        def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        app = Kupala(
            secret_key="key!",
            routes=RouteGroup(
                children=[
                    Mount(path="/", routes=[Route("/test", view)]),
                ]
            ),
        )
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.post("/test").status_code == 405

    def test_get(self, route_group: RouteGroup) -> None:
        @route_group.get("/test")
        async def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.post("/test").status_code == 405

    def test_get_named(self, route_group: RouteGroup) -> None:
        @route_group.get("/test", name="test")
        async def view(request: Request) -> Response:
            return PlainTextResponse(str(request.url_for("test")))

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.text == "http://testserver/test"

    def test_get_middleware(self, route_group: RouteGroup) -> None:
        @route_group.get("/test", name="test", middleware=[example_set_middleware])
        async def view(request: Request) -> Response:
            return PlainTextResponse(request.scope["state"]["value"])

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.text == "set"

    def test_get_or_post(self, route_group: RouteGroup) -> None:
        @route_group.get_or_post("/test")
        async def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.text == "ok"

            response = client.post("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.put("/test").status_code == 405

    def test_get_or_post_named(self, route_group: RouteGroup) -> None:
        @route_group.get_or_post("/test", name="test")
        async def view(request: Request) -> Response:
            return PlainTextResponse(str(request.url_for("test")))

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.post("/test")
            assert response.text == "http://testserver/test"

    def test_get_or_post_middleware(self, route_group: RouteGroup) -> None:
        @route_group.get_or_post("/test", name="test", middleware=[example_set_middleware])
        async def view(request: Request) -> Response:
            return PlainTextResponse(request.scope["state"]["value"])

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.post("/test")
            assert response.text == "set"

    def test_post_base(self, route_group: RouteGroup) -> None:
        @route_group.post("/test")
        async def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.post("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.get("/test").status_code == 405

    def test_post_named(self, route_group: RouteGroup) -> None:
        @route_group.post("/test", name="test")
        async def view(request: Request) -> Response:
            return PlainTextResponse(str(request.url_for("test")))

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.post("/test")
            assert response.text == "http://testserver/test"

    def test_post_middleware(self, route_group: RouteGroup) -> None:
        @route_group.post("/test", name="test", middleware=[example_set_middleware])
        async def view(request: Request) -> Response:
            return PlainTextResponse(request.scope["state"]["value"])

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.post("/test")
            assert response.text == "set"

    def test_put_base(self, route_group: RouteGroup) -> None:
        @route_group.put("/test")
        async def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.put("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.get("/test").status_code == 405

    def test_put_named(self, route_group: RouteGroup) -> None:
        @route_group.put("/test", name="test")
        async def view(request: Request) -> Response:
            return PlainTextResponse(str(request.url_for("test")))

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.put("/test")
            assert response.text == "http://testserver/test"

    def test_put_middleware(self, route_group: RouteGroup) -> None:
        @route_group.put("/test", name="test", middleware=[example_set_middleware])
        async def view(request: Request) -> Response:
            return PlainTextResponse(request.scope["state"]["value"])

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.put("/test")
            assert response.text == "set"

    def test_patch_base(self, route_group: RouteGroup) -> None:
        @route_group.patch("/test")
        async def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.patch("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.get("/test").status_code == 405

    def test_patch_named(self, route_group: RouteGroup) -> None:
        @route_group.patch("/test", name="test")
        async def view(request: Request) -> Response:
            return PlainTextResponse(str(request.url_for("test")))

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.patch("/test")
            assert response.text == "http://testserver/test"

    def test_patch_middleware(self, route_group: RouteGroup) -> None:
        @route_group.patch("/test", name="test", middleware=[example_set_middleware])
        async def view(request: Request) -> Response:
            return PlainTextResponse(request.scope["state"]["value"])

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.patch("/test")
            assert response.text == "set"

    def test_delete_base(self, route_group: RouteGroup) -> None:
        @route_group.delete("/test")
        async def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.delete("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.get("/test").status_code == 405

    def test_delete_named(self, route_group: RouteGroup) -> None:
        @route_group.delete("/test", name="test")
        async def view(request: Request) -> Response:
            return PlainTextResponse(str(request.url_for("test")))

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.delete("/test")
            assert response.text == "http://testserver/test"

    def test_delete_middleware(self, route_group: RouteGroup) -> None:
        @route_group.delete("/test", name="test", middleware=[example_set_middleware])
        async def view(request: Request) -> Response:
            return PlainTextResponse(request.scope["state"]["value"])

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            response = client.delete("/test")
            assert response.text == "set"

    def test_websocket_base(self, route_group: RouteGroup) -> None:
        @route_group.websocket("/test")
        async def view(websocket: WebSocket) -> None:
            await websocket.accept()
            await websocket.send_text("Hello, websocket!")
            await websocket.close()

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            with client.websocket_connect("/test") as session:
                assert session.receive_text() == "Hello, websocket!"

    def test_websocket_named_route(self, route_group: RouteGroup) -> None:
        @route_group.websocket("/test", name="test")
        async def view(websocket: WebSocket) -> None:
            await websocket.accept()
            await websocket.send_text(str(websocket.url_for("test")))
            await websocket.close()

        app = Kupala(secret_key="key!", routes=route_group)
        with TestClient(app) as client:
            with client.websocket_connect("/test") as session:
                assert session.receive_text() == "ws://testserver/test"


_Injection = typing.Annotated[str, "injected"]


class TestRoute:
    def test_injections(self) -> None:
        async def view(request: Request, injection: _Injection) -> Response:
            return PlainTextResponse(injection)

        app = Kupala(
            secret_key="key!",
            routes=[Route("/test/{injection}", view)],
        )
        with TestClient(app) as client:
            response = client.get("/test/injected")
            assert response.status_code == 200
            assert response.text == "injected"

    def test_injections_with_decorator(self) -> None:
        def view_decorator(fn: AsyncViewCallable) -> AsyncViewCallable:
            @functools.wraps(fn)
            async def inner_view(request: Request, **dependencies: typing.Any) -> Response:
                request.state.value = "fromdecorator"
                return await fn(request, **dependencies)

            return inner_view

        @view_decorator
        async def view(request: Request, injection: _Injection) -> Response:
            return PlainTextResponse(injection + request.state.value)

        app = Kupala(
            secret_key="key!",
            routes=[
                Route("/test/{injection}", view),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/test/injected")
            assert response.status_code == 200
            assert response.text == "injectedfromdecorator"

    def test_injections_with_multiple_routes_on_same_view(self) -> None:
        async def view(request: Request, injection: _Injection) -> Response:
            return PlainTextResponse(injection)

        app = Kupala(
            secret_key="key!",
            routes=[
                Route("/test/{injection}", view),
                Route("/test/2/{injection}", view),
            ],
        )
        with TestClient(app) as client:
            assert client.get("/test/injected").text == "injected"
            assert client.get("/test/2/injected").text == "injected"

    def test_route_dependency_injects_request(self) -> None:
        def dependency(request: Request) -> str:
            return request.url.path

        RequestDep = typing.Annotated[str, FactoryResolver(dependency)]

        async def view(dep: RequestDep) -> Response:
            return PlainTextResponse(dep)

        app = Kupala(
            secret_key="key!",
            routes=[
                Route("/", view),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert response.text == "/"

    def test_norequest_handler(self) -> None:
        async def view() -> Response:
            return PlainTextResponse("ok")

        app = Kupala(
            secret_key="key!",
            routes=[
                Route("/test", view),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.post("/test").status_code == 405

    def test_handler_with_decorator(self) -> None:
        def decorator(fn: AsyncViewCallable) -> AsyncViewCallable:
            @functools.wraps(fn)
            async def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
                return await fn(*args, **kwargs)

            return inner

        @decorator
        async def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        app = Kupala(
            secret_key="key!",
            routes=[
                Route("/test", view),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.post("/test").status_code == 405

    def test_async_handler(self) -> None:
        async def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        app = Kupala(
            secret_key="key!",
            routes=[
                Route("/test", view),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.post("/test").status_code == 405

    def test_sync_handler(self) -> None:
        def view(request: Request) -> Response:
            return PlainTextResponse("ok")

        app = Kupala(
            secret_key="key!",
            routes=[
                Route("/test", view),
            ],
        )
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.text == "ok"

        assert client.post("/test").status_code == 405

    def test_app_body_size_limit(self) -> None:
        async def view(request: Request) -> Response:
            return PlainTextResponse(await request.json())

        app = Kupala(
            secret_key="key!",
            routes=[
                Route("/test", view, methods=["POST"]),
            ],
            max_body_size=1,
        )
        with TestClient(app) as client:
            response = client.post("/test", json={"content": "a"})
            assert response.status_code == 413

    def test_route_body_size_limit(self) -> None:
        async def view(request: Request) -> Response:
            return JSONResponse(await request.json())

        app = Kupala(
            secret_key="key!",
            routes=[
                Route("/test", view, methods=["POST"], max_request_size=1),
            ],
        )
        with TestClient(app) as client:
            response = client.post("/test", json={"content": "a"})
            assert response.status_code == 413

    def test_route_increase_body_size_limit(self) -> None:
        async def view(request: Request) -> Response:
            return JSONResponse(await request.json())

        app = Kupala(
            secret_key="key!",
            max_body_size=1,
            routes=[
                Route("/test", view, methods=["POST"], max_request_size=1000000),
            ],
        )
        with TestClient(app) as client:
            response = client.post("/test", json={"content": "a"})
            assert response.status_code == 200

    def test_route_decrease_body_size_limit(self) -> None:
        async def view(request: Request) -> Response:
            return JSONResponse(await request.json())

        app = Kupala(
            secret_key="key!",
            max_body_size=1000000,
            routes=[
                Route("/test", view, methods=["POST"], max_request_size=1),
            ],
        )
        with TestClient(app) as client:
            response = client.post("/test", json={"content": "a"})
            assert response.status_code == 413

    def test_app_request_timeout(self) -> None:
        async def view(request: Request) -> Response:
            await anyio.sleep(0.002)
            return PlainTextResponse(await request.json())

        app = Kupala(
            secret_key="key!",
            routes=[
                Route("/test", view, methods=["POST"]),
            ],
            request_timeout=0.001,
        )
        with TestClient(app) as client:
            response = client.post("/test", json={"content": "a"})
            assert response.status_code == 504

    def test_route_request_timeout(self) -> None:
        async def view(request: Request) -> Response:
            await anyio.sleep(0.002)
            return JSONResponse(await request.json())

        app = Kupala(
            secret_key="key!",
            routes=[
                Route("/test", view, methods=["POST"], request_timeout=0.001),
            ],
        )
        with TestClient(app) as client:
            response = client.post("/test", json={"content": "a"})
            assert response.status_code == 504

    def test_route_increase_request_timeout(self) -> None:
        async def view(request: Request) -> Response:
            await anyio.sleep(0.002)
            return JSONResponse(await request.json())

        app = Kupala(
            secret_key="key!",
            request_timeout=0.001,
            routes=[
                Route("/test", view, methods=["POST"], request_timeout=0.005),
            ],
        )
        with TestClient(app) as client:
            response = client.post("/test", json={"content": "a"})
            assert response.status_code == 200

    def test_route_decrease_request_timeout(self) -> None:
        async def view(request: Request) -> Response:
            await anyio.sleep(0.002)
            return JSONResponse(await request.json())

        app = Kupala(
            secret_key="key!",
            request_timeout=0.1,
            routes=[
                Route("/test", view, methods=["POST"], request_timeout=0.001),
            ],
        )
        with TestClient(app) as client:
            response = client.post("/test", json={"content": "a"})
            assert response.status_code == 504


class TestWebSocketRoute:
    def test_websocket_dependency_injects_websocket(self) -> None:
        def dependency(websocket: WebSocket) -> str:
            return websocket.url.path

        RequestDep = typing.Annotated[str, FactoryResolver(dependency)]

        async def view(websocket: WebSocket, dep: RequestDep) -> None:
            await websocket.accept()
            await websocket.send_text(dep)
            await websocket.close()

        app = Kupala(
            secret_key="key!",
            routes=[
                WebSocketRoute("/test", view),
            ],
        )
        with TestClient(app) as client:
            with client.websocket_connect("/test") as session:
                assert session.receive_text() == "/test"

    def test_handler_with_decorator(self) -> None:
        def decorator(fn: WebSocketViewCallable) -> WebSocketViewCallable:
            @functools.wraps(fn)
            async def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
                return await fn(*args, **kwargs)

            return inner

        @decorator
        async def view(websocket: WebSocket) -> None:
            await websocket.accept()
            await websocket.send_text("ok")
            await websocket.close()

        app = Kupala(
            secret_key="key!",
            routes=[
                WebSocketRoute("/test", view),
            ],
        )
        with TestClient(app) as client:
            with client.websocket_connect("/test") as session:
                assert session.receive_text() == "ok"


async def view(request: Request) -> Response:
    return PlainTextResponse("ok")


class TestURLHelpers:
    def test_url_matches(self) -> None:
        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/test",
                "headers": [(b"host", b"testserver")],
                "router": Router([Route("/test", view)]),
            }
        )
        assert url_matches(request, "/test")
        assert not url_matches(request, "/nottests")

    def test_route_matches(self) -> None:
        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/test",
                "headers": [(b"host", b"testserver")],
                "router": Router(
                    [
                        Route("/test", view, name="test"),
                        Route("/test/{param}", view, name="test-param"),
                    ]
                ),
            }
        )
        assert route_matches(request, "test")
        assert not route_matches(request, "test-param", {"param": "value"})

    def test_route_matches_with_params(self) -> None:
        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/test/value",
                "headers": [(b"host", b"testserver")],
                "router": Router(
                    [
                        Route("/test", view, name="test"),
                        Route("/test/{param}", view, name="test-param"),
                    ]
                ),
            }
        )
        assert route_matches(request, "test-param", {"param": "value"})
        assert not route_matches(request, "test-param", {"param": "value2"})

    def test_abs_url_for(self) -> None:
        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/test",
                "headers": [(b"host", b"testserver")],
                "router": Router([Route("/test", view, name="test")]),
            }
        )
        assert abs_url_for(request, "test") == "http://testserver/test"
