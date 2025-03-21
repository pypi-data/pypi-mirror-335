import anyio
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class RequestTimeoutMiddleware:
    def __init__(self, app: ASGIApp, timeout: float = 30) -> None:
        """Limit the request processing time."""
        self.app = app
        self.timeout = timeout

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            timeout = self.timeout or scope["app"].request_timeout
            with anyio.fail_after(timeout):
                await self.app(scope, receive, send)
        except TimeoutError:
            response = PlainTextResponse("Gateway Timeout", status_code=504)
            await response(scope, receive, send)
