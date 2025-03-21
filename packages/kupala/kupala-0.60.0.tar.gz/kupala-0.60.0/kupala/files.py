from __future__ import annotations

import contextlib
import dataclasses
import datetime
import enum
import functools
import os
import time
import typing

import anyio
from async_storages import FileStorage, FileSystemBackend, generate_file_path, MemoryBackend, S3Backend
from async_storages.backends.base import AsyncFileLike, AsyncReader
from async_storages.contrib.starlette import FileServer
from starlette.datastructures import UploadFile, URL
from starlette.requests import Request
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles as StarletteStaticFiles

from kupala import Kupala
from kupala.dependencies import VariableResolver
from kupala.templating import Templates

_boot_time = time.time()

KEY_STATIC_ROUTE_NAME = "staticfiles_route_name"
KEY_MEDIA_ROUTE_NAME = "mediafiles_route_name"


def static_url(request: Request, path: str) -> URL:
    """Return URL for static file.
    If path is absolute, return it as is."""
    if path.startswith(("http://", "https://")):
        return URL(path)

    path_name = request.app.state[KEY_STATIC_ROUTE_NAME]
    version = time.time() if request.app.debug else _boot_time
    return request.url_for(path_name, path=path).include_query_params(v=version)


def static_context_processor(request: Request) -> dict[str, typing.Any]:
    return {"static_url": functools.partial(static_url, request)}


class StaticFiles:
    def __init__(
        self,
        packages: list[str | tuple[str, str]] | None = None,
        directory: str | None = None,
        url_prefix: str = "/static",
        route_name: str = "static",
    ) -> None:
        self.url_prefix = url_prefix
        self.route_name = route_name
        self.packages = packages
        self.directory = directory

    def configure(self, app: Kupala) -> None:
        app.routes.append(
            Mount(
                path=self.url_prefix,
                name=self.route_name,
                app=StarletteStaticFiles(
                    packages=self.packages,
                    directory=self.directory,
                ),
            ),
        )
        app.state[KEY_STATIC_ROUTE_NAME] = self.route_name
        with contextlib.suppress(KeyError):
            templates: Templates = app.state[Templates]
            templates.context_processors.append(static_context_processor)


class StorageType(enum.StrEnum):
    S3 = "s3"
    LOCAL = "local"
    MEMORY = "memory"


@dataclasses.dataclass(frozen=True)
class LocalConfig:
    directory: str
    url_prefix: str
    make_dirs: bool = True
    make_dirs_exists_ok: bool = True
    make_dirs_permissions: int = 0o777


@dataclasses.dataclass(frozen=True)
class S3Config:
    bucket: str
    access_key: str
    secret_key: str
    region: str
    endpoint: str | None = None
    signed_link_ttl: datetime.timedelta = datetime.timedelta(hours=1)


@dataclasses.dataclass(frozen=True)
class MemoryConfig:
    pass


type StorageConfig = LocalConfig | S3Config | MemoryConfig


def media_url(request: Request, path: str) -> URL:
    """Return URL for static file.
    If path is absolute, return it as is."""
    if path.startswith(("http://", "https://")):
        return URL(path)

    path_name = request.app.state[KEY_MEDIA_ROUTE_NAME]
    return request.url_for(path_name, path=path)


def media_context_processor(request: Request) -> dict[str, typing.Any]:
    return {"media_url": functools.partial(static_url, request)}


