"""Huellas SHA-256 reproducibles para detectar cambios o manipulación."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_payload(value: BaseModel | dict[str, Any]) -> dict[str, Any]:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else dict(value)
    payload.pop("content_hash", None)
    return payload


def compute_content_hash(value: BaseModel | dict[str, Any]) -> str:
    encoded = json.dumps(
        canonical_payload(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def with_content_hash[T: BaseModel](value: T) -> T:
    return value.model_copy(update={"content_hash": compute_content_hash(value)})


def has_valid_content_hash(value: BaseModel) -> bool:
    actual = getattr(value, "content_hash", None)
    return isinstance(actual, str) and actual == compute_content_hash(value)
