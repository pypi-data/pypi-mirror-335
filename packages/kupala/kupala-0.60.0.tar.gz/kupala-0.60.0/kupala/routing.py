from __future__ import annotations

import functools
import inspect
import typing

from starlette.concurrency import run_in_threadpool
from starlette.datastructures import URL
from starlette.middleware import Middleware as ASGIMiddleware
from starlette.requests import HTTPConnection, Request
from starlette.responses import Response
from starlette.routing import BaseRoute, Route as Route_, WebSocketRoute as WebSocketRoute_
from starlette.websockets import WebSocket

from kupala.asgi.request_limit import RequestBodyLimitMiddleware
from kupala.asgi.request_timeout import RequestTimeoutMiddleware
from kupala.dependencies import create_dependency_specs, Dependencies, VariableResolver

AsyncViewCallable = typing.Callable[..., typing.Awaitable[Response]]
SyncViewCallable = typing.Callable[..., Response]
AnyViewCallable = AsyncViewCallable | SyncViewCallable
WebSocketViewCallable = typing.Callable[[WebSocket], typing.Awaitable[None]]
HttpMethod = str

_PS = typing.ParamSpec("_PS")
_RT = typing.TypeVar("_RT")

type CallNext = typing.Callable[[Request], typing.Awaitable[Response]]
type Middleware = typing.Callable[[Request, CallNext], typing.Awaitable[Response]]


def unwrap_callable(fn: AnyViewCallable) -> AnyViewCallable:
    return fn if not hasattr(fn, "__wrapped__") else unwrap_callable(fn.__wrapped__)


def unwrap_websocket_callable(
    fn: typing.Callable[..., typing.Awaitable[None]],
) -> typing.Callable[..., typing.Awaitable[None]]:
    callback = fn if not hasattr(fn, "__wrapped__") else unwrap_callable(fn.__wrapped__)
    return typing.cast(typing.Callable[..., typing.Awaitable[None]], callback)


def wrap_with_middleware(fn: AsyncViewCallable, middleware: typing.Sequence[Middleware]) -> AsyncViewCallable:
    async def call_next(request_: Request) -> Response:
        return await fn(request_)

    async def middleware_adapter(middleware: Middleware, call_next_: CallNext, request_: Request) -> Response:
        return await middleware(request_, call_next_)

    for middleware_ in reversed(middleware):
        call_next = functools.partial(middleware_adapter, middleware_, call_next)
    return call_next


def get_view_metadata(view_callable: AnyViewCallable) -> dict[str, typing.Any]:
    return getattr(view_callable, "__metadata__", {})


