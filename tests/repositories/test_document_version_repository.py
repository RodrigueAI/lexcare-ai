from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from app.domain.versioning import DocumentVersion
from app.repositories.document_version_repository import FileDocumentVersionRepository


def _make_version(version_number: int, is_current: bool = True) -> DocumentVersion:
    return DocumentVersion(
        document_id=f"doc-{version_number}",
        source_id="gesetze-im-internet",
        artifact_uri="file:///SGB_5.pdf",
        version_number=version_number,
        content_hash=f"hash-{version_number}",
        effective_from=datetime(2024, 1, version_number, tzinfo=UTC),
        effective_to=None,
        is_current=is_current,
        metadata={"filename": "SGB_5.pdf"},
    )


def test_save_and_load_versions(tmp_path: Path) -> None:
    repo = FileDocumentVersionRepository(storage_path=str(tmp_path / "versions.json"))

    version_1 = _make_version(1)
    version_2 = _make_version(2)

    repo.save_version(version_1)
    repo.save_version(version_2)

    versions = repo.load_all()

    assert len(versions) == 2
    assert versions[0].version_number == 1
    assert versions[1].version_number == 2


def test_find_latest_returns_highest_version_number(tmp_path: Path) -> None:
    repo = FileDocumentVersionRepository(storage_path=str(tmp_path / "versions.json"))

    repo.save_version(_make_version(1))
    repo.save_version(_make_version(2))

    latest = repo.find_latest("gesetze-im-internet", "file:///SGB_5.pdf")

    assert latest is not None
    assert latest.version_number == 2


def test_update_version_replaces_existing_record(tmp_path: Path) -> None:
    repo = FileDocumentVersionRepository(storage_path=str(tmp_path / "versions.json"))

    version_1 = _make_version(1)
    repo.save_version(version_1)

    closed_version = DocumentVersion(
        document_id=version_1.document_id,
        source_id=version_1.source_id,
        artifact_uri=version_1.artifact_uri,
        version_number=version_1.version_number,
        content_hash=version_1.content_hash,
        effective_from=version_1.effective_from,
        effective_to=datetime(2024, 1, 2, tzinfo=UTC),
        is_current=False,
        metadata=version_1.metadata,
    )

    repo.update_version(closed_version)

    loaded = repo.load_all()
    assert loaded[0].is_current is False
    assert loaded[0].effective_to == datetime(2024, 1, 2, tzinfo=UTC)