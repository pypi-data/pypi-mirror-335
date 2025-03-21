import datetime
import typing

from starlette.middleware import Middleware
from starsessions import JsonSerializer, Serializer, SessionAutoloadMiddleware, SessionMiddleware, SessionStore

from kupala import Kupala


class Sessions:
    def __init__(
        self,
        store: SessionStore,
        *,
        autoload: bool = False,
        autoload_patterns: list[str | typing.Pattern[str]] | None = None,
        rolling: bool = True,
        lifetime: datetime.timedelta = datetime.timedelta(days=14),
        cookie_name: str = "session",
        cookie_same_site: str = "strict",
        cookie_https_only: bool = True,
        cookie_domain: str | None = None,
        cookie_path: str = "/",
        serializer: Serializer | None = None,
    ) -> None:
        self.rolling = rolling
        self.store = store
        self.lifetime = lifetime
        self.cookie_name = cookie_name
        self.cookie_same_site = cookie_same_site
        self.cookie_https_only = cookie_https_only
        self.cookie_domain = cookie_domain
        self.cookie_path = cookie_path
        self.serializer = serializer or JsonSerializer()
        self.autoload = autoload
        self.autoload_patterns = autoload_patterns or []

    def configure(self, app: Kupala) -> None:
        app.asgi_middleware.append(
            Middleware(
                SessionMiddleware,
                store=self.store,
                lifetime=self.lifetime,
                rolling=self.rolling,
                cookie_name=self.cookie_name,
                cookie_same_site=self.cookie_same_site,
                cookie_https_only=self.cookie_https_only,
                cookie_domain=self.cookie_domain,
                cookie_path=self.cookie_path,
                serializer=self.serializer,
            ),
        )
        if self.autoload:
            app.asgi_middleware.append(Middleware(SessionAutoloadMiddleware, paths=self.autoload_patterns))
