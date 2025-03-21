from __future__ import annotations

import enum
import typing


T = typing.TypeVar("T")
Choices = typing.Iterable[tuple[T, str]]


class ChoicesMeta(enum.EnumMeta):
    _value_map: dict[typing.Any, str]

    def __new__(mcs, name: str, bases: tuple[typing.Any], attrs: typing.Any, **kwargs: typing.Any) -> ChoicesMeta:
        value_map = {}
        for key in attrs._member_names:
            member = attrs[key]
            match member:
                case list([value, label]) | tuple([value, label]):
                    value_map[value] = label
                    dict.__setitem__(attrs, key, value)
                case _:
                    value_map[member] = key.replace("_", " ").title()

        cls = super().__new__(mcs, name, bases, attrs, **kwargs)
        setattr(cls, "_value_map", value_map)
        return enum.unique(cls)  # type:ignore

    @property
    def labels(cls) -> typing.Iterable[str]:
        return tuple(cls._value_map.values())

    @property
    def values(cls) -> typing.Iterable[typing.Any]:
        return tuple(cls._value_map.keys())

    @property
    def choices(cls) -> Choices[typing.Any]:
        return tuple([tuple([value, label]) for value, label in cls._value_map.items()])


class BaseChoices(enum.Enum, metaclass=ChoicesMeta): ...


class IntegerChoices(int, BaseChoices):
    @typing.overload
    def __eq__(self, other: IntegerChoices) -> bool: ...

    @typing.overload
    def __eq__(self, other: int) -> bool: ...

    @typing.overload
    def __eq__(self, other: object) -> bool: ...

    def __eq__(self, other: object | int | IntegerChoices) -> bool:
        return self.value == other


class TextChoices(str, BaseChoices):
    def __str__(self) -> str:
        return str(self.value)

    @typing.overload
    def __eq__(self, other: TextChoices) -> bool: ...

    @typing.overload
    def __eq__(self, other: str) -> bool: ...

    @typing.overload
    def __eq__(self, other: object) -> bool: ...

    def __eq__(self, other: object | str | TextChoices) -> bool:
        return self.value == other
