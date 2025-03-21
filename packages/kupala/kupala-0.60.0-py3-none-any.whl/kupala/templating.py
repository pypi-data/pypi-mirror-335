import functools
import os
import typing

import jinja2
import jinja2.ext
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from kupala import Kupala
from kupala.dependencies import VariableResolver
from kupala.routing import route_matches, url_matches

type ContextProcessor = typing.Callable[[Request], dict[str, typing.Any]]


def standard_processors(request: Request) -> dict[str, typing.Any]:
    return {
        "request": request,
        "app": request.app,
        "url_matches": functools.partial(url_matches, request),
        "route_matches": functools.partial(route_matches, request),
    }


class Templates(Jinja2Templates):
    def __init__(
        self,
        jinja_env: jinja2.Environment | None = None,
        *,
        debug: bool = False,
        auto_escape: bool = True,
        directories: typing.Sequence[str | os.PathLike[str]] = (),
        template_packages: typing.Sequence[str] = (),
        template_loaders: typing.Sequence[jinja2.BaseLoader] = (),
        context_processors: typing.Sequence[ContextProcessor] = (),
        extensions: typing.Sequence[str | type[jinja2.ext.Extension]] = (),
        globals: typing.Mapping[str, typing.Any] | None = None,
        filters: typing.Mapping[str, typing.Callable[[typing.Any], typing.Any]] | None = None,
        tests: typing.Mapping[str, typing.Callable[[typing.Any], bool]] | None = None,
        allow_undefined: bool = False,
    ) -> None:
        if not jinja_env:
            jinja_env = jinja2.Environment(
                auto_reload=debug,
                autoescape=auto_escape,
                extensions=extensions,
                undefined=jinja2.Undefined if allow_undefined else jinja2.StrictUndefined,
                loader=jinja2.ChoiceLoader(
                    [
                        *template_loaders,
                        jinja2.FileSystemLoader(directories),
                        *[jinja2.PackageLoader(package) for package in template_packages],
                        jinja2.PackageLoader("kupala"),
                    ]
                ),
            )
            jinja_env.globals.update(globals or {})
            jinja_env.filters.update(filters or {})
            jinja_env.tests.update(tests or {})

        context_processors = [standard_processors, *context_processors]

        super().__init__(
            env=jinja_env,
            context_processors=list(context_processors),
        )

    def render(self, name: str, context: dict[str, typing.Any] | None = None) -> str:
        """Render a template with the given context."""
        template = self.env.get_template(name)
        return template.render(context or {})

    def render_macro(
        self,
        name: str,
        macro: str,
        args: typing.Mapping[str, typing.Any] | None = None,
    ) -> str:
        """Render a macro from a template with the given arguments."""
        template: jinja2.Template = self.env.get_template(name)
        template_module = template.make_module({})
        callback = getattr(template_module, macro)
        return typing.cast(str, callback(**args or {}))

    def render_block(
        self,
        name: str,
        block: str,
        context: dict[str, typing.Any] | None = None,
    ) -> str:
        """Render a block from a template with the given context."""
        template = self.env.get_template(name)
        callback = template.blocks[block]
        template_context = template.new_context(context or {})
        return "".join(callback(template_context))

    def render_to_response(
        self,
        request: Request,
        name: str,
        context: dict[str, typing.Any] | None = None,
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
    ) -> Response:
        """Render a template to a response."""
        return super().TemplateResponse(
            request,
            name,
            context or {},
            status_code=status_code,
            headers=headers,
            media_type=media_type,
        )

    @classmethod
    def of(cls, app: Kupala) -> typing.Self:
        return typing.cast(typing.Self, app.state[Templates])

    def configure(self, app: Kupala) -> None:
        app.state[Templates] = self
        app.state[jinja2.Environment] = self.env
        app.dependencies.registry[Templates] = VariableResolver(self)