class Route(Route_):
    def __init__(
        self,
        path: str,
        endpoint: typing.Callable[..., typing.Any],
        *,
        methods: list[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        middleware: typing.Sequence[Middleware] = (),
        metadata: dict[str, typing.Any] | None = None,
        max_request_size: int | None = None,
        request_timeout: float | None = None,
    ) -> None:
        setattr(endpoint, "__metadata__", metadata or {})
        self.middleware = [*middleware]

        super().__init__(
            path,
            name=name,
            methods=methods,
            include_in_schema=include_in_schema,
            endpoint=self._build_endpoint(endpoint),
            middleware=[
                ASGIMiddleware(RequestBodyLimitMiddleware, max_body_size=max_request_size),
                ASGIMiddleware(RequestTimeoutMiddleware, timeout=request_timeout),
            ],
        )

    def _build_endpoint(self, view_callable: typing.Callable[..., typing.Any]) -> AsyncViewCallable:
        # find the original view callable in order to parse the dependencies
        actual_view_callable = unwrap_callable(view_callable)
        dependencies = create_dependency_specs(actual_view_callable)

        async def endpoint(request: Request) -> Response:
            async def wrapped_endpoint(request: Request) -> Response:
                nonlocal view_callable
                resolver = Dependencies(
                    parent=request.app.dependencies,
                    dependencies={
                        Request: VariableResolver(request),
                        HTTPConnection: VariableResolver(request),
                    },
                )
                if inspect.iscoroutinefunction(view_callable) is False:
                    view_callable = functools.partial(run_in_threadpool, view_callable)

                return await resolver.call_with(view_callable, dependencies)

            wrapped = wrap_with_middleware(wrapped_endpoint, [*request.app.middleware, *self.middleware])
            return await wrapped(request)

        return endpoint


class WebSocketRoute(WebSocketRoute_):
    def __init__(
        self,
        path: str,
        endpoint: typing.Callable[..., typing.Any],
        *,
        name: str | None = None,
        metadata: dict[str, typing.Any] | None = None,
    ) -> None:
        self.metadata = metadata or {}
        super().__init__(
            path=path,
            endpoint=self._build_endpoint(endpoint),
            name=name,
        )

    def _build_endpoint(self, view_callable: typing.Callable[..., typing.Any]) -> AsyncViewCallable:
        # find the original view callable in order to parse the dependencies
        actual_view_callable = unwrap_websocket_callable(view_callable)
        dependencies = create_dependency_specs(actual_view_callable)

        async def endpoint(websocket: WebSocket) -> Response:
            nonlocal view_callable
            resolver = Dependencies(
                parent=websocket.app.dependencies,
                dependencies={
                    WebSocket: VariableResolver(websocket),
                    HTTPConnection: VariableResolver(websocket),
                },
            )

            return await resolver.call_with(view_callable, dependencies)

        return endpoint


class RouteGroup(typing.Sequence[BaseRoute]):
    def __init__(
        self,
        prefix: str | None = None,
        middleware: typing.Sequence[Middleware] = (),
        children: typing.Sequence[RouteGroup | BaseRoute] | None = None,
    ) -> None:
        self.prefix = prefix or ""
        self.routes: list[BaseRoute] = []
        self._group_middleware = list(middleware or [])

        for child in children or []:
            if isinstance(child, RouteGroup):
                self.routes.extend(child)
            else:
                self.routes.append(child)

    def add(
        self,
        path: str,
        *,
        methods: list[HttpMethod] | None = None,
        name: str | None = None,
        middleware: typing.Sequence[Middleware] = (),
        metadata: dict[str, typing.Any] | None = None,
    ) -> typing.Callable[[AnyViewCallable], AnyViewCallable]:
        path = self.prefix.removesuffix("/") + path if self.prefix else path

        def decorator(view_callable: AnyViewCallable) -> AnyViewCallable:
            self.routes.append(
                Route(
                    path,
                    view_callable,
                    name=name,
                    methods=methods,
                    metadata=metadata,
                    middleware=(*self._group_middleware, *middleware),
                )
            )
            return view_callable

        return decorator

    def get(
        self, path: str, *, name: str | None = None, middleware: typing.Sequence[Middleware] = ()
    ) -> typing.Callable[[AnyViewCallable], AnyViewCallable]:
        return self.add(path, methods=["GET"], name=name, middleware=middleware)

    def post(
        self, path: str, *, name: str | None = None, middleware: typing.Sequence[Middleware] = ()
    ) -> typing.Callable[[AnyViewCallable], AnyViewCallable]:
        return self.add(path, methods=["POST"], name=name, middleware=middleware)

    def get_or_post(
        self, path: str, *, name: str | None = None, middleware: typing.Sequence[Middleware] = ()
    ) -> typing.Callable[[AnyViewCallable], AnyViewCallable]:
        return self.add(path, methods=["GET", "POST"], name=name, middleware=middleware)

    def put(
        self, path: str, *, name: str | None = None, middleware: typing.Sequence[Middleware] = ()
    ) -> typing.Callable[[AnyViewCallable], AnyViewCallable]:
        return self.add(path, methods=["PUT"], name=name, middleware=middleware)

    def patch(
        self, path: str, *, name: str | None = None, middleware: typing.Sequence[Middleware] = ()
    ) -> typing.Callable[[AnyViewCallable], AnyViewCallable]:
        return self.add(path, methods=["PATCH"], name=name, middleware=middleware)

    def delete(
        self, path: str, *, name: str | None = None, middleware: typing.Sequence[Middleware] = ()
    ) -> typing.Callable[[AnyViewCallable], AnyViewCallable]:
        return self.add(path, methods=["DELETE"], name=name, middleware=middleware)

    def websocket(
        self, path: str, *, name: str | None = None
    ) -> typing.Callable[[typing.Callable[_PS, typing.Awaitable[None]]], typing.Callable[_PS, typing.Awaitable[None]]]:
        path = self.prefix.removesuffix("/") + path if self.prefix else path

        def decorator(
            view_callable: typing.Callable[_PS, typing.Awaitable[None]],
        ) -> typing.Callable[_PS, typing.Awaitable[None]]:
            self.routes.append(
                WebSocketRoute(
                    path,
                    view_callable,
                    name=name,
                )
            )
            return view_callable

        return decorator

    def __iter__(self) -> typing.Iterator[BaseRoute]:
        return iter(self.routes)

    def __len__(self) -> int:
        return len(self.routes)

    def __repr__(self) -> str:
        routes_count = len(self.routes)
        noun = "route" if routes_count == 1 else "routes"
        return f"<{self.__class__.__name__}: {routes_count} {noun}>"

    @typing.overload
    def __getitem__(self, index: int) -> BaseRoute:  # pragma: no cover
        ...

    @typing.overload
    def __getitem__(self, index: slice) -> typing.Sequence[BaseRoute]:  # pragma: no cover
        ...

    def __getitem__(self, index: int | slice) -> BaseRoute | typing.Sequence[BaseRoute]:
        return self.routes[index]


def url_matches(request: Request, pattern: URL | str) -> bool:
    """Return True if request URL matches URL."""
    value = URL(str(pattern))
    print(request.url.path.removesuffix("/"), value.path.removesuffix("/"))
    return request.url.path.removesuffix("/").startswith(value.path.removesuffix("/"))


def route_matches(request: Request, pathname: str, path_params: dict[str, typing.Any] | None = None) -> bool:
    url = request.url_for(pathname, **(path_params or {}))
    return url_matches(request, url)


def abs_url_for(request: Request, name: str, **path_params: typing.Any) -> URL:
    """Return absolute URL for route."""
    return request.url_for(name, **path_params)
