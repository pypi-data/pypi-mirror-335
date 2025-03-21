from __future__ import annotations

import abc
import dataclasses
import hashlib
import hmac
import typing

import click
from starlette.authentication import AuthCredentials, AuthenticationBackend, BaseUser
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection

from kupala import Kupala
from kupala.dependencies import VariableResolver
from kupala.passwords import PasswordHasher

type ByIDLoader = typing.Callable[[HTTPConnection, str], typing.Awaitable[BaseUser | None]]
type ByUserNameLoader = typing.Callable[[HTTPConnection, str], typing.Awaitable[BaseUser | None]]
type ByAPITokenLoader = typing.Callable[[HTTPConnection, str], typing.Awaitable[BaseUser | None]]

SESSION_IDENTITY_KEY = "kupala.identity"
SESSION_HASH_KEY = "kupala.identity_hash"

_U = typing.TypeVar("_U", bound=BaseUser, default=BaseUser)


@dataclasses.dataclass
class Identity(typing.Generic[_U]):
    id: str
    user: _U
    scopes: typing.Sequence[str]
    authenticator: type[Authenticator]


class WithSessionAuthHash:  # pragma: no cover
    def get_password_hash(self) -> str:
        raise NotImplementedError


class WithScopes:
    def get_scopes(self) -> list[str]:
        return []


def make_session_auth_hash(user: WithSessionAuthHash, secret_key: str) -> str:
    """Compute current user session auth hash."""
    key = hashlib.sha256(("kupala.auth." + secret_key).encode()).digest()
    return hmac.new(key, msg=user.get_password_hash().encode(), digestmod=hashlib.sha256).hexdigest()


def update_session_auth_hash(connection: HTTPConnection, user: WithSessionAuthHash, secret_key: str) -> None:
    """Update session auth hash.
    Call this function each time you change user's password.
    Otherwise, the session will be instantly invalidated."""
    connection.session[SESSION_HASH_KEY] = make_session_auth_hash(user, secret_key)


def validate_session_auth_hash(connection: HTTPConnection, session_auth_hash: str) -> bool:
    """Validate session auth hash."""
    return hmac.compare_digest(connection.session.get(SESSION_HASH_KEY, ""), session_auth_hash)


class Authenticator(abc.ABC):
    """Base class for authenticators."""

    @abc.abstractmethod
    async def authenticate(self, conn: HTTPConnection) -> Identity | None:
        raise NotImplementedError


class SessionAuthenticator(Authenticator):
    """Authenticate user using session."""

    def __init__(self, user_loader: ByIDLoader) -> None:
        self.user_loader = user_loader

    async def authenticate(self, conn: HTTPConnection) -> Identity | None:
        user_id: str = conn.session.get(SESSION_IDENTITY_KEY, "")
        if not user_id:
            return None

        user = await self.user_loader(conn, user_id)
        if not user:
            return None

        scopes = []
        if isinstance(user, WithSessionAuthHash):
            # avoid authentication if session hash is invalid
            # this may happen when user changes password OR session is hijacked
            secret_key = conn.app.secret_key
            if not validate_session_auth_hash(conn, make_session_auth_hash(user, secret_key)):
                return None

        if isinstance(user, WithScopes):
            scopes = user.get_scopes()

        return Identity(id=user.identity, user=user, scopes=scopes, authenticator=self.__class__)


class ChainAuthenticator(Authenticator):
    """Authenticate user using multiple authenticators."""

    def __init__(self, *authenticators: Authenticator) -> None:
        self.authenticators = authenticators

    async def authenticate(self, conn: HTTPConnection) -> Identity | None:
        for authenticator in self.authenticators:
            if identity := await authenticator.authenticate(conn):
                return identity
        return None


class AuthenticatorBackend(AuthenticationBackend):
    """Integrates authenticators with Starlette's authentication middleware."""

    def __init__(self, authenticator: Authenticator) -> None:
        self.authenticator = authenticator

    async def authenticate(self, conn: HTTPConnection) -> tuple[AuthCredentials, BaseUser] | None:
        if identity := await self.authenticator.authenticate(conn):
            return AuthCredentials(scopes=identity.scopes), identity.user
        return None


# TODO: OpenID connect authenticators: google, github, etc.
# TODO: run authentication as middleware so other middlewares can access user data
# TODO: run authorization as route middleware


class Authentication:
    def __init__(
        self,
        authenticator: Authenticator,
        password_hasher: PasswordHasher,
    ) -> None:
        self.authenticator = authenticator
        self.passwords = password_hasher

    def configure(self, app: Kupala) -> None:
        app.state[Authenticator] = self
        app.commands.append(passwords_command)
        app.dependencies.registry[PasswordHasher] = VariableResolver(self.passwords)
        app.asgi_middleware.append(
            StarletteMiddleware(AuthenticationMiddleware, backend=AuthenticatorBackend(self.authenticator))
        )

    @classmethod
    def of(cls, app: Kupala) -> typing.Self:
        return typing.cast(typing.Self, app.state[Authenticator])


passwords_command = click.Group("passwords", help="Password management commands.")


@passwords_command.command("hash")
@click.argument("password")
@click.pass_obj
def hash_password_command(app: Kupala, password: str) -> None:
    """Hash a password."""
    passwords = Authentication.of(app).passwords
    click.echo(passwords.make(password))


@passwords_command.command("verify")
@click.argument("hashed_password")
@click.argument("plain_password")
@click.pass_obj
def verify_password_command(app: Kupala, hashed_password: str, plain_password: str) -> None:
    """Verify a password."""
    passwords = Authentication.of(app).passwords
    valid, new_hash = passwords.verify_and_migrate(plain_password, hashed_password)
    click.echo(
        "Valid: {valid}".format(valid=click.style("yes", fg="green") if valid else click.style("no", fg="yellow"))
    )
    if valid:
        click.echo(
            "Needs migration: {value}".format(
                value=click.style("yes", fg="yellow") if new_hash else click.style("no", fg="green")
            )
        )
