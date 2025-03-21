import contextlib
import typing

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware import Middleware

from kupala.applications import Kupala
from kupala.contrib.sqlalchemy.manager import Database
from kupala.contrib.sqlalchemy.middleware import DbSessionMiddleware
from kupala.dependencies import RequestResolver

type DbSession = typing.Annotated[AsyncSession, RequestResolver(lambda r: r.state.dbsession)]


class SQLAlchemy:
    def __init__(self, databases: dict[str, Database]) -> None:
        self._databases = databases

    @contextlib.asynccontextmanager
    async def initialize(self, _: Kupala) -> typing.AsyncGenerator[None, None]:
        async with contextlib.AsyncExitStack() as stack:
            for database in self._databases.values():
                await stack.enter_async_context(database)
            yield

    def configure(self, app: Kupala) -> None:
        app.initializers.append(self.initialize)
        app.dependencies.registry[AsyncSession] = RequestResolver(lambda r: r.state.dbsession)
        app.asgi_middleware.insert(0, Middleware(DbSessionMiddleware, self._databases))
