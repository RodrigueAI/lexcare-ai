# app/infrastructure/pdf_loader.py
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pypdf import PdfReader


@dataclass
class LoadedDocument:
    source_path: str
    text: str
    metadata: dict[str, Any]


class PDFLoader:
    def load(self, file_path: str) -> LoadedDocument:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file, got: {file_path}")

        reader = PdfReader(str(path))

        if getattr(reader, "is_encrypted", False):
            try:
                reader.decrypt("")
            except Exception as exc:
                raise ValueError(f"Unable to decrypt PDF: {file_path}") from exc

        pages_text: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append(text.strip())

        full_text = "\n\n".join(pages_text).strip()

        metadata = {
            "filename": path.name,
            "file_size_bytes": path.stat().st_size,
            "page_count": len(reader.pages),
            "pdf_metadata": dict(reader.metadata or {}),
        }

        return LoadedDocument(
            source_path=str(path),
            text=full_text,
            metadata=metadata,
        )
        