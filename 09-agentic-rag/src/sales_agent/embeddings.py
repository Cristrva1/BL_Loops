"""Cliente sin dependencias para POST /api/embed de Ollama local."""

from __future__ import annotations

import json
import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

EMBEDDING_PROFILE = "qwen3-sales-agent-hybrid-filtered-v1"
QUERY_INSTRUCTION = (
    "Given a sales question in Spanish or English, retrieve passages that help answer it"
)


class EmbeddingError(RuntimeError):
    """La operacion de embeddings no produjo vectores utilizables."""


@dataclass(frozen=True, slots=True)
class EmbeddingBatch:
    vectors: tuple[tuple[float, ...], ...]
    total_duration_ms: float | None
    prompt_tokens: int | None


OpenUrl = Callable[..., Any]


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, *_args: object, **_kwargs: object) -> None:
        return None


class EmbeddingClient:
    profile = EMBEDDING_PROFILE

    def __init__(
        self,
        base_url: str,
        model: str,
        dimensions: int,
        timeout_seconds: float,
        opener: OpenUrl | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.dimensions = dimensions
        self.timeout_seconds = timeout_seconds
        self._opener = opener or build_opener(ProxyHandler({}), _NoRedirectHandler()).open

    def embed_documents(self, texts: list[str]) -> EmbeddingBatch:
        if not texts:
            raise EmbeddingError("No hay documentos para convertir en vectores.")
        return self._embed(texts, expected_count=len(texts))

    def embed_query(self, text: str) -> EmbeddingBatch:
        query = text.strip()
        if not query:
            raise EmbeddingError("La consulta para embeddings esta vacia.")
        instructed = f"Instruct: {QUERY_INSTRUCTION}\nQuery: {query}"
        return self._embed(instructed, expected_count=1)

    def _embed(self, value: str | list[str], *, expected_count: int) -> EmbeddingBatch:
        payload = {
            "model": self.model,
            "input": value,
            "dimensions": self.dimensions,
            "truncate": False,
        }
        request = Request(
            f"{self.base_url}/api/embed",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "BL-Loops-Sales-Agent/0.1"},
            method="POST",
        )
        try:
            with self._opener(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as exc:
            detail = _error_detail(exc)
            if exc.code == 404:
                raise EmbeddingError(
                    f"Ollama no encontro '{self.model}'. Compruebalo con: ollama list"
                ) from exc
            raise EmbeddingError(f"Ollama respondio HTTP {exc.code}: {detail}") from exc
        except TimeoutError as exc:
            raise EmbeddingError(
                f"Ollama tardo mas de {self.timeout_seconds:g} segundos al crear embeddings."
            ) from exc
        except URLError as exc:
            raise EmbeddingError("No se pudo conectar con Ollama local para embeddings.") from exc

        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EmbeddingError("Ollama devolvio embeddings que no son JSON valido.") from exc
        if not isinstance(decoded, dict):
            raise EmbeddingError("Ollama devolvio un contrato de embeddings inesperado.")
        vectors = decoded.get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != expected_count:
            raise EmbeddingError("Ollama devolvio una cantidad inesperada de embeddings.")
        normalized = tuple(_normalize_vector(vector, self.dimensions) for vector in vectors)
        return EmbeddingBatch(
            normalized,
            _milliseconds(decoded.get("total_duration")),
            _optional_int(decoded.get("prompt_eval_count")),
        )


def _normalize_vector(value: object, dimensions: int) -> tuple[float, ...]:
    if not isinstance(value, list) or len(value) != dimensions:
        raise EmbeddingError(f"El vector no tiene las {dimensions} dimensiones configuradas.")
    try:
        vector = tuple(float(item) for item in value)
    except (TypeError, ValueError) as exc:
        raise EmbeddingError("El vector contiene valores no numericos.") from exc
    if not all(math.isfinite(item) for item in vector):
        raise EmbeddingError("El vector contiene valores no finitos.")
    norm = math.sqrt(math.fsum(item * item for item in vector))
    if norm <= 1e-12:
        raise EmbeddingError("Ollama devolvio un vector nulo.")
    return tuple(item / norm for item in vector)


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _milliseconds(value: object) -> float | None:
    raw = _optional_int(value)
    return round(raw / 1_000_000, 3) if raw is not None else None


def _error_detail(error: HTTPError) -> str:
    try:
        decoded = json.loads(error.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "error local sin detalle util"
    detail = decoded.get("error") if isinstance(decoded, dict) else None
    return detail[:240] if isinstance(detail, str) else "error local sin detalle util"
