from pathlib import Path

from vector_rag.quality import prepare_markdown


def test_known_noisy_sections_are_excluded_but_editorial_content_remains() -> None:
    text = """# Virtual Selling
**Autor:** Persona Sintética

## Descripción Editorial
La venta remota requiere escucha y preparación.

## Contexto (Wikipedia)
Richard Nixon fue presidente y este texto no pertenece al libro.

## Temas (Open Library)
- Commerce

## Fuentes y Adquisición
- https://example.test

---
*Candidato no revisado — fecha_adquisicion: 2026-06-20*
"""

    document = prepare_markdown(Path("ventas/Virtual_Selling.md"), text)

    combined = "\n".join(block.text for block in document.blocks)
    assert document.title == "Virtual Selling"
    assert document.source_status == "unreviewed"
    assert document.excluded_sections == 3
    assert "venta remota" in combined
    assert "Commerce" not in combined
    assert "Richard Nixon" not in combined
    assert "example.test" not in combined


def test_generated_and_received_sources_have_visible_statuses() -> None:
    generated = prepare_markdown(
        Path("book.md"),
        "# Libro\n\nContenido.\n\n*Documento generado por ÁNIMA research pipeline*\n",
    )
    received = prepare_markdown(Path("paper.md"), "# Artículo\n\nContenido primario.\n")

    assert generated.source_status == "generated"
    assert received.source_status == "received"
