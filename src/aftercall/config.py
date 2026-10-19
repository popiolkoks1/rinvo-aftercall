from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


@lru_cache
def settings() -> dict:
    return yaml.safe_load((ROOT / "config" / "settings.yaml").read_text())


@lru_cache
def taxonomy() -> dict:
    return yaml.safe_load((ROOT / "config" / "taxonomy.yaml").read_text())


def prompt(name: str) -> str:
    return (ROOT / "prompts" / f"{name}.md").read_text()


def path(key: str) -> Path:
    return ROOT / settings()["paths"][key]


def gemini_model() -> str:
    return os.environ.get("GEMINI_MODEL") or "gemini-2.5-flash"


def gemini_key() -> str | None:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
