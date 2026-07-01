# app/domain/keys.py
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse
from uuid import NAMESPACE_URL, uuid5


class WarehouseKeyFactory:
    @staticmethod
    def _clean(value: str) -> str:
        cleaned = value.strip().lower()
        cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
        cleaned = re.sub(r"_+", "_", cleaned)
        return cleaned.strip("_") or "unknown"

    @classmethod
    def create_surrogate_key(cls, namespace: str, business_key: str) -> str:
        return str(uuid5(NAMESPACE_URL, f"{namespace}::{business_key}"))

    @classmethod
    def create_source_key(cls, source_id: str) -> str:
        return cls.create_surrogate_key("source", cls._clean(source_id))

    @classmethod
    def build_topic_id(cls, topic_name: str) -> str:
        return cls._clean(topic_name)

    @classmethod
    def create_topic_key(cls, topic_id: str) -> str:
        return cls.create_surrogate_key("topic", topic_id)

    @classmethod
    def build_document_id(cls, source_id: str, source_path: str) -> str:
        parsed = urlparse(source_path)
        if parsed.scheme == "file":
            file_name = Path(unquote(parsed.path)).name
        else:
            file_name = Path(source_path).name

        return f"{cls._clean(source_id)}::{cls._clean(file_name)}"

    @classmethod
    def create_document_key(cls, document_id: str) -> str:
        return cls.create_surrogate_key("document", document_id)

    @classmethod
    def create_link_key(cls, document_key: str, topic_key: str) -> str:
        return cls.create_surrogate_key("link", f"{document_key}::{topic_key}")

    @classmethod
    def create_satellite_key(cls, namespace: str, document_key: str, hash_diff: str) -> str:
        return cls.create_surrogate_key(namespace, f"{document_key}::{hash_diff}")

    @classmethod
    def create_satellite_metadata_key(cls, document_key: str, hash_diff: str) -> str:
        return cls.create_satellite_key("satellite_document_metadata", document_key, hash_diff)

    @classmethod
    def create_satellite_content_key(cls, document_key: str, hash_diff: str) -> str:
        return cls.create_satellite_key("satellite_document_content", document_key, hash_diff)
