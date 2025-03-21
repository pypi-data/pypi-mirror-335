import contextlib
import inspect
import typing

import pytest
from starlette.requests import HTTPConnection, Request

from kupala.dependencies import (
    Argument,
    create_dependency_from_parameter,
    create_dependency_specs,
    Dependencies,
    DependencyError,
    DependencyNotFoundError,
    FactoryResolver,
    FromPath,
    RegistryResolver,
    RequestResolver,
    ResolveContext,
    VariableResolver,
)


class TestVariableResolver:
    async def test_variable_resolver(self) -> None:
        resolver = VariableResolver("abc")
        context = ResolveContext(
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
            dependencies=Dependencies(),
        )
        value = await resolver.resolve(context)
        assert value == "abc"


class TestFactoryResolver:
    async def test_sync_factory(self) -> None:
        def factory() -> str:
            return "abc"

        resolver = FactoryResolver(factory)
        context = ResolveContext(
            dependencies=Dependencies(),
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
        )
        value = await resolver.resolve(context)
        assert value == "abc"

    async def test_async_factory(self) -> None:
        async def factory() -> str:
            return "abc"

        resolver = FactoryResolver(factory)
        context = ResolveContext(
            dependencies=Dependencies(),
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
        )
        value = await resolver.resolve(context)
        assert value == "abc"

    async def test_subdependencies(self) -> None:
        def level3_factory() -> str:
            return "three"

        def level2_factory(three: typing.Annotated[str, FactoryResolver(level3_factory)]) -> str:
            return f"two-{three}"

        def level1_factory(two: typing.Annotated[str, FactoryResolver(level2_factory)]) -> str:
            return f"one-{two}"

        def factory(parent: typing.Annotated[str, FactoryResolver(level1_factory)]) -> str:
            return f"ok-{parent}"

        resolver = FactoryResolver(factory)
        context = ResolveContext(
            dependencies=Dependencies(),
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
        )
        value = await resolver.resolve(context)
        assert value == "ok-one-two-three"

    async def test_async_subdependencies(self) -> None:
        async def level3_factory() -> str:
            return "three"

        async def level2_factory(three: typing.Annotated[str, FactoryResolver(level3_factory)]) -> str:
            return f"two-{three}"

        async def level1_factory(two: typing.Annotated[str, FactoryResolver(level2_factory)]) -> str:
            return f"one-{two}"

        async def factory(parent: typing.Annotated[str, FactoryResolver(level1_factory)]) -> str:
            return f"ok-{parent}"

        resolver = FactoryResolver(factory)
        context = ResolveContext(
            dependencies=Dependencies(),
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
        )
        value = await resolver.resolve(context)
        assert value == "ok-one-two-three"

    async def test_mixed_subdependencies(self) -> None:
        async def level3_factory() -> str:
            return "three"

        def level2_factory(three: typing.Annotated[str, FactoryResolver(level3_factory)]) -> str:
            return f"two-{three}"

        async def level1_factory(two: typing.Annotated[str, FactoryResolver(level2_factory)]) -> str:
            return f"one-{two}"

        def factory(parent: typing.Annotated[str, FactoryResolver(level1_factory)]) -> str:
            return f"ok-{parent}"

        resolver = FactoryResolver(factory)
        context = ResolveContext(
            dependencies=Dependencies(),
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
        )
        value = await resolver.resolve(context)
        assert value == "ok-one-two-three"

    async def test_sync_context_manager_dependency(self) -> None:
        @contextlib.contextmanager
        def factory() -> typing.Generator[str, None, None]:
            yield "abc"

        resolver = FactoryResolver(factory)
        context = ResolveContext(
            dependencies=Dependencies(),
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
        )
        async with context:
            value = await resolver.resolve(context)
        assert value == "abc"

    async def test_async_context_manager_dependency(self) -> None:
        @contextlib.asynccontextmanager
        async def factory() -> typing.AsyncGenerator[str, None]:
            yield "abc"

        resolver = FactoryResolver(factory)
        context = ResolveContext(
            dependencies=Dependencies(),
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
        )
        async with context:
            value = await resolver.resolve(context)
        assert value == "abc"


