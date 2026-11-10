"""Indice SQLite de documentos, aristas extraidas y recuperacion multi-hop."""

from __future__ import annotations

import hashlib
import os
import re
import sqlite3
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from graph_rag.extract import ExtractError, extract_triples, match_entities

SCHEMA_VERSION = "1"
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
WORD_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)
STOPWORDS = frozenset(
    {
        "a",
        "al",
        "and",
        "como",
        "con",
        "cual",
        "cuál",
        "de",
        "del",
        "el",
        "en",
        "es",
        "for",
        "how",
        "la",
        "las",
        "los",
        "of",
        "para",
        "por",
        "que",
        "qué",
        "se",
        "the",
        "un",
        "una",
        "what",
        "y",
    }
)


class IndexingError(RuntimeError):
    """El corpus no pudo convertirse en un grafo valido."""


class SearchError(RuntimeError):
    """La consulta no puede ejecutarse con el indice disponible."""


@dataclass(frozen=True, slots=True)
class BuildStats:
    index_path: Path
    discovered_documents: int
    indexed_documents: int
    duplicate_documents: int
    chunks: int
    nodes: int
    extracted_edges: int
    corpus_hash: str


@dataclass(frozen=True, slots=True)
class LexicalHit:
    chunk_id: int
    source_path: str
    title: str
    heading: str
    start_line: int
    end_line: int
    content: str
    score: float


@dataclass(frozen=True, slots=True)
class PathHop:
    subject: str
    predicate: str
    object: str
    direction: str
    origin: str
    source_path: str
    start_line: int
    end_line: int


@dataclass(frozen=True, slots=True)
class InferredEdge:
    subject: str
    predicate: str
    object: str
    hops: int
    origin: str = "inferred"


@dataclass(frozen=True, slots=True)
class GraphPath:
    hops: tuple[PathHop, ...]
    inferred: InferredEdge | None


@dataclass(frozen=True, slots=True)
class GraphRetrieval:
    seeds: tuple[str, ...]
    paths: tuple[GraphPath, ...]
    nodes_visited: int
    edges_traversed: int


@dataclass(frozen=True, slots=True)
class SearchBundle:
    graph: GraphRetrieval | None
    lexical: tuple[LexicalHit, ...]


@dataclass(frozen=True, slots=True)
class _Block:
    text: str
    heading: str
    start_line: int
    end_line: int


@dataclass(frozen=True, slots=True)
class _Chunk:
    title: str
    heading: str
    start_line: int
    end_line: int
    content: str


@dataclass(frozen=True, slots=True)
class _EdgeRow:
    predicate: str
    source_path: str
    start_line: int
    end_line: int
    subject_id: int
    object_id: int


