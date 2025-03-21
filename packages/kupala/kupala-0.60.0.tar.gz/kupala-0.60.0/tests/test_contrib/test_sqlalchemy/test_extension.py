from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response
from starlette.testclient import TestClient

from kupala import Kupala
from kupala.contrib.sqlalchemy.extension import DbSession, SQLAlchemy
from kupala.contrib.sqlalchemy.manager import Database
from kupala.routing import Route


async def inject_async_session_view(dbsession: AsyncSession) -> Response:
    return Response(dbsession.__class__.__name__)


async def inject_db_session_view(dbsession: DbSession) -> Response:
    return Response(dbsession.__class__.__name__)


def test_provides_async_session_dependency() -> None:
    app = Kupala(
        secret_key="key!",
        routes=[
            Route("/", inject_async_session_view),
        ],
        extensions=[
            SQLAlchemy(
                {
                    "default": Database("sqlite+aiosqlite:///:memory:"),
                }
            )
        ],
    )
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "AsyncSession"


def test_provides_dbsession_dependency() -> None:
    app = Kupala(
        secret_key="key!",
        routes=[
            Route("/", inject_db_session_view),
        ],
        extensions=[
            SQLAlchemy(
                {
                    "default": Database("sqlite+aiosqlite:///:memory:"),
                }
            )
        ],
    )
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "AsyncSession"
