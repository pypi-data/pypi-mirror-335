"""SQLAlchemy column types and annotations."""

import datetime
import typing
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column

type JSONSerializable = str | int | float | bool | None | dict[str, JSONSerializable] | list[JSONSerializable]

IntPk = typing.Annotated[int, mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)]
StrPk = typing.Annotated[str, mapped_column(sa.Text, primary_key=True)]
UUIDPk = typing.Annotated[uuid.UUID, mapped_column(sa.UUID(), primary_key=True, default=uuid.uuid4)]
JSONDict = typing.Annotated[dict[str, JSONSerializable], mapped_column(JSONB, default=dict, server_default="{}")]
JSONList = typing.Annotated[list[JSONSerializable], mapped_column(JSONB, default=list, server_default="[]")]

AutoCreatedAt = typing.Annotated[
    datetime.datetime,
    mapped_column(
        nullable=False,
        server_default=sa.func.now(),
        default=lambda: datetime.datetime.now(datetime.UTC),
    ),
]
AutoUpdatedAt = typing.Annotated[
    datetime.datetime,
    mapped_column(
        nullable=False,
        server_default=sa.func.now(),
        server_onupdate=sa.func.now(),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
        default=lambda: datetime.datetime.now(datetime.UTC),
    ),
]
