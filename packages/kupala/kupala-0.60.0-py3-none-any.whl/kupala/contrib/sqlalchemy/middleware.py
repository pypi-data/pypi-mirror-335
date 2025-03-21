from __future__ import annotations

import contextlib

from starlette.types import ASGIApp, Receive, Scope, Send

from kupala.contrib.sqlalchemy.manager import Database


class DbSessionMiddleware:
    def __init__(self, app: ASGIApp, databases: dict[str, Database]) -> None:
        self.app = app
        self.databases = databases

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        scope.setdefault("state", {})
        async with contextlib.AsyncExitStack() as stack:
            for name, database in self.databases.items():
                dbsession = await stack.enter_async_context(database.session())
                if name == "default":
                    scope["state"]["dbsession"] = dbsession
                scope["state"][f"dbsession_{name}"] = dbsession

                await self.app(scope, receive, send)
