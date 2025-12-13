"""Anibridge library provider interfaces package."""

from anibridge.library.interfaces import (
    ExternalId,
    HistoryEntry,
    IdNameSpace,
    LibraryEpisode,
    LibraryMedia,
    LibraryMovie,
    LibraryProvider,
    LibrarySeason,
    LibrarySection,
    LibraryShow,
    LibraryUser,
    MappingDescriptor,
    MappingEdge,
    MappingGraph,
    MediaKind,
)
from anibridge.library.registry import (
    LibraryProviderRegistry,
    library_provider,
    provider_registry,
)

__all__ = [
    "ExternalId",
    "HistoryEntry",
    "IdNameSpace",
    "LibraryEpisode",
    "LibraryMedia",
    "LibraryMovie",
    "LibraryProvider",
    "LibraryProviderRegistry",
    "LibrarySeason",
    "LibrarySection",
    "LibraryShow",
    "LibraryUser",
    "MappingDescriptor",
    "MappingEdge",
    "MappingGraph",
    "MediaKind",
    "library_provider",
    "provider_registry",
]
