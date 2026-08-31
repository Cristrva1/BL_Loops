from pathlib import Path

from sales_agent.quality import prepare_markdown


def test_known_noise_and_metadata_are_excluded() -> None:
    prepared = prepare_markdown(
        Path("book.md"),
        """# Libro
**Autor:** Persona

## Descripcion Editorial
Escuchar necesidades y aportar valor.

## Contexto (Wikipedia)
Una biografia equivocada.

## Metadatos
- Commerce
""",
    )

    joined = " ".join(block.text for block in prepared.blocks)
    assert joined == "Escuchar necesidades y aportar valor."
    assert prepared.excluded_sections == 2


def test_source_status_is_explicit() -> None:
    prepared = prepare_markdown(
        Path("candidate.md"),
        "# Candidato\n\n## Descripcion Editorial\nContenido.\n\n*Candidato no revisado*",
    )

    assert prepared.source_status == "unreviewed"