class TestFactoryResolverScopes:
    async def test_transient(self) -> None:
        def factory() -> object:
            return object()

        resolver = FactoryResolver(factory, scope="transient")
        context = ResolveContext(
            dependencies=Dependencies(),
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
        )
        value1 = await resolver.resolve(context)
        value2 = await resolver.resolve(context)
        assert id(value1) != id(value2)

    async def test_cached(self) -> None:
        def factory() -> object:
            return object()

        resolver = FactoryResolver(factory, scope="cached")
        context = ResolveContext(
            dependencies=Dependencies(),
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
        )
        value1 = await resolver.resolve(context)
        value2 = await resolver.resolve(context)
        assert id(value1) == id(value2)

    async def test_scoped(self) -> None:
        def factory() -> object:
            return object()

        resolver = FactoryResolver(factory, scope="scoped")
        context = ResolveContext(
            dependencies=Dependencies(),
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
        )
        context2 = ResolveContext(
            dependencies=Dependencies(),
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
        )
        value1: object = await resolver.resolve(context)
        value2: object = await resolver.resolve(context)
        value3: object = await resolver.resolve(context2)
        assert id(value1) == id(value2)
        assert id(value1) != id(value3)
        assert id(value2) != id(value3)


class TestRequestResolver:
    async def test_one_param_callback(self) -> None:
        request = Request({"type": "http", "state": {"dep": "abc"}})

        resolver = RequestResolver(lambda r: r.state.dep)
        context = ResolveContext(
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
            dependencies=Dependencies(
                {
                    HTTPConnection: VariableResolver(request),
                }
            ),
        )
        assert await resolver.resolve(context) == "abc"

    async def test_two_param_callback(self) -> None:
        request = Request({"type": "http", "state": {"dep": "abc"}})

        resolver = RequestResolver(lambda r, a: r.state.dep + a.param_name)
        context = ResolveContext(
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
            dependencies=Dependencies(
                {
                    HTTPConnection: VariableResolver(request),
                    Argument: VariableResolver(
                        Argument(
                            param_name="def",
                            param_type=str,
                            default=None,
                            annotation=str,
                            nullable=False,
                        )
                    ),
                }
            ),
        )
        assert await resolver.resolve(context) == "abcdef"


class TestRegistryResolver:
    async def test_resolve(self) -> None:
        resolver = RegistryResolver(Dep)
        context = ResolveContext(
            sync_stack=contextlib.ExitStack(),
            async_stack=contextlib.AsyncExitStack(),
            dependencies=Dependencies(
                {
                    Dep: VariableResolver("abc"),
                }
            ),
        )
        value: str = await resolver.resolve(context)
        assert value == "abc"


class TestDependencies:
    async def test_resolves_dependency(self) -> None:
        dependencies = Dependencies(
            dependencies={
                str: VariableResolver("abc"),
            }
        )
        context = ResolveContext(dependencies=Dependencies())
        assert await dependencies.resolve(context, str) == "abc"

    async def test_resolves_from_parent(self) -> None:
        dependencies = Dependencies(
            dependencies={str: VariableResolver("abc")},
            parent=Dependencies(dependencies={int: VariableResolver(1)}),
        )

        context = ResolveContext(dependencies=Dependencies())
        assert await dependencies.resolve(context, int) == 1

    async def test_resolves_type_alias(self) -> None:
        type A = str
        dependencies = Dependencies(
            dependencies={
                A: VariableResolver("abc"),
                str: VariableResolver("str"),
            }
        )

        context = ResolveContext(dependencies=Dependencies())
        assert await dependencies.resolve(context, A) == "abc"
        assert await dependencies.resolve(context, str) == "str"

    async def test_missing_type(self) -> None:
        context = ResolveContext(dependencies=Dependencies())
        with pytest.raises(DependencyNotFoundError):
            await context.resolve(str)

    async def test_call_with(self) -> None:
        type Dep = str

        def fn(dep: Dep, dep2: typing.Annotated[str, VariableResolver("def")]) -> str:
            return dep + dep2

        resolver = Dependencies(
            dependencies={
                Dep: VariableResolver("abc"),
            }
        )
        dependencies = create_dependency_specs(fn)
        assert await resolver.call_with(fn, dependencies) == "abcdef"

    async def test_call_with_async(self) -> None:
        type Dep = str

        async def fn(dep: Dep, dep2: typing.Annotated[str, VariableResolver("def")]) -> str:
            return dep + dep2

        resolver = Dependencies(
            dependencies={
                Dep: VariableResolver("abc"),
            }
        )
        dependencies = create_dependency_specs(fn)
        assert await resolver.call_with(fn, dependencies) == "abcdef"  # type: ignore


type Dep = str
type DepAlias = str


