from __future__ import annotations

import contextlib
import contextvars
import functools
import inspect
import typing

import anyio
import click
from starlette.applications import Starlette
from starlette.datastructures import URLPath
from starlette.middleware import Middleware as ASGIMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.routing import BaseRoute
from starlette.types import ExceptionHandler, Receive, Scope, Send

from kupala.dependencies import Dependencies
from kupala.routing import Middleware


class Extension(typing.Protocol):
    def configure(self, app: Kupala) -> None: ...


type Initializer = typing.Callable[[Kupala], typing.AsyncContextManager[None]]


@contextlib.asynccontextmanager
async def _starlette_lifespan_adapter(_: Starlette, kupala: Kupala) -> typing.AsyncGenerator[None, None]:
    async with kupala.initialize():
        yield None


class Kupala:
    _current_app: contextvars.ContextVar[Kupala] = contextvars.ContextVar("kupala_app")

    def __init__(
        self,
        secret_key: str,
        *,
        debug: bool = False,
        middleware: typing.Sequence[Middleware] = (),
        asgi_middleware: typing.Sequence[ASGIMiddleware] = (),
        routes: typing.Sequence[BaseRoute] = (),
        initializers: typing.Sequence[Initializer] = (),
        extensions: typing.Sequence[Extension] = (),
        commands: typing.Sequence[click.Command] = (),
        dependencies: Dependencies | None = None,
        exception_handlers: typing.Mapping[typing.Any, ExceptionHandler] | None = None,
        max_body_size: int = 20 * 1024 * 1024,
        request_timeout: float = 30,
        trusted_hosts: typing.Sequence[str] = ("localhost", "127.0.0.1", "testserver"),
        compress_response: bool = False,
    ) -> None:
        self.debug = debug
        self.commands = list(commands)
        self.secret_key = secret_key
        self.middleware = middleware
        self.initializers = list(initializers)
        self.asgi_middleware = list(asgi_middleware)
        self.state: dict[typing.Hashable, typing.Any] = {}
        self.dependencies = dependencies or Dependencies()
        self.max_body_size = max_body_size
        self.request_timeout = request_timeout
        self.routes: list[BaseRoute] = list(routes)

        # setup trusted hosts
        if trusted_hosts:
            self.asgi_middleware.append(ASGIMiddleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts))

        if compress_response:
            self.asgi_middleware.append(ASGIMiddleware(GZipMiddleware))

        for extension in extensions:
            extension.configure(self)

        self._app = Starlette(
            debug=debug,
            routes=self.routes,
            middleware=self.asgi_middleware,
            lifespan=functools.partial(_starlette_lifespan_adapter, kupala=self),
            exception_handlers=exception_handlers or {},
        )

    @classmethod
    def current(cls) -> Kupala | None:
        try:
            return cls._current_app.get()
        except LookupError:
            return None

    def url_path_for(self, name: str, /, **path_params: typing.Any) -> URLPath:
        return self._app.router.url_path_for(name, **path_params)

    @contextlib.asynccontextmanager
    async def initialize(self) -> typing.AsyncGenerator[dict[str, typing.Any], None]:
        old_app = self._current_app.set(self)
        async with contextlib.AsyncExitStack() as stack:
            for initializer in self.initializers:
                await stack.enter_async_context(initializer(self))

            yield {}
            self._current_app.reset(old_app)

    def cli_plugin(self, app: click.Group) -> None:
        """Install this application as Kupala CLI plugin."""

        for command in self.commands:
            app.add_command(command)

    def run_cli(self, *args: str) -> None:
        """Run CLI application."""

        @click.group()
        @click.pass_context
        def cli(ctx: click.Context) -> None:
            ctx.obj = self

        self.cli_plugin(cli)

        async def main() -> None:
            async with self.initialize():
                try:
                    rv = cli(standalone_mode=False, args=args)
                    if inspect.iscoroutine(rv):
                        await rv
                except click.ClickException as exc:
                    click.secho("error: " + str(exc), err=True, fg="red")
                    raise SystemExit(exc.exit_code)

        anyio.run(main)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        scope["app"] = self

        if self._app.middleware_stack is None:
            self._app.middleware_stack = self._app.build_middleware_stack()

        await self._app.middleware_stack(scope, receive, send)
