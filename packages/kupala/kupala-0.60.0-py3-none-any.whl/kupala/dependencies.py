from __future__ import annotations

import abc
import contextlib
import dataclasses
import inspect
import types
import typing

from starlette.concurrency import run_in_threadpool
from starlette.requests import HTTPConnection


class DependencyError(Exception): ...


class DependencyNotFoundError(Exception): ...


class DependencyRequiresValueError(Exception): ...


@dataclasses.dataclass
class Argument:
    param_name: str
    param_type: type | typing.TypeAliasType
    default: typing.Any
    annotation: typing.Any
    nullable: bool


@dataclasses.dataclass
class ResolveContext:
    dependencies: Dependencies
    sync_stack: contextlib.ExitStack = dataclasses.field(default_factory=contextlib.ExitStack)
    async_stack: contextlib.AsyncExitStack = dataclasses.field(default_factory=contextlib.AsyncExitStack)
    cache: dict[int, typing.Any] = dataclasses.field(default_factory=dict)

    async def resolve(self, dependency: typing.Hashable | DependencyResolver) -> typing.Any:
        return await self.dependencies.resolve(self, dependency)

    async def __aenter__(self) -> typing.Self:
        self.sync_stack.__enter__()
        await self.async_stack.__aenter__()
        return self

    async def __aexit__(self, *exc_type: typing.Any) -> None:
        await self.async_stack.__aexit__(*exc_type)
        self.sync_stack.__exit__(*exc_type)


class DependencyResolver(abc.ABC):  # pragma: no cover
    @abc.abstractmethod
    async def resolve(self, context: ResolveContext) -> typing.Any:
        raise NotImplementedError


type DependencyScope = typing.Literal["transient", "cached", "scoped"]


class RegistryResolver(DependencyResolver):
    def __init__(self, klass: typing.Hashable) -> None:
        self.klass = klass

    async def resolve(self, context: ResolveContext) -> typing.Any:
        return await context.resolve(self.klass)


class FactoryResolver(DependencyResolver):
    """Dependency resolver that resolves dependencies from factories."""

    def __init__(self, factory: typing.Callable[..., typing.Any], *, scope: DependencyScope = "transient") -> None:
        self._scope = scope
        self._factory = factory
        self._dependencies = create_dependency_specs(factory)
        self._is_async = inspect.iscoroutinefunction(factory)
        self._value: typing.Any = None

    async def resolve(self, context: ResolveContext) -> typing.Any:
        if self._scope == "cached" and self._value is not None:
            return self._value

        if self._scope == "scoped":
            if value := context.cache.get(id(context)):
                return value

        resolver = Dependencies(parent=context.dependencies)
        dependencies = await resolver.solve_parameters(context, self._dependencies)
        value = await self._resolve_function(dependencies)
        if isinstance(value, contextlib.AbstractContextManager):
            value = context.sync_stack.enter_context(value)
        elif isinstance(value, contextlib.AbstractAsyncContextManager):
            value = await context.async_stack.enter_async_context(value)
        else:
            value = value

        if self._scope == "scoped":
            context.cache[id(context)] = value

        if self._scope == "cached":
            self._value = value

        return value

    async def _resolve_function(self, dependencies: dict[str, typing.Any]) -> typing.Any:
        return await self._factory(**dependencies) if self._is_async else self._factory(**dependencies)


class VariableResolver(DependencyResolver):
    """Simple resolver that returns the same value for all dependencies."""

    __match_args__ = ("_value",)

    def __init__(self, value: typing.Any) -> None:
        self._value = value

    async def resolve(self, context: ResolveContext) -> typing.Any:
        return self._value