class Files:
    def __init__(
        self,
        default: str | None = None,
        storages: dict[str, FileStorage] | None = None,
        url_prefix: str = "/media",
        route_name: str = "media",
    ) -> None:
        if default:
            assert default in (storages or {}), f"Default storage '{default}' is not configured."

        self._storages = storages or {}
        self._default = default
        self.url_prefix = url_prefix
        self.route_name = route_name

    def get_storage(self, name: str) -> FileStorage:
        return self._storages[name]

    async def temporary_url(
        self, file_name: str | os.PathLike[typing.AnyStr], ttl: int | datetime.timedelta, *, storage: str | None = None
    ) -> URL:
        storage = self.get_storage(storage or self._default)
        return await storage.url(file_name)

    async def temporary_upload_url(
        self, file_name: str | os.PathLike[typing.AnyStr], ttl: int | datetime.timedelta, *, storage: str | None = None
    ) -> URL:
        pass

    async def copy(
        self,
        source: str | os.PathLike[typing.AnyStr],
        destination: str | os.PathLike[typing.AnyStr],
        *,
        storage: str | None = None,
    ) -> None:
        pass

    async def move(
        self,
        source: str | os.PathLike[typing.AnyStr],
        destination: str | os.PathLike[typing.AnyStr],
        *,
        storage: str | None = None,
    ) -> None:
        pass

    async def exists(self, file_name: str | os.PathLike[typing.AnyStr], *, storage: str | None = None) -> bool:
        storage = self.get_storage(storage or self._default)
        return await storage.exists(file_name)

    async def open(self, file_name: str | os.PathLike[typing.AnyStr], *, storage: str | None = None) -> AsyncFileLike:
        return await self.get_storage(storage or self._default).open(file_name)

    async def readlines(
        self, file_name: str | os.PathLike[typing.AnyStr], storage: str | None = None
    ) -> typing.AsyncIterator[bytes]:
        return await self.get_storage(storage or self._default).iterator(file_name)

    async def write(
        self,
        file_name: str | os.PathLike[typing.AnyStr],
        data: bytes | AsyncReader | typing.BinaryIO,
        *,
        storage: str | None = None,
    ) -> None:
        return self.get_storage(storage or self._default).write(file_name, data)

    async def upload(
        self,
        upload_file: UploadFile,
        destination: str,
        *,
        extra_tokens: typing.Mapping[str, typing.Any] | None = None,
        storage: str | None = None,
    ) -> str:
        assert upload_file.filename, "Filename is required"
        storage = self.get_storage(storage or self._default)
        file_name = generate_file_path(upload_file.filename, destination, extra_tokens=extra_tokens or {})
        await storage.write(file_name, upload_file)
        return file_name

    async def upload_many(
        self,
        destination: str,
        upload_files: typing.Sequence[UploadFile],
        extra_tokens: typing.Mapping[str, typing.Any] | None = None,
    ) -> str:
        file_names: list[str] = []
        extra_tokens = extra_tokens or {}

        async def worker(file: UploadFile) -> None:
            assert file.filename, "Filename is required"
            file_path = await self.upload(file, destination, extra_tokens=extra_tokens)
            file_names.append(file_path)

        async with anyio.create_task_group() as tg:
            for file in upload_files:
                tg.start_soon(worker, file)
        return file_names

    async def delete(
        self,
        file_name: str | os.PathLike[typing.AnyStr],
        *,
        storage: str | None = None,
    ) -> None:
        storage = self.get_storage(storage or self._default)
        await storage.delete(file_name)

    async def delete_many(
        self,
        file_names: typing.Sequence[str | os.PathLike[typing.AnyStr]],
        *,
        storage: str | None = None,
    ) -> None:
        async with anyio.create_task_group() as tg:
            for file_name in file_names:
                tg.start_soon(functools.partial(self.delete, storage=storage), file_name)

    @classmethod
    def from_configs(cls, storage_name: str, **storages: StorageConfig) -> Files:
        config = storages[storage_name]
        if isinstance(config, LocalConfig):
            return cls(
                FileSystemBackend(
                    base_dir=config.directory,
                    base_url=config.url_prefix,
                    mkdirs=config.make_dirs,
                    mkdir_exists_ok=config.make_dirs_exists_ok,
                    mkdir_permissions=config.make_dirs_permissions,
                )
            )

        if isinstance(config, S3Config):
            return cls(
                S3Backend(
                    bucket=config.bucket,
                    aws_access_key_id=config.access_key,
                    aws_secret_access_key=config.secret_key,
                    region_name=config.region,
                    endpoint_url=config.endpoint,
                    signed_link_ttl=config.signed_link_ttl.total_seconds(),
                )
            )

        if isinstance(config, MemoryConfig):
            return cls(MemoryBackend())

        raise ValueError(f"Unknown storage type: {config}")

    def configure(self, app: Kupala) -> None:
        app.routes.append(
            Mount(
                path=self.url_prefix,
                name=self.route_name,
                app=FileServer(self._storages, as_attachment=True, redirect_status=301),
            ),
        )
        app.state[KEY_MEDIA_ROUTE_NAME] = self.route_name
        app.dependencies.registry[type(self)] = VariableResolver(self)
        with contextlib.suppress(KeyError):
            templates: Templates = app.state[Templates]
            templates.context_processors.append(media_context_processor)

    @classmethod
    def of(cls, app: Kupala) -> typing.Self:
        return app.state[KEY_MEDIA_ROUTE_NAME]