class TestCreateDependencyFromParameter:
    async def test_type(self) -> None:
        """It should create an injection from a simple annotation.
        Example def fn(dep: Dep) -> None: ...
        """
        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                annotation=Dep,
                default=inspect.Parameter.empty,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )
        assert injection.dependency.param_name == "dep"
        assert injection.dependency.param_type == Dep
        assert injection.dependency.default is inspect.Parameter.empty
        assert injection.dependency.annotation == Dep
        assert injection.dependency.nullable is False

    def test_union_unsupported(self) -> None:
        """It should raise an error if the union has more than two parameters.
        Example def fn(dep: str | int | None) -> None: ..."""
        with pytest.raises(DependencyError, match="Union type with more than two arguments is not supported"):
            create_dependency_from_parameter(
                inspect.Parameter(
                    name="dep",
                    default=inspect.Parameter.empty,
                    annotation=str | int | None,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            )

    def test_param_default_unsupported(self) -> None:
        with pytest.raises(DependencyError, match="Dependencies with default values are not supported."):
            create_dependency_from_parameter(
                inspect.Parameter(
                    name="dep",
                    default="abc",
                    annotation=str,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            )

    def test_positional_only_unsupported(self) -> None:
        with pytest.raises(DependencyError, match="Dependencies with positional-only parameters are not supported"):
            create_dependency_from_parameter(
                inspect.Parameter(
                    name="dep",
                    default="abc",
                    annotation=str,
                    kind=inspect.Parameter.POSITIONAL_ONLY,
                )
            )

    def test_union_none(self) -> None:
        """It should create an injection from a nullable type.
        Example def fn(dep: str | None) -> None: ..."""
        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                default=inspect.Parameter.empty,
                annotation=str | None,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )
        assert injection.dependency.param_type is str
        assert injection.dependency.nullable is True

    def test_union_non_none(self) -> None:
        """It should raise an error if the union has no None type.
        Example def fn(dep: str | int) -> None: ..."""
        with pytest.raises(DependencyError, match="Union type without None is not supported"):
            create_dependency_from_parameter(
                inspect.Parameter(
                    name="dep",
                    default=inspect.Parameter.empty,
                    annotation=str | int,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            )

    def test_annotated(self) -> None:
        """It should create an injection from an annotated type.
        Example def fn(dep: typing.Annotated[Dep, VariableResolver("abc")]) -> None: ...
        """
        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                default=inspect.Parameter.empty,
                annotation=typing.Annotated[str, VariableResolver("abc")],
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )
        assert injection.dependency.param_type is str
        assert injection.dependency.nullable is False
        assert isinstance(injection.resolver, VariableResolver)

    def test_annotated_optional(self) -> None:
        """It should create an injection from an annotated nullable type.
        Example def fn(dep: Dep | None) -> None: ..."""
        with pytest.raises(DependencyError, match="Only Union and Annotated"):
            create_dependency_from_parameter(
                inspect.Parameter(
                    name="dep",
                    default=inspect.Parameter.empty,
                    annotation=typing.Annotated[str, VariableResolver("abc")] | None,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            )

    def test_annotated_union(self) -> None:
        """It should create an injection from an annotated union type.
        Example def fn(dep: typing.Annotated[Dep, VariableResolver("abc")] | int) -> None: ...
        """
        with pytest.raises(DependencyError, match="not supported"):
            create_dependency_from_parameter(
                inspect.Parameter(
                    name="dep",
                    default=inspect.Parameter.empty,
                    annotation=typing.Annotated[str | int, VariableResolver("abc")],
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            )

    def test_annotated_nullable(self) -> None:
        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                default=inspect.Parameter.empty,
                annotation=typing.Annotated[str | None, VariableResolver("abc")],
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )
        assert injection.dependency.param_type is str
        assert injection.dependency.nullable is True

    def test_annotated_typevar_with_default_type(self) -> None:
        _T = typing.TypeVar("_T", default=int)
        _Dep = typing.Annotated[_T, VariableResolver("abc")]

        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                default=inspect.Parameter.empty,
                annotation=_Dep,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )
        assert injection.dependency.param_type is int

    def test_annotated_typevar_without_default_type(self) -> None:
        _T = typing.TypeVar("_T")
        _Dep = typing.Annotated[_T, VariableResolver("abc")]

        with pytest.raises(DependencyError, match="TypeVar without default type is not supported"):
            create_dependency_from_parameter(
                inspect.Parameter(
                    name="dep",
                    default=inspect.Parameter.empty,
                    annotation=_Dep,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            )

    def test_annotated_resolver(self) -> None:
        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                default=inspect.Parameter.empty,
                annotation=typing.Annotated[str, VariableResolver("abc")],
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )
        assert injection.dependency.param_type is str
        assert isinstance(injection.resolver, VariableResolver)

    def test_annotated_resolver_with_extra_annotations(self) -> None:
        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                default=inspect.Parameter.empty,
                annotation=typing.Annotated[str, "abc", VariableResolver("abc")],
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )
        assert injection.dependency.param_type is str
        assert isinstance(injection.resolver, VariableResolver)

    def test_unsupported_generic(self) -> None:
        with pytest.raises(DependencyError, match="are supported as dependencies"):
            create_dependency_from_parameter(
                inspect.Parameter(
                    name="dep",
                    default=inspect.Parameter.empty,
                    annotation=list[str],
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            )

    async def test_shortcut_variable(self) -> None:
        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                annotation=typing.Annotated[str, "value"],
                default=inspect.Parameter.empty,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )
        context = ResolveContext(
            dependencies=Dependencies({HTTPConnection: VariableResolver(Request({"type": "http"}))}),
        )
        assert injection.dependency.param_type is str
        assert await context.resolve(injection.resolver) == "value"

    async def test_shortcut_factory(self) -> None:
        def factory() -> str:
            return "value"

        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                annotation=typing.Annotated[str, factory],
                default=inspect.Parameter.empty,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )
        context = ResolveContext(
            dependencies=Dependencies({HTTPConnection: VariableResolver(Request({"type": "http"}))}),
        )
        assert await context.resolve(injection.resolver) == "value"

    async def test_shortcut_zero_arg_lambda(self) -> None:
        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                annotation=typing.Annotated[str, lambda: "value"],
                default=inspect.Parameter.empty,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )

        context = ResolveContext(
            dependencies=Dependencies({HTTPConnection: VariableResolver(Request({"type": "http"}))}),
        )
        assert await context.resolve(injection.resolver) == "value"

    async def test_shortcut_one_arg_lambda(self) -> None:
        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                annotation=typing.Annotated[str, lambda r: "value"],
                default=inspect.Parameter.empty,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )

        context = ResolveContext(
            dependencies=Dependencies({HTTPConnection: VariableResolver(Request({"type": "http"}))}),
        )
        assert await context.resolve(injection.resolver) == "value"

    async def test_shortcut_two_arg_lambda(self) -> None:
        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                annotation=typing.Annotated[str, lambda r, arg: "value" + arg.param_name],
                default=inspect.Parameter.empty,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )

        context = ResolveContext(
            dependencies=Dependencies(
                {
                    HTTPConnection: VariableResolver(Request({"type": "http"})),
                    Argument: VariableResolver(
                        Argument(
                            param_name="arg",
                            param_type=str,
                            default=None,
                            annotation=str,
                            nullable=False,
                        )
                    ),
                }
            ),
        )
        assert await context.resolve(injection.resolver) == "valuearg"

    def test_shortcut_three_arg_lambda(self) -> None:
        with pytest.raises(DependencyError, match="should accept zero, one, or two parameters"):
            create_dependency_from_parameter(
                inspect.Parameter(
                    name="dep",
                    annotation=typing.Annotated[str, lambda r, arg, bar: "value"],
                    default=inspect.Parameter.empty,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            )

    def test_generator_function(self) -> None:
        def gen() -> typing.Generator[str, None, None]:
            yield "abc"

        with pytest.raises(DependencyError, match="Generators are not supported"):
            create_dependency_from_parameter(
                inspect.Parameter(
                    name="dep",
                    annotation=typing.Annotated[str, gen],
                    default=inspect.Parameter.empty,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            )

    def test_async_generator_function(self) -> None:
        async def gen() -> typing.AsyncGenerator[str, None]:
            yield "abc"

        with pytest.raises(DependencyError, match="Generators are not supported"):
            create_dependency_from_parameter(
                inspect.Parameter(
                    name="dep",
                    annotation=typing.Annotated[str, gen],
                    default=inspect.Parameter.empty,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            )

    def test_type_alias(self) -> None:
        type Alias = typing.Annotated[str, VariableResolver("abc")]
        injection = create_dependency_from_parameter(
            inspect.Parameter(
                name="dep",
                default=inspect.Parameter.empty,
                annotation=Alias,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        )
        assert injection.dependency.param_type is str
        assert injection.dependency.nullable is False
        assert isinstance(injection.resolver, VariableResolver)


class TestFromPath:
    async def test_from_path_no_type(self) -> None:
        context = ResolveContext(
            dependencies=Dependencies(
                {
                    HTTPConnection: VariableResolver(Request({"type": "http", "path_params": {"path": "abc"}})),
                    Argument: VariableResolver(
                        Argument(param_name="path", param_type=str, default=None, annotation=str, nullable=False)
                    ),
                }
            )
        )
        async with context:
            assert await context.resolve(FromPath) == "abc"

    async def test_from_path_with_type(self) -> None:
        context = ResolveContext(
            dependencies=Dependencies(
                {
                    HTTPConnection: VariableResolver(Request({"type": "http", "path_params": {"path": "42"}})),
                    Argument: VariableResolver(
                        Argument(param_name="path", param_type=int, default=None, annotation=str, nullable=False)
                    ),
                }
            )
        )
        async with context:
            assert await context.resolve(FromPath[int]) == 42