class RequestResolver(DependencyResolver):
    """Helper resolver that uses request state to return dependency values.
    It accepts a callable that receives HTTPConnection (like Request or WebSocket) and returns a value.

    Note: this resolver should be used in request context only.
    """

    def __init__(
        self,
        fn: typing.Callable[[HTTPConnection, Argument], typing.Any] | typing.Callable[[HTTPConnection], typing.Any],
    ) -> None:
        signature = inspect.signature(fn)
        self._takes_argument = len(signature.parameters) == 2
        self._fn = fn

    async def resolve(self, context: ResolveContext) -> typing.Any:
        args = [await context.resolve(HTTPConnection)]
        if self._takes_argument:
            args.append(await context.resolve(Argument))
        return self._fn(*args)


@dataclasses.dataclass
class Injection:
    dependency: Argument
    resolver: DependencyResolver


def create_dependency_from_parameter(parameter: inspect.Parameter) -> Injection:
    annotation: type = parameter.annotation
    if isinstance(annotation, typing.TypeAliasType):
        annotation = annotation.__value__

    origin = typing.get_origin(annotation)
    is_nullable = False
    param_type: type = parameter.annotation
    resolver: DependencyResolver = RegistryResolver(param_type)

    if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
        raise DependencyError(
            "Dependencies with positional-only parameters are not supported. "
            f"Parameter: {parameter.name}, annotation: {parameter.annotation}."
        )

    if parameter.default is not inspect.Parameter.empty:
        raise DependencyError(
            "Dependencies with default values are not supported. "
            f"Parameter: {parameter.name}, annotation: {parameter.annotation}."
        )

    if origin not in [None, typing.Annotated, types.UnionType]:
        raise DependencyError(
            "Only Union and Annotated generic types are supported as dependencies. "
            f"Parameter: {parameter.name}, annotation: {parameter.annotation}."
        )

    # handle union types and nullable types
    if origin is types.UnionType:
        type_args = typing.get_args(parameter.annotation)

        # support union type with at most two arguments
        if len(type_args) > 2:
            raise DependencyError(
                "Union type with more than two arguments is not supported. "
                f"Parameter: {parameter.name}, annotation: {parameter.annotation}."
            )

        # support only nullable unions
        # we can't resolve non-distinct union types
        if None not in type_args and types.NoneType not in type_args:
            raise DependencyError(
                "Union type without None is not supported. "
                f"Parameter: {parameter.name}, annotation: {parameter.annotation}."
            )

        is_nullable = type(None) in type_args
        annotation = [arg for arg in typing.get_args(parameter.annotation) if arg is not None][0]
        origin = typing.get_origin(annotation)
        param_type = annotation

    if origin is typing.Annotated:
        type_args = typing.get_args(annotation)
        defined_param_type = type_args[0]
        if type(defined_param_type) is typing.TypeVar:
            defined_param_type = defined_param_type.__default__
            if defined_param_type is typing.NoDefault:
                raise DependencyError(
                    "TypeVar without default type is not supported. "
                    f"Parameter: {parameter.name}, annotation: {parameter.annotation}."
                )
        if typing.get_origin(defined_param_type) is types.UnionType:
            defined_param_type_args = [arg for arg in typing.get_args(defined_param_type)]
            if types.NoneType not in defined_param_type_args:
                raise DependencyError(
                    "Union type without None is not supported. "
                    f"Parameter: {parameter.name}, annotation: {parameter.annotation}."
                )

            defined_param_type = defined_param_type_args[0]
            is_nullable = True

        param_type = defined_param_type

        match type_args:
            case (*_, DependencyResolver() as defined_resolver):
                resolver = defined_resolver

            case (*_, fn) if inspect.isfunction(fn) and fn.__name__ == "<lambda>":
                signature = inspect.signature(fn)
                if len(signature.parameters) == 0:
                    resolver = FactoryResolver(fn)
                elif len(signature.parameters) == 1:

                    def one_param_callback(request: HTTPConnection) -> typing.Any:
                        return fn(request)

                    resolver = RequestResolver(one_param_callback)
                elif len(signature.parameters) == 2:

                    def two_params_callback(request: HTTPConnection, spec: Argument) -> typing.Any:
                        return fn(request, spec)

                    resolver = RequestResolver(two_params_callback)
                else:
                    raise DependencyError(
                        "Lambda passed as dependency should accept zero, one, or two parameters: "
                        "(lambda: ...), (lambda request: ...), or (lambda request, spec: ...)."
                    )

            case (*_, fn) if inspect.isgeneratorfunction(fn) or inspect.isasyncgenfunction(fn):
                raise DependencyError(
                    "Generators are not supported as dependency factories. "
                    "Use context managers or async context managers instead. "
                    f"Parameter: {parameter.name}, resolver: {fn}."
                )

            case (*_, fn) if inspect.isfunction(fn):
                resolver = FactoryResolver(fn)

            case (*_, value):
                resolver = VariableResolver(value)

            case _:  # pragma: no cover, we never reach this line
                ...

    return Injection(
        resolver=resolver,
        dependency=Argument(
            param_type=param_type,
            nullable=is_nullable,
            default=parameter.default,
            param_name=parameter.name,
            annotation=parameter.annotation,
        ),
    )


