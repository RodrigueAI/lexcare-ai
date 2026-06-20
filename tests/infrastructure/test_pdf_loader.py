# tests/infrastructure/test_pdf_loader.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pytest

import app.infrastructure.pdf_loader as pdf_loader_module
from app.infrastructure.pdf_loader import PDFLoader


@dataclass
class FakePage:
    text: str | None

    def extract_text(self) -> str | None:
        return self.text


class FakePdfReader:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.pages = [
            FakePage("First page text"),
            FakePage(""),
            FakePage(None),
            FakePage("Second page text"),
        ]
        self.metadata = {
            "/Title": "Sample PDF",
            "/Author": "Test Author",
        }
        self.is_encrypted = False

    def decrypt(self, password: str) -> bool:
        return True


class FakeEncryptedPdfReader:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.pages = [FakePage("Encrypted content")]
        self.metadata = {}
        self.is_encrypted = True

    def decrypt(self, password: str) -> bool:
        raise RuntimeError("Cannot decrypt")


def test_load_pdf_extracts_text_and_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")

    monkeypatch.setattr(pdf_loader_module, "PdfReader", FakePdfReader)

    loader = PDFLoader()
    created_at = datetime(2024, 1, 1, tzinfo=UTC)

    document = loader.load(
        str(pdf_path),
        source="gesetze-im-internet",
        document_type="law",
        topic="krankenversicherung",
        created_at=created_at,
    )

    assert document.source_path == str(pdf_path)
    assert document.text == "First page text\n\nSecond page text"
    assert document.metadata.source == "gesetze-im-internet"
    assert document.metadata.document_type == "law"
    assert document.metadata.topic == "krankenversicherung"
    assert document.metadata.created_at == created_at
    assert document.metadata.extra["filename"] == "sample.pdf"
    assert document.metadata.extra["page_count"] == 4
    assert document.metadata.extra["pdf_metadata"]["/Title"] == "Sample PDF"


def test_load_pdf_rejects_missing_file() -> None:
    loader = PDFLoader()

    with pytest.raises(FileNotFoundError, match="PDF not found"):
        loader.load(
            "does-not-exist.pdf",
            source="gesetze-im-internet",
            document_type="law",
            topic="krankenversicherung",
        )


def test_load_pdf_rejects_non_pdf_file(tmp_path: Path) -> None:
    text_file = tmp_path / "notes.txt"
    text_file.write_text("hello", encoding="utf-8")

    loader = PDFLoader()

    with pytest.raises(ValueError, match="Expected a PDF file"):
        loader.load(
            str(text_file),
            source="gesetze-im-internet",
            document_type="law",
            topic="krankenversicherung",
        )


def test_load_pdf_raises_when_encrypted_pdf_cannot_be_decrypted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf_path = tmp_path / "encrypted.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")

    monkeypatch.setattr(pdf_loader_module, "PdfReader", FakeEncryptedPdfReader)

    loader = PDFLoader()

    with pytest.raises(ValueError, match="Unable to decrypt PDF"):
        loader.load(
            str(pdf_path),
            source="gesetze-im-internet",
            document_type="law",
            topic="krankenversicherung",
        )
