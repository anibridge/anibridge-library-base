"""Registration utilities for `LibraryProvider` implementations."""

from collections.abc import Callable, Iterator
from typing import overload

from anibridge.library.interfaces import LibraryProvider


class LibraryProviderRegistry:
    """Registry for `LibraryProvider` implementations."""

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._providers: dict[str, type[LibraryProvider]] = {}

    def clear(self) -> None:
        """Remove all provider registrations."""
        self._providers.clear()

    def create(self, namespace: str, *, config: dict | None = None) -> LibraryProvider:
        """Instantiate the provider registered under `namespace`.

        Args:
            namespace (str): The namespace identifier to create.
            config (dict | None): Optional configuration dictionary to pass to the
                provider constructor.

        Returns:
            LibraryProvider: An instance of the registered provider.
        """
        provider_cls = self.get(namespace)
        return provider_cls(config=config)

    def get(self, namespace: str) -> type[LibraryProvider]:
        """Return the provider class registered under `namespace`.

        Args:
            namespace (str): The namespace identifier to look up.

        Returns:
            type[LibraryProvider]: The registered provider class.
        """
        try:
            return self._providers[namespace]
        except KeyError as exc:
            raise LookupError(
                f"No provider registered for namespace '{namespace}'."
            ) from exc

    def namespaces(self) -> tuple[str, ...]:
        """Return a tuple of registered namespace identifiers.

        Returns:
            tuple[str, ...]: The registered namespace identifiers.
        """
        return tuple(self._providers)

    @overload
    def register(
        self,
        provider_cls: type[LibraryProvider],
        *,
        namespace: str | None = None,
    ) -> type[LibraryProvider]: ...

    @overload
    def register(
        self,
        provider_cls: None = None,
        *,
        namespace: str | None = None,
    ) -> Callable[[type[LibraryProvider]], type[LibraryProvider]]: ...

    def register(
        self,
        provider_cls: type[LibraryProvider] | None = None,
        *,
        namespace: str | None = None,
    ) -> (
        type[LibraryProvider]
        | Callable[
            [type[LibraryProvider]],
            type[LibraryProvider],
        ]
    ):
        """Register a provider class, optionally used as a decorator.

        Args:
            provider_cls (type[LibraryProvider] | None): The provider class to register.
                If `None`, the method acts as a decorator factory.
            namespace (str | None): Explicit namespace override. Defaults to the class'
                `NAMESPACE` attribute.

        Returns:
            type[LibraryProvider] | Callable[[type[LibraryProvider]],
                type[LibraryProvider]]: The registered provider class, or a decorator
                that registers the class.
        """

        def decorator(cls: type[LibraryProvider]) -> type[LibraryProvider]:
            """Register `cls` as a provider."""
            resolved_namespace = namespace or getattr(cls, "NAMESPACE", None)
            if not isinstance(resolved_namespace, str) or not resolved_namespace:
                raise ValueError(
                    "Library providers must define a non-empty string `NAMESPACE` "
                    "attribute or pass `namespace=` when registering."
                )

            existing = self._providers.get(resolved_namespace)
            if existing is not None and existing is not cls:
                raise ValueError(
                    f"A provider is already registered for namespace "
                    f"'{resolved_namespace}'."
                )

            self._providers[resolved_namespace] = cls
            return cls

        if provider_cls is None:
            return decorator
        return decorator(provider_cls)

    def unregister(self, namespace: str) -> None:
        """Remove a provider registration if it exists.

        Args:
            namespace (str): The namespace identifier to unregister.
        """
        self._providers.pop(namespace, None)

    def __contains__(self, namespace: object) -> bool:
        """Check if a provider is registered under `namespace`."""
        return isinstance(namespace, str) and namespace in self._providers

    def __iter__(self) -> Iterator[tuple[str, type[LibraryProvider]]]:
        """Iterate over `(namespace, provider_class)` pairs."""
        return iter(self._providers.items())


provider_registry = LibraryProviderRegistry()


def library_provider(
    cls: type[LibraryProvider] | None = None,
    *,
    namespace: str | None = None,
    registry: LibraryProviderRegistry | None = None,
) -> (
    type[LibraryProvider]
    | Callable[
        [type[LibraryProvider]],
        type[LibraryProvider],
    ]
):
    """Class decorator that registers `LibraryProvider` implementations.

    This helper lets third-party providers register themselves declaratively:

        ```
        from anibridge.library import library_provider


        @library_provider(namespace="plex")
        class PlexLibraryProvider:
            NAMESPACE = "plex"
            ...
        ```

    Args:
        cls (type[LibraryProvider]): Optional provider class when used directly instead
            of as a decorator.
        namespace (str): Explicit namespace override. Defaults to the class'
            `NAMESPACE`.
        registry (LibraryProviderRegistry): Alternate registry to insert into. Defaults
            to the module-level one.

    Returns:
        type[LibraryProvider] | Callable[[type[LibraryProvider]],
            type[LibraryProvider]]: The registered provider class, or a decorator that
            registers the class.
    """
    active_registry = registry or provider_registry
    return active_registry.register(cls, namespace=namespace)
