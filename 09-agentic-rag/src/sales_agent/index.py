"""Proyeccion SQLite exacta y recuperacion hibrida del agente."""

from __future__ import annotations

import hashlib
import math
import os
import re
import sqlite3
import sys
from array import array
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from sales_agent.embeddings import EmbeddingBatch
from sales_agent.quality import PreparedBlock, prepare_markdown

SCHEMA_VERSION = "1"
WORD_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)
STOPWORDS = frozenset(
    {
        "a",
        "algo",
        "al",
        "and",
        "antes",
        "como",
        "con",
        "cual",
        "cuál",
        "de",
        "del",
        "el",
        "en",
        "es",
        "la",
        "las",
        "le",
        "les",
        "lo",
        "los",
        "para",
        "por",
        "que",
        "qué",
        "se",
        "sin",
        "su",
        "sus",
        "the",
        "un",
        "una",
        "y",
    }
)
MODES = frozenset({"lexical", "vector", "hybrid"})
LEXICAL_RRF_WEIGHT = 0.35
VECTOR_RRF_WEIGHT = 0.65


class IndexingError(RuntimeError):
    """El corpus no pudo convertirse en un indice vectorial completo."""


class SearchError(RuntimeError):
    """La recuperacion no puede ejecutarse con el indice disponible."""


class Embedder(Protocol):
    model: str
    dimensions: int
    profile: str

    def embed_documents(self, texts: list[str]) -> EmbeddingBatch: ...

    def embed_query(self, text: str) -> EmbeddingBatch: ...


@dataclass(frozen=True, slots=True)
class BuildStats:
    index_path: Path
    discovered_documents: int
    indexed_documents: int
    duplicate_documents: int
    excluded_sections: int
    unreviewed_documents: int
    chunks: int
    embedded_chunks: int
    embedding_model: str
    dimensions: int
    corpus_hash: str


@dataclass(frozen=True, slots=True)
class SearchResult:
    chunk_id: int
    source_path: str
    title: str
    heading: str
    source_status: str
    start_line: int
    end_line: int
    content: str
    lexical_rank: int | None
    vector_rank: int | None
    lexical_score: float | None
    vector_score: float | None
    fused_score: float


@dataclass(frozen=True, slots=True)
class _Chunk:
    document_id: int
    source_path: str
    title: str
    heading: str
    status: str
    start_line: int
    end_line: int
    content: str


Progress = Callable[[int, int], None]