def create_dependency_specs(fn: typing.Callable[..., typing.Any]) -> dict[str, Injection]:
    signature = inspect.signature(fn, eval_str=True)
    return {parameter.name: create_dependency_from_parameter(parameter) for parameter in signature.parameters.values()}


_PS = typing.ParamSpec("_PS")
_RT = typing.TypeVar("_RT")


class Dependencies:
    def __init__(
        self,
        dependencies: dict[typing.Hashable, DependencyResolver] | None = None,
        parent: Dependencies | None = None,
    ) -> None:
        self.parent = parent
        self.registry: dict[typing.Hashable, DependencyResolver] = dependencies or {}

    async def resolve(self, context: ResolveContext, dependency: DependencyResolver | typing.Hashable) -> typing.Any:
        if dependency in self.registry:
            return await self.registry[dependency].resolve(context)

        if typing.get_origin(dependency) is typing.Annotated:
            dependency = next((r for r in typing.get_args(dependency) if isinstance(r, DependencyResolver)), None)
            if not dependency:
                raise DependencyNotFoundError(f"Dependency {dependency} not found and is not a resolver.")

        if isinstance(dependency, DependencyResolver):
            return await dependency.resolve(context)

        if self.parent is not None:
            return await self.parent.resolve(context, dependency)

        raise DependencyNotFoundError(f"Dependency {dependency} not found.")

    async def solve_parameters(
        self, context: ResolveContext, dependencies: dict[str, Injection]
    ) -> dict[str, typing.Any]:
        solved_dependencies: dict[str, typing.Any] = {}
        for spec in dependencies.values():
            child_context = ResolveContext(
                sync_stack=context.sync_stack,
                async_stack=context.async_stack,
                dependencies=Dependencies(
                    parent=context.dependencies,
                    dependencies={Argument: VariableResolver(spec.dependency)},
                ),
            )
            solved_dependencies[spec.dependency.param_name] = await context.dependencies.resolve(
                child_context, spec.resolver
            )

        return solved_dependencies

    async def call_with(
        self,
        fn: typing.Callable[..., _RT] | typing.Callable[..., typing.Awaitable[_RT]],
        dependencies: dict[str, Injection],
    ) -> _RT:
        """Call a function with prepared dependencies."""
        context = ResolveContext(dependencies=self)

        async with context:
            solved_dependencies = await self.solve_parameters(context, dependencies)
            if inspect.iscoroutinefunction(fn):
                rv = await fn(**solved_dependencies)
            else:
                rv = await run_in_threadpool(fn, **solved_dependencies)
            return typing.cast(_RT, rv)


T = typing.TypeVar("T", default=str)

FromPath = typing.Annotated[
    T, RequestResolver(lambda request, attr: attr.param_type(request.path_params[attr.param_name]))
]