class GraphIndex:
    def __init__(self, index_path: Path) -> None:
        self.index_path = index_path.resolve()

    def build(self, source_dir: Path, *, chunk_chars: int) -> BuildStats:
        source_root = source_dir.resolve()
        if not source_root.is_dir():
            raise IndexingError(f"El directorio fuente no existe: {source_dir}")
        if not 400 <= chunk_chars <= 4000:
            raise IndexingError("chunk_chars debe estar entre 400 y 4000.")
        markdown_files = sorted(
            source_root.rglob("*.md"),
            key=lambda path: path.relative_to(source_root).as_posix().casefold(),
        )
        if not markdown_files:
            raise IndexingError("El directorio no contiene ningun archivo Markdown (.md).")
        symlinks = [path for path in markdown_files if path.is_symlink()]
        if symlinks:
            relative = symlinks[0].relative_to(source_root).as_posix()
            raise IndexingError(f"No se admite un enlace simbolico en el corpus: {relative}")

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.index_path.with_name(f".{self.index_path.name}.{uuid4().hex}.tmp")
        discovered = len(markdown_files)
        indexed = 0
        duplicates = 0
        chunk_count = 0
        edge_count = 0
        seen_document_hashes: set[str] = set()
        node_ids: dict[str, int] = {}
        corpus_hasher = hashlib.sha256()

        try:
            connection = sqlite3.connect(temporary_path)
            try:
                _create_schema(connection)
                for path in markdown_files:
                    relative_path = path.relative_to(source_root).as_posix()
                    raw_bytes = path.read_bytes()
                    document_hash = hashlib.sha256(raw_bytes).hexdigest()
                    if document_hash in seen_document_hashes:
                        duplicates += 1
                        continue
                    seen_document_hashes.add(document_hash)
                    try:
                        text = raw_bytes.decode("utf-8-sig")
                    except UnicodeDecodeError as exc:
                        raise IndexingError(
                            f"El archivo no es UTF-8 valido: {relative_path}"
                        ) from exc
                    try:
                        triples = extract_triples(text)
                    except ExtractError as exc:
                        raise IndexingError(f"{relative_path}: {exc}") from exc
                    title, chunks = _chunk_markdown(path, text, chunk_chars)
                    if not chunks:
                        continue
                    cursor = connection.execute(
                        "INSERT INTO documents(source_path, title, content_hash, chunk_count) "
                        "VALUES (?, ?, ?, ?)",
                        (relative_path, title, document_hash, len(chunks)),
                    )
                    document_id = int(cursor.lastrowid)
                    for chunk in chunks:
                        chunk_hash = hashlib.sha256(chunk.content.encode("utf-8")).hexdigest()
                        chunk_cursor = connection.execute(
                            "INSERT INTO chunks("
                            "document_id, source_path, title, heading, start_line, end_line, "
                            "content, content_hash"
                            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (
                                document_id,
                                relative_path,
                                chunk.title,
                                chunk.heading,
                                chunk.start_line,
                                chunk.end_line,
                                chunk.content,
                                chunk_hash,
                            ),
                        )
                        connection.execute(
                            "INSERT INTO chunks_fts(rowid, title, heading, content) "
                            "VALUES (?, ?, ?, ?)",
                            (
                                int(chunk_cursor.lastrowid),
                                chunk.title,
                                chunk.heading,
                                chunk.content,
                            ),
                        )
                        chunk_count += 1
                    for triple in triples:
                        subject_id = _upsert_node(connection, node_ids, triple.subject)
                        object_id = _upsert_node(connection, node_ids, triple.object)
                        connection.execute(
                            "INSERT INTO edges("
                            "subject_id, object_id, predicate, origin, document_id, "
                            "source_path, start_line, end_line"
                            ") VALUES (?, ?, ?, 'extracted', ?, ?, ?, ?)",
                            (
                                subject_id,
                                object_id,
                                triple.predicate,
                                document_id,
                                relative_path,
                                triple.start_line,
                                triple.end_line,
                            ),
                        )
                        edge_count += 1
                    indexed += 1
                    corpus_hasher.update(relative_path.encode("utf-8"))
                    corpus_hasher.update(b"\0")
                    corpus_hasher.update(document_hash.encode("ascii"))
                    corpus_hasher.update(b"\n")
                if indexed == 0 or chunk_count == 0:
                    raise IndexingError("Los Markdown no produjeron ningun fragmento indexable.")
                if edge_count == 0:
                    raise IndexingError("El corpus no produjo ninguna arista extraida.")
                corpus_hash = corpus_hasher.hexdigest()
                metadata = {
                    "schema_version": SCHEMA_VERSION,
                    "built_at": datetime.now(UTC).isoformat(),
                    "discovered_documents": str(discovered),
                    "indexed_documents": str(indexed),
                    "duplicate_documents": str(duplicates),
                    "chunks": str(chunk_count),
                    "nodes": str(len(node_ids)),
                    "extracted_edges": str(edge_count),
                    "chunk_chars": str(chunk_chars),
                    "corpus_hash": corpus_hash,
                }
                connection.executemany(
                    "INSERT INTO metadata(key, value) VALUES (?, ?)", metadata.items()
                )
                connection.commit()
            finally:
                connection.close()
            os.replace(temporary_path, self.index_path)
        except (OSError, sqlite3.Error) as exc:
            raise IndexingError(f"No se pudo construir el indice local: {exc}") from exc
        finally:
            temporary_path.unlink(missing_ok=True)

        return BuildStats(
            index_path=self.index_path,
            discovered_documents=discovered,
            indexed_documents=indexed,
            duplicate_documents=duplicates,
            chunks=chunk_count,
            nodes=len(node_ids),
            extracted_edges=edge_count,
            corpus_hash=corpus_hash,
        )

    def current_stats(self) -> BuildStats:
        metadata = self._metadata()
        return BuildStats(
            index_path=self.index_path,
            discovered_documents=int(metadata["discovered_documents"]),
            indexed_documents=int(metadata["indexed_documents"]),
            duplicate_documents=int(metadata["duplicate_documents"]),
            chunks=int(metadata["chunks"]),
            nodes=int(metadata["nodes"]),
            extracted_edges=int(metadata["extracted_edges"]),
            corpus_hash=metadata["corpus_hash"],
        )

    def stored_origins(self) -> tuple[str, ...]:
        connection = self._connect(query_only=True)
        try:
            rows = connection.execute(
                "SELECT DISTINCT origin FROM edges ORDER BY origin"
            ).fetchall()
        finally:
            connection.close()
        return tuple(str(row[0]) for row in rows)

    def search(
        self,
        question: str,
        *,
        top_k: int,
        mode: str,
        max_hops: int,
    ) -> SearchBundle:
        if mode not in {"graph", "lexical", "compare"}:
            raise SearchError("El modo debe ser graph, lexical o compare.")
        graph = None if mode == "lexical" else self.search_graph(question, max_hops=max_hops)
        lexical: tuple[LexicalHit, ...] = ()
        if mode in {"lexical", "compare"}:
            lexical = tuple(self.search_lexical(question, top_k=top_k))
        return SearchBundle(graph=graph, lexical=lexical)

    def search_lexical(self, question: str, *, top_k: int) -> list[LexicalHit]:
        self._ensure_index()
        if not 1 <= top_k <= 10:
            raise SearchError("top_k debe estar entre 1 y 10.")
        terms = _query_terms(question)
        if not terms:
            raise SearchError("La pregunta no contiene palabras buscables.")
        match_expression = " OR ".join(f'"{term}"*' for term in terms)
        connection = self._connect(query_only=True)
        try:
            rows = connection.execute(
                "SELECT c.id, c.source_path, c.title, c.heading, c.start_line, "
                "c.end_line, c.content, bm25(chunks_fts, 3.0, 2.0, 1.0) AS score "
                "FROM chunks_fts JOIN chunks AS c ON c.id = chunks_fts.rowid "
                "WHERE chunks_fts MATCH ? ORDER BY score, c.id LIMIT ?",
                (match_expression, top_k),
            ).fetchall()
        except sqlite3.Error as exc:
            raise SearchError(f"El indice SQLite no se pudo consultar: {exc}") from exc
        finally:
            connection.close()
        return [
            LexicalHit(
                chunk_id=int(row["id"]),
                source_path=str(row["source_path"]),
                title=str(row["title"]),
                heading=str(row["heading"]),
                start_line=int(row["start_line"]),
                end_line=int(row["end_line"]),
                content=str(row["content"]),
                score=float(row["score"]),
            )
            for row in rows
        ]

    def search_graph(self, question: str, *, max_hops: int) -> GraphRetrieval:
        self._ensure_index()
        if not question.strip():
            raise SearchError("La pregunta no puede estar vacia.")
        if not 1 <= max_hops <= 6:
            raise SearchError("max_hops debe estar entre 1 y 6.")
        connection = self._connect(query_only=True)
        try:
            node_rows = connection.execute("SELECT id, label FROM nodes ORDER BY id").fetchall()
            edge_rows = connection.execute(
                "SELECT subject_id, object_id, predicate, source_path, start_line, end_line "
                "FROM edges"
            ).fetchall()
        finally:
            connection.close()
        labels = [str(row["label"]) for row in node_rows]
        id_by_label = {str(row["label"]): int(row["id"]) for row in node_rows}
        label_by_id = {int(row["id"]): str(row["label"]) for row in node_rows}
        seeds = match_entities(question, labels)
        seed_ids = tuple(id_by_label[label] for label in seeds)
        adjacency: dict[int, list[tuple[int, _EdgeRow, str]]] = defaultdict(list)
        for row in edge_rows:
            edge = _EdgeRow(
                predicate=str(row["predicate"]),
                source_path=str(row["source_path"]),
                start_line=int(row["start_line"]),
                end_line=int(row["end_line"]),
                subject_id=int(row["subject_id"]),
                object_id=int(row["object_id"]),
            )
            adjacency[edge.subject_id].append((edge.object_id, edge, "forward"))
            adjacency[edge.object_id].append((edge.subject_id, edge, "reverse"))

        collected: list[GraphPath] = []
        visited_nodes: set[int] = set(seed_ids)
        edges_traversed = 0
        for seed_id in seed_ids:
            queue: deque[tuple[int, tuple[int, ...], tuple[PathHop, ...]]] = deque()
            queue.append((seed_id, (seed_id,), ()))
            while queue:
                current, chain, hops = queue.popleft()
                if hops:
                    collected.append(_path_from_hops(hops))
                if len(hops) >= max_hops:
                    continue
                for neighbor, edge, direction in adjacency.get(current, ()):
                    if neighbor in chain:
                        continue
                    edges_traversed += 1
                    visited_nodes.add(neighbor)
                    hop = PathHop(
                        subject=label_by_id[current],
                        predicate=edge.predicate,
                        object=label_by_id[neighbor],
                        direction=direction,
                        origin="extracted",
                        source_path=edge.source_path,
                        start_line=edge.start_line,
                        end_line=edge.end_line,
                    )
                    queue.append((neighbor, (*chain, neighbor), (*hops, hop)))
        collected.sort(key=lambda item: (-len(item.hops), ascii_path(item)))
        return GraphRetrieval(
            seeds=seeds,
            paths=tuple(collected),
            nodes_visited=len(visited_nodes),
            edges_traversed=edges_traversed,
        )

    def _ensure_index(self) -> None:
        if not self.index_path.is_file():
            raise SearchError(
                "El indice no existe. Ejecuta primero: graph-rag index --source <carpeta>"
            )

    def _metadata(self) -> dict[str, str]:
        self._ensure_index()
        connection = self._connect(query_only=True)
        try:
            return dict(connection.execute("SELECT key, value FROM metadata"))
        finally:
            connection.close()

    def _connect(self, *, query_only: bool) -> sqlite3.Connection:
        try:
            connection = sqlite3.connect(self.index_path)
            connection.row_factory = sqlite3.Row
            if query_only:
                connection.execute("PRAGMA query_only = ON")
            _validate_schema(connection)
        except sqlite3.Error as exc:
            raise SearchError(f"El indice SQLite no se pudo consultar: {exc}") from exc
        return connection


