"""Lectura local acotada: sin path traversal, sin seguir enlaces de escape."""

from __future__ import annotations

from pathlib import Path

ALLOWED_SUFFIXES = {".md": "text/markdown", ".markdown": "text/markdown", ".txt": "text/plain"}


class IngestError(ValueError):
    """La ruta o el archivo no cumplen la política de ingesta."""


def resolve_inside(root: Path, candidate: Path) -> Path:
    base = root.resolve()
    target = (base / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    if not target.is_relative_to(base):
        raise IngestError("La ruta sale del directorio permitido")
    if target.is_symlink():
        real = target.resolve()
        if not real.is_relative_to(base):
            raise IngestError("El enlace simbólico sale del directorio permitido")
    return target


def discover_sources(root: Path, source_dir: Path) -> list[Path]:
    directory = resolve_inside(root, source_dir)
    if not directory.is_dir():
        raise IngestError("La fuente debe ser un directorio local")
    files = [
        path
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.suffix.casefold() in ALLOWED_SUFFIXES
    ]
    if not files:
        raise IngestError("No hay archivos Markdown o TXT permitidos")
    for path in files:
        resolve_inside(directory, path)
        if path.is_symlink():
            resolve_inside(directory, path)
    return files


def mime_for(path: Path) -> str:
    mime = ALLOWED_SUFFIXES.get(path.suffix.casefold())
    if mime is None:
        raise IngestError(f"MIME no permitido: {path.suffix}")
    return mime


def read_bytes(path: Path, max_bytes: int) -> bytes:
    size = path.stat().st_size
    if size > max_bytes:
        raise IngestError(f"El archivo supera MAX_BYTES_PER_SOURCE ({max_bytes})")
    return path.read_bytes()
