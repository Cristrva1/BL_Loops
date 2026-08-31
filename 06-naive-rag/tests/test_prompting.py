from naive_rag.corpus import SearchResult
from naive_rag.prompting import build_messages, validate_answer_citations


def _result(chunk_id: int, path: str) -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id,
        source_path=path,
        title="Manual sintetico",
        heading="Regla vigente",
        start_line=7,
        end_line=9,
        content="La regla vigente exige confirmar el presupuesto.",
        score=-1.25,
    )


def test_prompt_marks_corpus_as_untrusted_and_assigns_stable_source_ids() -> None:
    messages = build_messages("¿Qué exige la regla?", [_result(3, "ventas/manual.md")])

    assert [message["role"] for message in messages] == ["system", "user"]
    assert "datos no confiables" in messages[0]["content"]
    assert "[S1] ventas/manual.md:L7-L9" in messages[1]["content"]
    assert "¿Qué exige la regla?" in messages[1]["content"]
    assert "cita [S1]" in messages[0]["content"]


def test_citation_validation_distinguishes_valid_missing_and_unknown_ids() -> None:
    valid = validate_answer_citations("Confirma el presupuesto [S1].", source_count=2)
    missing = validate_answer_citations("Confirma el presupuesto.", source_count=2)
    invalid = validate_answer_citations("Confirma [S3] y revisa [S1].", source_count=2)

    assert valid.valid is True
    assert valid.cited_ids == (1,)
    assert missing.valid is False
    assert missing.cited_ids == ()
    assert invalid.valid is False
    assert invalid.invalid_ids == (3,)