def ascii_path(path: GraphPath) -> str:
    if not path.hops:
        return ""
    pieces = [path.hops[0].subject]
    for hop in path.hops:
        if hop.direction == "forward":
            pieces.append(f"--{hop.predicate}-->")
        else:
            pieces.append(f"<--{hop.predicate}--")
        pieces.append(hop.object)
    return " ".join(pieces)


def mermaid_path(path: GraphPath) -> str:
    if not path.hops:
        return "graph LR"
    lines = ["graph LR"]
    for hop in path.hops:
        left = _mermaid_id(hop.subject)
        right = _mermaid_id(hop.object)
        if hop.direction == "forward":
            lines.append(f"  {left} -->|{hop.predicate}| {right}")
        else:
            # El salto se recorrió al revés: el triple escrito va de `object` a `subject`.
            lines.append(f"  {right} -->|{hop.predicate}| {left}")
    return "\n".join(lines)


def _mermaid_id(label: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", label)
    return cleaned or "node"


def _path_from_hops(hops: tuple[PathHop, ...]) -> GraphPath:
    inferred = None
    if len(hops) >= 2:
        inferred = InferredEdge(
            subject=hops[0].subject,
            # `^predicado` marca un salto inverso, como los caminos inversos de SPARQL 1.1.
            predicate="/".join(
                hop.predicate if hop.direction == "forward" else f"^{hop.predicate}" for hop in hops
            ),
            object=hops[-1].object,
            hops=len(hops),
        )
    return GraphPath(hops=hops, inferred=inferred)


def _upsert_node(connection: sqlite3.Connection, cache: dict[str, int], label: str) -> int:
    normalized = label.casefold()
    cached = cache.get(normalized)
    if cached is not None:
        return cached
    cursor = connection.execute(
        "INSERT INTO nodes(label, normalized) VALUES (?, ?)",
        (label, normalized),
    )
    node_id = int(cursor.lastrowid)
    cache[normalized] = node_id
    return node_id


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA journal_mode = DELETE;
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY,
            source_path TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            content_hash TEXT NOT NULL UNIQUE,
            chunk_count INTEGER NOT NULL CHECK (chunk_count > 0)
        );
        CREATE TABLE chunks (
            id INTEGER PRIMARY KEY,
            document_id INTEGER NOT NULL REFERENCES documents(id),
            source_path TEXT NOT NULL,
            title TEXT NOT NULL,
            heading TEXT NOT NULL,
            start_line INTEGER NOT NULL CHECK (start_line > 0),
            end_line INTEGER NOT NULL CHECK (end_line >= start_line),
            content TEXT NOT NULL,
            content_hash TEXT NOT NULL
        );
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            title,
            heading,
            content,
            tokenize = 'unicode61 remove_diacritics 2'
        );
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            label TEXT NOT NULL,
            normalized TEXT NOT NULL UNIQUE
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            subject_id INTEGER NOT NULL REFERENCES nodes(id),
            object_id INTEGER NOT NULL REFERENCES nodes(id),
            predicate TEXT NOT NULL,
            origin TEXT NOT NULL CHECK (origin = 'extracted'),
            document_id INTEGER NOT NULL REFERENCES documents(id),
            source_path TEXT NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL
        );
        """
    )


def _validate_schema(connection: sqlite3.Connection) -> None:
    row = connection.execute("SELECT value FROM metadata WHERE key = 'schema_version'").fetchone()
    if row is None or str(row[0]) != SCHEMA_VERSION:
        raise SearchError("El indice usa un schema incompatible; vuelve a indexar el corpus.")


def _query_terms(question: str) -> list[str]:
    raw_terms = [term for term in WORD_PATTERN.findall(question.casefold()) if len(term) >= 2]
    unique_terms = list(dict.fromkeys(raw_terms))
    useful_terms = [term for term in unique_terms if term not in STOPWORDS]
    return useful_terms or unique_terms


def _chunk_markdown(path: Path, text: str, max_chars: int) -> tuple[str, list[_Chunk]]:
    lines = text.splitlines()
    title = path.stem.replace("_", " ").strip()
    current_heading = title
    blocks: list[_Block] = []
    paragraph_lines: list[str] = []
    paragraph_start = 0

    def flush_paragraph(end_line: int) -> None:
        nonlocal paragraph_lines, paragraph_start
        content = " ".join(line.strip() for line in paragraph_lines).strip()
        if content:
            blocks.append(_Block(content, current_heading, paragraph_start, end_line))
        paragraph_lines = []
        paragraph_start = 0

    for line_number, raw_line in enumerate(lines, 1):
        stripped = raw_line.strip()
        heading_match = HEADING_PATTERN.match(stripped)
        if heading_match:
            flush_paragraph(line_number - 1)
            heading_text = heading_match.group(2).strip()
            if len(heading_match.group(1)) == 1 and heading_text:
                title = heading_text
            current_heading = heading_text or title
            continue
        if not stripped:
            flush_paragraph(line_number - 1)
            continue
        if not paragraph_lines:
            paragraph_start = line_number
        paragraph_lines.append(stripped)
    flush_paragraph(len(lines))
    if not blocks and title:
        blocks.append(_Block(title, title, 1, max(1, len(lines))))

    chunks: list[_Chunk] = []
    active: list[_Block] = []
    active_chars = 0

    def flush_chunk() -> None:
        nonlocal active, active_chars
        if not active:
            return
        chunks.append(
            _Chunk(
                title=title,
                heading=active[0].heading,
                start_line=active[0].start_line,
                end_line=active[-1].end_line,
                content="\n\n".join(block.text for block in active),
            )
        )
        active = []
        active_chars = 0

    for block in blocks:
        separator = 2 if active else 0
        changes_heading = bool(active and active[0].heading != block.heading)
        if active and (changes_heading or active_chars + separator + len(block.text) > max_chars):
            flush_chunk()
            separator = 0
        active.append(block)
        active_chars += separator + len(block.text)
    flush_chunk()
    return title, chunks
