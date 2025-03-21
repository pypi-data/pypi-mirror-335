from __future__ import annotations

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from kupala.contrib.sqlalchemy.query import MultipleResultsError, NoResultError, query
from tests.test_contrib.test_sqlalchemy.models import User


class TestOne:
    async def test_one(self, dbsession: AsyncSession) -> None:
        stmt = sa.select(User).where(User.id == 1)
        model = await query(dbsession).select(stmt).one()
        assert model.id == 1

    async def test_one_no_rows(self, dbsession: AsyncSession) -> None:
        with pytest.raises(NoResultError):
            stmt = sa.select(User).where(User.id == -1)
            await query(dbsession).select(stmt).one()

    async def test_one_multiple_rows(self, dbsession: AsyncSession) -> None:
        with pytest.raises(MultipleResultsError):
            stmt = sa.select(User).where(sa.or_(User.id == 1, User.id == 2))
            await query(dbsession).select(stmt).one()


class TestOneOrNone:
    async def test_one_or_none(self, dbsession: AsyncSession) -> None:
        stmt = sa.select(User).where(User.id == 1)
        model = await query(dbsession).select(stmt).one_or_none()
        assert model is not None
        assert model.id == 1

    async def test_one_or_none_no_row(self, dbsession: AsyncSession) -> None:
        stmt = sa.select(User).where(User.id == -1)
        model = await query(dbsession).select(stmt).one_or_none()
        assert model is None

    async def test_one_or_none_multiple_rows(self, dbsession: AsyncSession) -> None:
        with pytest.raises(MultipleResultsError):
            stmt = sa.select(User).where(sa.or_(User.id == 1, User.id == 2))
            await query(dbsession).select(stmt).one_or_none()


class TestOneOrRaise:
    async def test_one_or_raise(self, dbsession: AsyncSession) -> None:
        stmt = sa.select(User).where(User.id == 1)
        model = await query(dbsession).select(stmt).one_or_raise(ValueError())
        assert model

    async def test_one_or_raise_no_row(self, dbsession: AsyncSession) -> None:
        with pytest.raises(ValueError):
            await query(dbsession).select(sa.select(User).where(User.id == -1)).one_or_raise(ValueError())

    async def test_one_or_raise_multiple_rows(self, dbsession: AsyncSession) -> None:
        with pytest.raises(MultipleResultsError):
            stmt = sa.select(User).where(sa.or_(User.id == 1, User.id == 2))
            await query(dbsession).select(stmt).one_or_raise(ValueError())


class TestOneOrDefault:
    async def test_one_or_default(self, dbsession: AsyncSession) -> None:
        stmt = sa.select(User).where(User.id == 1)
        model = await query(dbsession).select(stmt).one_or_default(User(id=-1, name="n/a", email="n/a"))
        assert model.id == 1

    async def test_one_or_default_no_row(self, dbsession: AsyncSession) -> None:
        stmt = sa.select(User).where(User.id == -1)
        model = await query(dbsession).select(stmt).one_or_default(User(id=-1, name="n/a", email="n/a"))
        assert model.id == -1


async def test_of(dbsession: AsyncSession) -> None:
    stmt = query.of(User)
    models = await query(dbsession).select(stmt).all()
    assert len(models) == 9


async def test_all(dbsession: AsyncSession) -> None:
    stmt = sa.select(User)
    models = await query(dbsession).select(stmt).all()
    assert len(models) == 9


async def test_get(dbsession: AsyncSession) -> None:
    assert await query(dbsession).get(User, 1)
    assert not await query(dbsession).get(User, -1)


async def test_iterator(dbsession: AsyncSession) -> None:
    stmt = sa.select(User).limit(3)
    iterator = query(dbsession).select(stmt).iterator(batch_size=1)
    assert [1, 2, 3] == [model.id async for model in iterator]


async def test_exists(dbsession: AsyncSession) -> None:
    stmt = sa.select(User).where(User.id == 1)
    assert await query(dbsession).select(stmt).exists() is True

    stmt = sa.select(User).where(User.id == -1)
    assert await query(dbsession).select(stmt).exists() is False


async def test_count(dbsession: AsyncSession) -> None:
    stmt = sa.select(User)
    assert await query(dbsession).select(stmt).count() == 9

    stmt = sa.select(User).where(User.id == 1)
    assert await query(dbsession).select(stmt).count() == 1


class TestChoices:
    async def test_choices(self, dbsession: AsyncSession) -> None:
        stmt = sa.select(User).limit(3)
        choices = [choice async for choice in query(dbsession).select(stmt).choices()]
        assert choices == [(1, "user_01"), (2, "user_02"), (3, "user_03")]

    async def test_choices_string_keys(self, dbsession: AsyncSession) -> None:
        stmt = sa.select(User).limit(3)
        choices: list[tuple[int, str]] = [
            choice async for choice in query(dbsession).select(stmt).choices(label_attr="name", value_attr="id")
        ]
        assert choices == [(1, "user_01"), (2, "user_02"), (3, "user_03")]

    async def test_choices_callable_keys(self, dbsession: AsyncSession) -> None:
        stmt = sa.select(User).limit(3)
        choices = [
            choice
            async for choice in query(dbsession)
            .select(stmt)
            .choices(label_attr=lambda obj: obj.name, value_attr=lambda o: o.id)
        ]
        assert choices == [(1, "user_01"), (2, "user_02"), (3, "user_03")]
