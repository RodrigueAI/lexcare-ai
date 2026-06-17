# src/app/services/text_cleaning_service.py
import re


class TextCleaningService:
    def clean(self, text: str) -> str:
        if not text or not text.strip():
            return ""

        normalized = text.replace("\r\n", "\n").replace("\r", "\n")

        normalized = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", normalized)
        normalized = re.sub(r"[ \t\f\v]+", " ", normalized)

        lines = [line.strip() for line in normalized.splitlines()]
        normalized = "\n".join(lines)

        normalized = re.sub(r"\n{3,}", "\n\n", normalized)

        return normalized.strip()