import dataclasses

from starlette.authentication import BaseUser
from starlette.requests import HTTPConnection

from kupala import Kupala
from kupala.authentication import (
    Authenticator,
    AuthenticatorBackend,
    ChainAuthenticator,
    Identity,
    make_session_auth_hash,
    SESSION_HASH_KEY,
    SESSION_IDENTITY_KEY,
    SessionAuthenticator,
    update_session_auth_hash,
    WithScopes,
    WithSessionAuthHash,
)


@dataclasses.dataclass
class User(BaseUser):
    username: str

    @property
    def identity(self) -> str:
        return self.username

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:  # pragma: no cover
        return self.username


@dataclasses.dataclass
class UserWithSessionHash(User, WithSessionAuthHash):
    password: str

    def get_password_hash(self) -> str:
        return self.password


@dataclasses.dataclass
class UserWithScopes(User, WithScopes):
    def get_scopes(self) -> list[str]:
        return ["admin"]


class UserLoader:
    def __init__(self, users: list[User]) -> None:
        self.users: dict[str, User] = {user.identity: user for user in users}

    async def __call__(self, conn: HTTPConnection, user_id: str) -> BaseUser | None:
        return self.users.get(user_id)


class _DummyAuthenticator(Authenticator):
    def __init__(self, user: BaseUser | None) -> None:
        self.user = user

    async def authenticate(self, conn: HTTPConnection) -> Identity | None:
        if self.user:
            return Identity(
                id=self.user.identity,
                user=self.user,
                scopes=[],
                authenticator=type(self),
            )
        return None


class TestSessionAuthenticator:
    async def test_authenticates(self) -> None:
        user = User("root")
        user_loader = UserLoader([user])

        conn = HTTPConnection(
            {
                "type": "http",
                "app": Kupala(secret_key="key!"),
                "session": {SESSION_IDENTITY_KEY: "root"},
            }
        )
        authenticator = SessionAuthenticator(user_loader=user_loader)
        identity = await authenticator.authenticate(conn)
        assert identity
        assert identity.id == "root"

    async def test_not_authenticated(self) -> None:
        user = User("root")
        user_loader = UserLoader([user])

        conn = HTTPConnection(
            {
                "type": "http",
                "app": Kupala(secret_key="key!"),
                "session": {},
            }
        )
        authenticator = SessionAuthenticator(user_loader=user_loader)
        assert not await authenticator.authenticate(conn)

    async def test_no_user(self) -> None:
        user = User("test")
        user_loader = UserLoader([user])

        conn = HTTPConnection(
            {
                "type": "http",
                "app": Kupala(secret_key="key!"),
                "session": {SESSION_IDENTITY_KEY: "root"},
            }
        )
        authenticator = SessionAuthenticator(user_loader=user_loader)
        assert not await authenticator.authenticate(conn)

    async def test_extracts_user_scopes(self) -> None:
        user_loader = UserLoader([UserWithScopes("root")])

        authenticator = SessionAuthenticator(user_loader=user_loader)
        conn = HTTPConnection(
            {
                "type": "http",
                "app": Kupala(secret_key="key!"),
                "session": {SESSION_IDENTITY_KEY: "root"},
            }
        )
        identity = await authenticator.authenticate(conn)
        assert identity
        assert identity.scopes == ["admin"]

    async def test_validates_session_hash(self) -> None:
        user = UserWithSessionHash(username="root", password="password")
        user_loader = UserLoader([user])

        authenticator = SessionAuthenticator(user_loader=user_loader)
        conn = HTTPConnection(
            {
                "type": "http",
                "app": Kupala(secret_key="key!"),
                "session": {
                    SESSION_IDENTITY_KEY: "root",
                    SESSION_HASH_KEY: make_session_auth_hash(user, "key!"),
                },
            }
        )
        assert await authenticator.authenticate(conn)

    async def test_validates_invalid_session_hash(self) -> None:
        user = UserWithSessionHash(username="root", password="password")
        user_loader = UserLoader([user])

        authenticator = SessionAuthenticator(user_loader=user_loader)
        conn = HTTPConnection(
            {
                "type": "http",
                "app": Kupala(secret_key="key!"),
                "session": {
                    SESSION_IDENTITY_KEY: "root",
                    SESSION_HASH_KEY: "bad hash",
                },
            }
        )
        assert not await authenticator.authenticate(conn)

    async def test_update_session_hash(self) -> None:
        user = UserWithSessionHash(username="root", password="password")
        user_loader = UserLoader([user])

        authenticator = SessionAuthenticator(user_loader=user_loader)
        conn = HTTPConnection(
            {
                "type": "http",
                "app": Kupala(secret_key="key!"),
                "session": {
                    SESSION_IDENTITY_KEY: "root",
                    SESSION_HASH_KEY: "bad hash",
                },
            }
        )
        assert not await authenticator.authenticate(conn)

        update_session_auth_hash(conn, user, "key!")
        assert await authenticator.authenticate(conn)


class TestChainAuthenticator:
    async def test_authenticates(self) -> None:
        user = User("root")
        authenticator = ChainAuthenticator(
            _DummyAuthenticator(None),
            _DummyAuthenticator(user),
        )
        conn = HTTPConnection({"type": "http"})
        assert await authenticator.authenticate(conn)

    async def test_not_authenticates(self) -> None:
        backend = ChainAuthenticator(
            _DummyAuthenticator(None),
            _DummyAuthenticator(None),
        )
        conn = HTTPConnection({"type": "http"})
        assert not await backend.authenticate(conn)


class TestAuthenticatorBackend:
    async def test_authenticates(self) -> None:
        user = User("root")
        backend = AuthenticatorBackend(_DummyAuthenticator(user))
        result = await backend.authenticate(HTTPConnection({"type": "http"}))
        assert result
        credentials, authenticated_user = result
        assert credentials.scopes == []
        assert authenticated_user.identity == "root"

    async def test_not_authenticates(self) -> None:
        backend = AuthenticatorBackend(_DummyAuthenticator(None))
        assert not await backend.authenticate(HTTPConnection({"type": "http"}))


class TestPasswordHasher:
    pass


class TestAuthentication:
    pass
