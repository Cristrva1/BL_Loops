import pytest

from graph_rag.extract import ExtractError, extract_triples, match_entities


def test_extracts_visible_triples_and_ignores_prose() -> None:
    text = (
        "# Personas\n\n"
        "Ana Ruiz lidera AtlasCRM.\n\n"
        "- `Ana Ruiz` --owns--> `AtlasCRM`\n"
        "- esto no es una relacion\n"
        "`Luis Soto` --owns--> `PortalClientes`\n"
    )

    triples = extract_triples(text)

    assert [(item.subject, item.predicate, item.object, item.start_line) for item in triples] == [
        ("Ana Ruiz", "owns", "AtlasCRM", 5),
        ("Luis Soto", "owns", "PortalClientes", 7),
    ]
    assert all(item.origin == "extracted" for item in triples)


def test_normalizes_whitespace_inside_labels() -> None:
    triples = extract_triples("- `Ana   Ruiz` --owns--> `AtlasCRM`\n")

    assert triples[0].subject == "Ana Ruiz"
    assert triples[0].object == "AtlasCRM"


def test_rejects_self_loop() -> None:
    with pytest.raises(ExtractError, match="bucle"):
        extract_triples("- `AtlasCRM` --owns--> `AtlasCRM`\n")


def test_longest_entity_label_wins_without_overlapping_shorter_names() -> None:
    labels = match_entities("proyecto de Ana Ruiz y AtlasCRM", ["Ana", "Ana Ruiz", "AtlasCRM"])

    assert labels == ("Ana Ruiz", "AtlasCRM")
    assert "Ana" not in labels
