# notebooks/_bootstrap.py
from __future__ import annotations

import sys
from pathlib import Path


def get_project_root() -> Path:
    current = Path.cwd()

    candidates = [current, current.parent, current.parent.parent]
    for candidate in candidates:
        if (candidate / "pyproject.toml").exists():
            return candidate

    raise RuntimeError("Could not resolve project root. Expected a pyproject.toml file.")


PROJECT_ROOT = get_project_root()
SRC_DIR = PROJECT_ROOT / "src"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"


def find_pdfs() -> list[Path]:
    if not RAW_DIR.exists():
        return []
    return sorted(RAW_DIR.rglob("*.pdf"))


def find_pdf_subdirs() -> list[Path]:
    if not RAW_DIR.exists():
        return []
    return sorted([p for p in RAW_DIR.iterdir() if p.is_dir()])


def find_pdfs_in(subdir: str) -> list[Path]:
    target_dir = RAW_DIR / subdir
    if not target_dir.exists():
        return []
    return sorted(target_dir.rglob("*.pdf"))
