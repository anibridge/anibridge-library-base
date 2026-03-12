"""Tests for the library provider base classes."""

import asyncio
import logging
from collections.abc import Sequence
from datetime import UTC, datetime

from starlette.requests import Request

from anibridge.library import HistoryEntry, LibraryEntry, LibraryMedia, LibraryProvider
from anibridge.library.base import LibrarySection, LibraryUser, MediaKind


class DummyLibraryProvider(LibraryProvider):
    """Concrete provider used to exercise the base implementation."""

    NAMESPACE = "dummy"

    def __init__(self) -> None:
        """Initialize the provider with a test logger."""
        super().__init__(logger=logging.getLogger("tests.library"))

    async def get_sections(self) -> tuple[LibrarySection[DummyLibraryProvider], ...]:
        """Return a single dummy section."""
        return (DummyLibrarySection(self),)

    async def list_items(
        self,
        section: LibrarySection[DummyLibraryProvider],
        *,
        min_last_modified: datetime | None = None,
        require_watched: bool = False,
        keys: Sequence[str] | None = None,
    ) -> Sequence[LibraryEntry[DummyLibraryProvider]]:
        """Return a single dummy entry."""
        return (DummyLibraryEntry(self, section, "item-1"),)

    def user(self) -> LibraryUser | None:
        """Return a stable dummy user."""
        return LibraryUser(key="user-1", title="Test User")


class DummyLibrarySection(LibrarySection[DummyLibraryProvider]):
    """Concrete library section for tests."""

    def __init__(self, provider: DummyLibraryProvider) -> None:
        """Create a dummy section."""
        self._provider = provider
        self._key = "section-1"
        self._title = "Section"
        self._media_kind = MediaKind.SHOW


class DummyLibraryMedia(LibraryMedia[DummyLibraryProvider]):
    """Concrete library media for tests."""

    def __init__(
        self,
        provider: DummyLibraryProvider,
        section: LibrarySection[DummyLibraryProvider],
        key: str,
    ) -> None:
        """Create dummy media metadata."""
        self._provider = provider
        self._key = key
        self._title = "Item"
        self._media_kind = MediaKind.SHOW
        self._section = section


class DummyLibraryEntry(LibraryEntry[DummyLibraryProvider]):
    """Concrete library entry for tests."""

    def __init__(
        self,
        provider: DummyLibraryProvider,
        section: LibrarySection[DummyLibraryProvider],
        key: str,
    ) -> None:
        """Create a dummy library entry."""
        self._provider = provider
        self._section = section
        self._key = key
        self._title = "Item"
        self._media_kind = MediaKind.SHOW
        self._media = DummyLibraryMedia(provider, section, key)

    async def history(self) -> tuple[HistoryEntry, ...]:
        """Return a single history event."""
        return (
            HistoryEntry(
                library_key=self.key,
                viewed_at=datetime(2026, 3, 12, tzinfo=UTC),
            ),
        )

    def mapping_descriptors(self) -> tuple[tuple[str, str, None], ...]:
        """Return a single mapping descriptor."""
        return (("anilist", "1", None),)

    def media(self) -> DummyLibraryMedia:
        """Return the cached media object."""
        return self._media

    @property
    def on_watching(self) -> bool:
        """Return whether the entry is currently being watched."""
        return True

    @property
    def on_watchlist(self) -> bool:
        """Return whether the entry is on the watchlist."""
        return False

    @property
    async def review(self) -> str | None:
        """Return the review text."""
        return "Review"

    def section(self) -> LibrarySection[DummyLibraryProvider]:
        """Return the parent section."""
        return self._section

    @property
    def user_rating(self) -> int | None:
        """Return a normalized user rating."""
        return 90

    @property
    def view_count(self) -> int:
        """Return the view count."""
        return 2


def test_library_provider_default_hooks() -> None:
    """The default provider hooks should be safe no-ops."""
    provider = DummyLibraryProvider()
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/webhook",
            "headers": [],
            "query_string": b"",
        }
    )

    assert asyncio.run(provider.initialize()) is None
    assert asyncio.run(provider.clear_cache()) is None
    assert asyncio.run(provider.close()) is None
    assert asyncio.run(provider.parse_webhook(request)) == (False, ())
    assert provider.user() == LibraryUser(key="user-1", title="Test User")


def test_library_entities_expose_expected_defaults() -> None:
    """Entries should expose the shared helpers defined by the base classes."""
    provider = DummyLibraryProvider()
    section = DummyLibrarySection(provider)
    entry = DummyLibraryEntry(provider, section, "item-1")

    assert entry.media().external_url is None
    assert entry.media().poster_image is None
    assert entry.mapping_descriptors() == (("anilist", "1", None),)
    assert entry.section() is section
    assert hash(provider.user()) == hash("user-1")
    assert entry == DummyLibraryEntry(provider, section, "item-1")
