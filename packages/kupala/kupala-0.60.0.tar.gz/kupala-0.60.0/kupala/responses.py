import json as jsonlib
import os
import typing
from json import JSONEncoder

from starlette.datastructures import URL, URLPath
from starlette.requests import Request
from starlette.responses import (
    ContentStream,
    FileResponse,
    HTMLResponse,
    JSONResponse as JSONResponse_,
    PlainTextResponse,
    RedirectResponse,
    Response,
    StreamingResponse,
)

from kupala.templating import Templates


class JSONResponse(JSONResponse_):
    def __init__(
        self,
        content: typing.Any,
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        indent: int = 2,
        encoder_class: type[JSONEncoder] | None = None,
    ):
        self._indent = indent
        self._encoder_class = encoder_class
        super().__init__(content, status_code, headers, media_type)

    def render(self, content: typing.Any) -> bytes:
        return jsonlib.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=self._indent,
            separators=(",", ":"),
            cls=self._encoder_class,
        ).encode("utf-8")


class EmptyResponse(Response):
    def __init__(self, headers: typing.Mapping[str, str] | None = None) -> None:
        super().__init__(b"", status_code=204, headers=headers)


class GoBackResponse(RedirectResponse):
    def __init__(
        self,
        request: Request,
        status_code: int = 302,
        headers: typing.Mapping[str, str] | None = None,
    ) -> None:
        default_url = URLPath(str(request.base_url), request.url.scheme, request.url.netloc)
        redirect_to = request.headers.get("referer", default_url)
        current_origin = request.url.netloc
        if current_origin not in redirect_to:
            redirect_to = default_url

        super().__init__(
            redirect_to,
            status_code=status_code,
            headers=headers,
        )


def text(content: str, status_code: int = 200, headers: typing.Mapping[str, str] | None = None) -> PlainTextResponse:
    """Return a plain text response."""
    return PlainTextResponse(content, status_code, headers=headers)


def html(content: str, status_code: int = 200, headers: typing.Mapping[str, str] | None = None) -> HTMLResponse:
    """Return an HTML response."""
    return HTMLResponse(content, status_code, headers=headers)


def redirect(
    url: str | URL, status_code: int = 302, headers: typing.Mapping[str, str] | None = None
) -> RedirectResponse:
    """Redirect to a URL."""
    return RedirectResponse(url, status_code, headers=headers)


def redirect_to_route(
    request: Request,
    route_name: str,
    route_params: typing.Mapping[str, typing.Any] | None = None,
    status_code: int = 302,
    headers: typing.Mapping[str, str] | None = None,
) -> RedirectResponse:
    """Redirect to a named route."""
    url = request.url_for(route_name, **(route_params or {}))
    return RedirectResponse(url, status_code, headers=headers)


def json(
    content: typing.Any,
    status_code: int = 200,
    headers: typing.Mapping[str, str] | None = None,
    indent: int = 2,
    encoder_class: type[jsonlib.JSONEncoder] | None = None,
) -> JSONResponse:
    """Return a JSON response."""
    return JSONResponse(content, status_code, headers=headers, indent=indent, encoder_class=encoder_class)


def send_file(
    path: str | os.PathLike[str],
    status_code: int = 200,
    headers: typing.Mapping[str, str] | None = None,
    media_type: str | None = None,
    filename: str | None = None,
    stat_result: os.stat_result | None = None,
    content_disposition_type: str = "attachment",
    inline: bool = False,
) -> FileResponse:
    """Return a response with a file."""
    if inline:
        content_disposition_type = "inline"

    return FileResponse(
        path,
        status_code=status_code,
        headers=headers,
        media_type=media_type,
        filename=filename,
        stat_result=stat_result,
        content_disposition_type=content_disposition_type,
    )


def empty(headers: typing.Mapping[str, str] | None = None) -> EmptyResponse:
    """Return an empty response with status code 204."""
    return EmptyResponse(headers=headers)


def back(request: Request, status_code: int = 302, headers: typing.Mapping[str, str] | None = None) -> GoBackResponse:
    """Redirect to the previous page."""
    return GoBackResponse(request, status_code=status_code, headers=headers)


def stream(
    content: ContentStream,
    status_code: int = 200,
    headers: typing.Mapping[str, str] | None = None,
    media_type: str = "application/octet-stream",
) -> StreamingResponse:
    return StreamingResponse(
        content=content,
        status_code=status_code,
        headers=headers,
        media_type=media_type,
    )


def template(
    request: Request,
    template_name: str,
    context: dict[str, typing.Any] | None = None,
    status_code: int = 200,
    headers: typing.Mapping[str, str] | None = None,
    media_type: str = "text/html",
) -> Response:
    """Render a template to a response."""
    return Templates.of(request.app).render_to_response(
        request, template_name, context, status_code=status_code, headers=headers, media_type=media_type
    )


def template_block(
    request: Request,
    template_name: str,
    block: str,
    context: dict[str, typing.Any] | None = None,
    status_code: int = 200,
    headers: typing.Mapping[str, str] | None = None,
    media_type: str = "text/html",
) -> Response:
    """Render a block from a template to a response."""
    content = Templates.of(request.app).render_block(template_name, block, context)
    return Response(content, status_code=status_code, headers=headers, media_type=media_type)


def template_macro(
    request: Request,
    template_name: str,
    macro_name: str,
    context: typing.Mapping[str, typing.Any] | None = None,
    status_code: int = 200,
    headers: typing.Mapping[str, str] | None = None,
    media_type: str = "text/html",
) -> Response:
    """Render a block from a template to a response."""
    content = Templates.of(request.app).render_macro(template_name, macro_name, context)
    return Response(content, status_code=status_code, headers=headers, media_type=media_type)
