# app/services/ingestion_service.py
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.core.config import Settings, get_settings
from app.domain.models import StoredDocument
from app.infrastructure.pdf_loader import PDFLoader
from app.repositories.document_repository import DocumentRepository, FileDocumentRepository


class IngestionService:
    def __init__(
        self,
        pdf_loader: PDFLoader | None = None,
        repository: DocumentRepository | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.pdf_loader = pdf_loader or PDFLoader()
        self.repository = repository or FileDocumentRepository()
        self.raw_upload_dir = Path(self.settings.raw_upload_dir)
        self.raw_upload_dir.mkdir(parents=True, exist_ok=True)

    def ingest_pdf_bytes(
        self,
        *,
        file_name: str,
        content: bytes,
        source: str,
        document_type: str,
        topic: str,
    ) -> StoredDocument:
        if not file_name.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported.")

        if not content:
            raise ValueError("Uploaded file is empty.")

        raw_pdf_path = self._save_raw_pdf(
            file_name=file_name,
            content=content,
            source=source,
            document_type=document_type,
        )

        loaded_document = self.pdf_loader.load(
            str(raw_pdf_path),
            source=source,
            document_type=document_type,
            topic=topic,
        )

        return self.repository.save(loaded_document)

    def _save_raw_pdf(
        self,
        *,
        file_name: str,
        content: bytes,
        source: str,
        document_type: str,
    ) -> Path:
        safe_name = Path(file_name).name
        source_dir = self._safe_segment(source)
        document_type_dir = self._safe_segment(document_type)

        target_dir = self.raw_upload_dir / source_dir / document_type_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / f"{uuid4()}_{safe_name}"
        target_path.write_bytes(content)

        return target_path

    def _safe_segment(self, value: str) -> str:
        cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value.strip())
        cleaned = "_".join(part for part in cleaned.split("_") if part)
        return cleaned or "unknown"