class HybridSalesIndex:
    def __init__(
        self,
        index_path: Path,
        embedding_model: str,
        dimensions: int,
        embedding_profile: str,
    ) -> None:
        self.index_path = index_path.resolve()
        self.embedding_model = embedding_model
        self.dimensions = dimensions
        self.embedding_profile = embedding_profile

    def build(
        self,
        source_dir: Path,
        *,
        chunk_chars: int,
        batch_size: int,
        embedder: Embedder,
        progress: Progress | None = None,
    ) -> BuildStats:
        source_root = source_dir.resolve()
        if not source_root.is_dir():
            raise IndexingError(f"El directorio fuente no existe: {source_dir}")
        files = sorted(
            source_root.rglob("*.md"),
            key=lambda path: path.relative_to(source_root).as_posix().casefold(),
        )
        if not files:
            raise IndexingError("El directorio no contiene ningun archivo Markdown (.md).")
        if any(path.is_symlink() for path in files):
            raise IndexingError("El corpus contiene un enlace simbolico no permitido.")
        if embedder.model != self.embedding_model or embedder.dimensions != self.dimensions:
            raise IndexingError("El cliente no coincide con el perfil de embeddings del indice.")
        if embedder.profile != self.embedding_profile:
            raise IndexingError("El cliente usa una instruccion de embeddings incompatible.")

        documents: list[tuple[str, str, str, str, int, tuple[PreparedBlock, ...]]] = []
        seen_hashes: set[str] = set()
        duplicates = 0
        excluded_sections = 0
        unreviewed = 0
        corpus_hasher = hashlib.sha256()
        for path in files:
            relative = path.relative_to(source_root).as_posix()
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if digest in seen_hashes:
                duplicates += 1
                continue
            seen_hashes.add(digest)
            try:
                text = raw.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise IndexingError(f"El archivo no es UTF-8 valido: {relative}") from exc
            prepared = prepare_markdown(Path(relative), text)
            excluded_sections += prepared.excluded_sections
            unreviewed += int(prepared.source_status == "unreviewed")
            if not prepared.blocks:
                continue
            documents.append(
                (
                    relative,
                    prepared.title,
                    digest,
                    prepared.source_status,
                    prepared.excluded_sections,
                    prepared.blocks,
                )
            )
            corpus_hasher.update(relative.encode("utf-8"))
            corpus_hasher.update(b"\0")
            corpus_hasher.update(digest.encode("ascii"))
            corpus_hasher.update(b"\n")
        if not documents:
            raise IndexingError("Los Markdown no produjeron contenido confiable indexable.")

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.index_path.with_name(f".{self.index_path.name}.{uuid4().hex}.tmp")
        chunk_count = 0
        try:
            connection = sqlite3.connect(temporary)
            try:
                _create_schema(connection)
                chunks: list[_Chunk] = []
                for relative, title, digest, status, excluded, blocks in documents:
                    prepared_chunks = _chunk_blocks(blocks, chunk_chars)
                    if not prepared_chunks:
                        continue
                    cursor = connection.execute(
                        "INSERT INTO documents(source_path,title,content_hash,source_status,"
                        "excluded_sections,chunk_count) VALUES(?,?,?,?,?,?)",
                        (relative, title, digest, status, excluded, len(prepared_chunks)),
                    )
                    document_id = int(cursor.lastrowid)
                    chunks.extend(
                        _Chunk(
                            document_id,
                            relative,
                            title,
                            block.heading,
                            status,
                            block.start_line,
                            block.end_line,
                            block.text,
                        )
                        for block in prepared_chunks
                    )
                if not chunks:
                    raise IndexingError("El corpus filtrado no produjo fragmentos.")

                total = len(chunks)
                for offset in range(0, total, batch_size):
                    batch_chunks = chunks[offset : offset + batch_size]
                    inputs = [
                        f"{chunk.title}\n{chunk.heading}\n{chunk.content}" for chunk in batch_chunks
                    ]
                    embedded = embedder.embed_documents(inputs)
                    if len(embedded.vectors) != len(batch_chunks):
                        raise IndexingError("El batch de embeddings quedo incompleto.")
                    for chunk, vector in zip(batch_chunks, embedded.vectors, strict=True):
                        digest = hashlib.sha256(chunk.content.encode("utf-8")).hexdigest()
                        cursor = connection.execute(
                            "INSERT INTO chunks("
                            "document_id,source_path,title,heading,source_status,"
                            "start_line,end_line,content,content_hash,vector) "
                            "VALUES(?,?,?,?,?,?,?,?,?,?)",
                            (
                                chunk.document_id,
                                chunk.source_path,
                                chunk.title,
                                chunk.heading,
                                chunk.status,
                                chunk.start_line,
                                chunk.end_line,
                                chunk.content,
                                digest,
                                _pack(vector, self.dimensions),
                            ),
                        )
                        row_id = int(cursor.lastrowid)
                        connection.execute(
                            "INSERT INTO chunks_fts(rowid,title,heading,content) VALUES(?,?,?,?)",
                            (row_id, chunk.title, chunk.heading, chunk.content),
                        )
                        chunk_count += 1
                    if progress is not None:
                        progress(min(offset + len(batch_chunks), total), total)

                metadata = {
                    "schema_version": SCHEMA_VERSION,
                    "built_at": datetime.now(UTC).isoformat(),
                    "embedding_model": self.embedding_model,
                    "embedding_dimensions": str(self.dimensions),
                    "embedding_profile": self.embedding_profile,
                    "discovered_documents": str(len(files)),
                    "indexed_documents": str(len(documents)),
                    "duplicate_documents": str(duplicates),
                    "excluded_sections": str(excluded_sections),
                    "unreviewed_documents": str(unreviewed),
                    "chunks": str(chunk_count),
                    "corpus_hash": corpus_hasher.hexdigest(),
                }
                connection.executemany(
                    "INSERT INTO metadata(key,value) VALUES(?,?)", metadata.items()
                )
                connection.commit()
            finally:
                connection.close()
            os.replace(temporary, self.index_path)
        except (OSError, sqlite3.Error) as exc:
            raise IndexingError(f"No se pudo construir el indice hibrido: {exc}") from exc
        finally:
            temporary.unlink(missing_ok=True)

        return BuildStats(
            self.index_path,
            len(files),
            len(documents),
            duplicates,
            excluded_sections,
            unreviewed,
            chunk_count,
            chunk_count,
            self.embedding_model,
            self.dimensions,
            corpus_hasher.hexdigest(),
        )

    def search(
        self,
        question: str,
        *,
        top_k: int,
        mode: str,
        embedder: Embedder,
    ) -> tuple[SearchResult, ...]:
        normalized_mode = mode.casefold()
        if normalized_mode not in MODES:
            raise SearchError("Modo invalido: usa lexical, vector o hybrid.")
        if not self.index_path.is_file():
            raise SearchError("El indice no existe; ejecuta primero sales-agent index.")
        if not question.strip():
            raise SearchError("La pregunta esta vacia.")
        if not 1 <= top_k <= 12:
            raise SearchError("top_k debe estar entre 1 y 12.")

        try:
            connection = sqlite3.connect(self.index_path)
            connection.row_factory = sqlite3.Row
            try:
                connection.execute("PRAGMA query_only=ON")
                _validate_profile(
                    connection,
                    self.embedding_model,
                    self.dimensions,
                    self.embedding_profile,
                )
                rows = connection.execute(
                    "SELECT id,source_path,title,heading,source_status,start_line,end_line,"
                    "content,vector FROM chunks"
                ).fetchall()
                lexical = _lexical_candidates(connection, question, max(top_k * 4, 12))
            finally:
                connection.close()
        except sqlite3.Error as exc:
            raise SearchError(f"No se pudo consultar SQLite: {exc}") from exc

        row_by_id = {int(row["id"]): row for row in rows}
        lexical_rank = {chunk_id: rank for rank, (chunk_id, _score) in enumerate(lexical, 1)}
        lexical_score = dict(lexical)
        vector: list[tuple[int, float]] = []
        if normalized_mode in {"vector", "hybrid"}:
            if embedder.model != self.embedding_model or embedder.dimensions != self.dimensions:
                raise SearchError("El cliente no coincide con el perfil de embeddings del indice.")
            if embedder.profile != self.embedding_profile:
                raise SearchError("El cliente usa una instruccion de embeddings incompatible.")
            query_vector = embedder.embed_query(question).vectors[0]
            vector = sorted(
                (
                    (
                        chunk_id,
                        math.fsum(
                            a * b
                            for a, b in zip(
                                query_vector,
                                _unpack(row["vector"], self.dimensions),
                                strict=True,
                            )
                        ),
                    )
                    for chunk_id, row in row_by_id.items()
                ),
                key=lambda item: (-item[1], item[0]),
            )[: max(top_k * 4, 12)]
        vector_rank = {chunk_id: rank for rank, (chunk_id, _score) in enumerate(vector, 1)}
        vector_score = dict(vector)

        if normalized_mode == "lexical":
            ordered_ids = [chunk_id for chunk_id, _score in lexical[:top_k]]
            fused = {chunk_id: -lexical_score[chunk_id] for chunk_id in ordered_ids}
        elif normalized_mode == "vector":
            ordered_ids = [chunk_id for chunk_id, _score in vector[:top_k]]
            fused = {chunk_id: vector_score[chunk_id] for chunk_id in ordered_ids}
        else:
            candidates = set(lexical_rank) | set(vector_rank)
            fused = {
                chunk_id: (
                    (
                        LEXICAL_RRF_WEIGHT / (60 + lexical_rank[chunk_id])
                        if chunk_id in lexical_rank
                        else 0
                    )
                    + (
                        VECTOR_RRF_WEIGHT / (60 + vector_rank[chunk_id])
                        if chunk_id in vector_rank
                        else 0
                    )
                )
                for chunk_id in candidates
            }
            ordered_ids = sorted(candidates, key=lambda item: (-fused[item], item))[:top_k]

        return tuple(
            _result(
                row_by_id[chunk_id],
                lexical_rank.get(chunk_id),
                vector_rank.get(chunk_id),
                lexical_score.get(chunk_id),
                vector_score.get(chunk_id),
                fused[chunk_id],
            )
            for chunk_id in ordered_ids
        )

    def current_stats(self) -> BuildStats:
        if not self.index_path.is_file():
            raise SearchError("El indice no existe.")
        try:
            connection = sqlite3.connect(self.index_path)
            try:
                connection.execute("PRAGMA query_only=ON")
                _validate_profile(
                    connection,
                    self.embedding_model,
                    self.dimensions,
                    self.embedding_profile,
                )
                metadata = dict(connection.execute("SELECT key,value FROM metadata"))
            finally:
                connection.close()
        except sqlite3.Error as exc:
            raise SearchError(f"No se pudo inspeccionar SQLite: {exc}") from exc
        return BuildStats(
            self.index_path,
            int(metadata["discovered_documents"]),
            int(metadata["indexed_documents"]),
            int(metadata["duplicate_documents"]),
            int(metadata["excluded_sections"]),
            int(metadata["unreviewed_documents"]),
            int(metadata["chunks"]),
            int(metadata["chunks"]),
            metadata["embedding_model"],
            int(metadata["embedding_dimensions"]),
            metadata["corpus_hash"],
        )


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA journal_mode=DELETE;
        CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE documents(
            id INTEGER PRIMARY KEY,
            source_path TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            content_hash TEXT NOT NULL UNIQUE,
            source_status TEXT NOT NULL,
            excluded_sections INTEGER NOT NULL,
            chunk_count INTEGER NOT NULL
        );
        CREATE TABLE chunks(
            id INTEGER PRIMARY KEY,
            document_id INTEGER NOT NULL REFERENCES documents(id),
            source_path TEXT NOT NULL,
            title TEXT NOT NULL,
            heading TEXT NOT NULL,
            source_status TEXT NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            content TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            vector BLOB NOT NULL
        );
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            title,heading,content,tokenize='unicode61 remove_diacritics 2'
        );
        """
    )


def _validate_profile(
    connection: sqlite3.Connection, model: str, dimensions: int, profile: str
) -> None:
    metadata = dict(connection.execute("SELECT key,value FROM metadata"))
    if metadata.get("schema_version") != SCHEMA_VERSION:
        raise SearchError("El schema del indice es incompatible; vuelve a indexar.")
    if (
        metadata.get("embedding_model") != model
        or metadata.get("embedding_dimensions") != str(dimensions)
        or metadata.get("embedding_profile") != profile
    ):
        raise SearchError("El indice no coincide con el perfil de embeddings configurado.")


def _lexical_candidates(
    connection: sqlite3.Connection, question: str, limit: int
) -> list[tuple[int, float]]:
    terms = _query_terms(question)
    if not terms:
        return []
    expression = " OR ".join(f'"{term}"*' for term in terms)
    rows = connection.execute(
        "SELECT c.id,bm25(chunks_fts,3.0,2.0,1.0) AS score "
        "FROM chunks_fts JOIN chunks c ON c.id=chunks_fts.rowid "
        "WHERE chunks_fts MATCH ? ORDER BY score,c.id LIMIT ?",
        (expression, limit),
    ).fetchall()
    return [(int(row[0]), float(row[1])) for row in rows]


def _query_terms(question: str) -> list[str]:
    raw = [term for term in WORD_PATTERN.findall(question.casefold()) if len(term) >= 2]
    unique = list(dict.fromkeys(raw))
    useful = [term for term in unique if term not in STOPWORDS]
    return useful or unique


def _chunk_blocks(blocks: tuple[PreparedBlock, ...], max_chars: int) -> list[PreparedBlock]:
    expanded: list[PreparedBlock] = []
    for block in blocks:
        if len(block.text) <= max_chars:
            expanded.append(block)
            continue
        words = block.text.split()
        active = ""
        for word in words:
            candidate = f"{active} {word}".strip()
            if active and len(candidate) > max_chars:
                expanded.append(
                    PreparedBlock(active, block.heading, block.start_line, block.end_line)
                )
                active = word
            else:
                active = candidate
        if active:
            expanded.append(PreparedBlock(active, block.heading, block.start_line, block.end_line))

    chunks: list[PreparedBlock] = []
    active_blocks: list[PreparedBlock] = []
    active_chars = 0

    def flush() -> None:
        nonlocal active_blocks, active_chars
        if not active_blocks:
            return
        chunks.append(
            PreparedBlock(
                "\n\n".join(block.text for block in active_blocks),
                active_blocks[0].heading,
                active_blocks[0].start_line,
                active_blocks[-1].end_line,
            )
        )
        active_blocks = []
        active_chars = 0

    for block in expanded:
        separator = 2 if active_blocks else 0
        heading_changed = bool(active_blocks and active_blocks[0].heading != block.heading)
        if active_blocks and (
            heading_changed or active_chars + separator + len(block.text) > max_chars
        ):
            flush()
            separator = 0
        active_blocks.append(block)
        active_chars += separator + len(block.text)
    flush()
    return chunks


def _pack(vector: tuple[float, ...], dimensions: int) -> bytes:
    if len(vector) != dimensions:
        raise IndexingError("El vector no coincide con la dimension configurada.")
    values = array("f", vector)
    if sys.byteorder != "little":
        values.byteswap()
    return values.tobytes()


def _unpack(blob: bytes, dimensions: int) -> tuple[float, ...]:
    values = array("f")
    values.frombytes(blob)
    if sys.byteorder != "little":
        values.byteswap()
    if len(values) != dimensions:
        raise SearchError("Un vector almacenado tiene una dimension incompatible.")
    return tuple(values)


def _result(
    row: sqlite3.Row,
    lexical_rank: int | None,
    vector_rank: int | None,
    lexical_score: float | None,
    vector_score: float | None,
    fused_score: float,
) -> SearchResult:
    return SearchResult(
        int(row["id"]),
        str(row["source_path"]),
        str(row["title"]),
        str(row["heading"]),
        str(row["source_status"]),
        int(row["start_line"]),
        int(row["end_line"]),
        str(row["content"]),
        lexical_rank,
        vector_rank,
        lexical_score,
        vector_score,
        fused_score,
    )
