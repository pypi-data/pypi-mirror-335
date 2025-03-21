import contextlib
import contextvars
import typing

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)


class NoActiveSession(Exception): ...


EngineOptions = dict[str, typing.Any]
SessionOptions = dict[str, typing.Any]


class Database:
    def __init__(
        self,
        url: str,
        *,
        echo: bool = False,
        session_class: type[AsyncSession] = AsyncSession,
        engine_options: EngineOptions | None = None,
        session_options: SessionOptions | None = None,
    ) -> None:
        self._engine = create_async_engine(
            url=url,
            echo=echo,
            **(engine_options or {}),
        )

        _session_options: dict[str, typing.Any] = {"expire_on_commit": False, "class_": session_class}
        _session_options.update(session_options or {})
        self._sessionmaker = async_sessionmaker(bind=self._engine, **_session_options)
        self._current_session: contextvars.ContextVar[AsyncSession] = contextvars.ContextVar("sqla_current_session")

    async def __aenter__(self) -> AsyncEngine:
        return self._engine

    async def __aexit__(self, *exc: typing.Any) -> None:
        pass

    @property
    def current_session(self) -> AsyncSession | None:
        """Return the currently active session if it exists.
        Prefer not to use this method, only for debugging and special purposes.
        Raises ValueError if no session is active."""
        try:
            return self._current_session.get()
        except LookupError:
            raise NoActiveSession("No SQLAlchemy session is currently active.")

    @contextlib.asynccontextmanager
    async def session(self, force_rollback: bool = False) -> typing.AsyncGenerator[AsyncSession, None]:
        """Get a new session instance.
        If force_rollback is True, the session will be rolled back after exiting the context."""

        factory: typing.Callable[[], typing.AsyncContextManager[AsyncSession]] = self._start_normal_session
        if force_rollback:
            factory = self._start_rollback_session

        async with factory() as session:
            restore_token = self._current_session.set(session)
            try:
                yield session
            finally:
                self._current_session.reset(restore_token)

    @contextlib.asynccontextmanager
    async def _start_normal_session(self, **kwargs: typing.Any) -> typing.AsyncGenerator[AsyncSession, None]:
        async with self._sessionmaker(**kwargs) as session:
            yield session

    @contextlib.asynccontextmanager
    async def _start_rollback_session(self) -> typing.AsyncGenerator[AsyncSession, None]:
        """Create a new session that will be rolled back after exiting the context.
        For testing purposes. Any BEGIN/COMMIT/ROLLBACK ops are executed in SAVEPOINT.
        See https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites"""
        async with self._engine.connect() as conn:
            async with conn.begin() as tx:
                async with self._start_normal_session(bind=conn, join_transaction_mode="create_savepoint") as session:
                    try:
                        yield session
                    finally:
                        await tx.rollback()
