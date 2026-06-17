# src/app/services/document_processing_service.py
from app.domain.models import DocumentChunk, StoredDocument
from app.services.chunking_service import ChunkingService
from app.services.text_cleaning_service import TextCleaningService


class DocumentProcessingService:
    def __init__(
        self,
        cleaning_service: TextCleaningService | None = None,
        chunking_service: ChunkingService | None = None,
    ) -> None:
        self.cleaning_service = cleaning_service or TextCleaningService()
        self.chunking_service = chunking_service or ChunkingService()

    def process(self, document: StoredDocument) -> list[DocumentChunk]:
        cleaned_text = self.cleaning_service.clean(document.text)
        return self.chunking_service.split(document=document, text=cleaned_text)