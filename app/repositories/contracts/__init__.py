# app/repositories/contracts/__init__.py
from .document import (
    DocumentListRepositoryProtocol,
    DocumentReadRepositoryProtocol,
    DocumentWriteRepositoryProtocol,
)
from .ingestion import IngestionIndexRepositoryProtocol
from .source import SourceRegistryProtocol
from .versioning import DocumentVersionRepositoryProtocol
from .warehouse import (
    HubDocumentRepositoryProtocol,
    HubSourceLookupRepositoryProtocol,
    HubSourceRepositoryProtocol,
    HubTopicRepositoryProtocol,
)

__all__ = [
    "DocumentListRepositoryProtocol",
    "DocumentReadRepositoryProtocol",
    "DocumentWriteRepositoryProtocol",
    "DocumentVersionRepositoryProtocol",
    "HubDocumentRepositoryProtocol",
    "HubSourceLookupRepositoryProtocol",
    "HubSourceRepositoryProtocol",
    "HubTopicRepositoryProtocol",
    "IngestionIndexRepositoryProtocol",
    "SourceRegistryProtocol",
]
