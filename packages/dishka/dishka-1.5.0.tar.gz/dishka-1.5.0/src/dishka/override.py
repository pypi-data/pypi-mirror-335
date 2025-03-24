from collections.abc import AsyncIterator, Iterator
from contextlib import contextmanager
from typing import TypeVar

from dishka import (
    DEFAULT_COMPONENT,
    AsyncContainer,
    Container,
    make_async_container,
    make_container,
)
from dishka.provider import BaseProvider


def _container_provider(container: Container | AsyncContainer) -> BaseProvider:
    container_provider = BaseProvider(component=DEFAULT_COMPONENT)
    container_provider.factories.extend(container.registry.factories.values())
    for registry in container.child_registries:
        container_provider.factories.extend(registry.factories.values())
    return container_provider


CT = TypeVar("CT", Container, AsyncContainer)
def _swap(c1: CT, c2: CT) -> None:
    for attr in type(c1).__slots__:
        tmp = getattr(c1, attr)
        setattr(c1, attr, getattr(c2, attr))
        setattr(c2, attr, tmp)

@contextmanager
def override(container: Container, *providers: BaseProvider) -> Iterator[None]:
    new_container = make_container(_container_provider(container), *providers)
    _swap(container, new_container)
    yield
    container.close()
    _swap(new_container, container)



@contextmanager
async def override_async(
        container: AsyncContainer, *providers: BaseProvider,
) -> AsyncIterator[None]:
    new_container = make_async_container(_container_provider(container), *providers)
    _swap(container, new_container)
    yield
    await container.close()
    _swap(new_container, container)


