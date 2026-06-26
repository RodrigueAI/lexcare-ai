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
    HubDocumentLookupRepositoryProtocol,
    HubDocumentRepositoryProtocol,
    HubSourceLookupRepositoryProtocol,
    HubSourceRepositoryProtocol,
    HubTopicLookupRepositoryProtocol,
    HubTopicRepositoryProtocol,
    LinkDocumentTopicRepositoryProtocol,
)

__all__ = [
    "DocumentListRepositoryProtocol",
    "DocumentReadRepositoryProtocol",
    "DocumentWriteRepositoryProtocol",
    "DocumentVersionRepositoryProtocol",
    "HubDocumentLookupRepositoryProtocol",
    "HubDocumentRepositoryProtocol",
    "HubSourceLookupRepositoryProtocol",
    "HubSourceRepositoryProtocol",
    "HubTopicLookupRepositoryProtocol",
    "HubTopicRepositoryProtocol",
    "IngestionIndexRepositoryProtocol",
    "LinkDocumentTopicRepositoryProtocol",
    "SourceRegistryProtocol",
]
