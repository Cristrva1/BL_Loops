from __future__ import annotations

import copy
import json
from collections.abc import Callable
from pathlib import Path

import pytest
from conftest import FakeRunner, happy_results

from local_code_hermes.config import PreflightConfig
from local_code_hermes.preflight import (
    REQUIRED_GATE_IDS,
    GateResult,
    PreflightReport,
    run_preflight,
)
from local_code_hermes.run_log import build_preflight_events
from local_code_hermes.validation import ValidationError, validate_events, validate_path


def _report(config: PreflightConfig, override: GateResult | None = None) -> PreflightReport:
    base = run_preflight(config, FakeRunner(happy_results()))
    gates = list(base.gates)
    if override is not None:
        gates[REQUIRED_GATE_IDS.index(override.gate_id)] = override
    return PreflightReport("formal", tuple(gates))


def _events(
    make_formal_config: Callable[..., PreflightConfig],
    override: GateResult | None = None,
) -> list[dict[str, object]]:
    config = make_formal_config()
    return build_preflight_events(
        _report(config, override),
        config,
        run_id="run-validation-0001",
    )


def _write(path: Path, events: list[dict[str, object]], *, final_newline: bool = True) -> None:
    text = "\n".join(
        json.dumps(event, ensure_ascii=False, separators=(",", ":")) for event in events
    )
    if final_newline:
        text += "\n"
    path.write_text(text, encoding="utf-8", newline="")


def test_valid_completed_blocked_and_failed_runs_roundtrip(
    tmp_path: Path,
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    scenarios = (
        (None, "run.completed"),
        (
            GateResult("git.head", "blocked", True, "head_absent_formal", {}),
            "run.blocked",
        ),
        (
            GateResult("git.head", "failed", True, "internal_check_error", {}),
            "run.failed",
        ),
    )
    for index, (override, terminal) in enumerate(scenarios):
        path = tmp_path / f"run-{index}.jsonl"
        _write(path, _events(make_formal_config, override))

        summary = validate_path(path)

        assert summary["terminal_event"] == terminal
        assert summary["event_count"] == 2 + 2 * len(REQUIRED_GATE_IDS)


@pytest.mark.parametrize(
    "mutation",
    (
        lambda events: events[0].pop("metrics"),
        lambda events: events[0].__setitem__("unexpected", True),
        lambda events: events[0].__setitem__("schema_version", "1.0"),
        lambda events: events[0].__setitem__("lab_id", "02-single-agent"),
        lambda events: events[0].__setitem__("case_id", "CODE-LOCAL-001@1.0.0"),
        lambda events: events[0].__setitem__("sequence", True),
        lambda events: events[0].__setitem__("timestamp", "2026-01-01T00:00:00"),
        lambda events: events[0].__setitem__("event_type", "arbitrary.event"),
        lambda events: events[0].__setitem__("payload", []),
        lambda events: events[0].__setitem__("metrics", []),
        lambda events: events[0].__setitem__("artifact_refs", {}),
        lambda events: events[0]["model"].__setitem__("extra", True),  # type: ignore[union-attr]
        lambda events: events[0]["model"].__setitem__(  # type: ignore[union-attr]
            "endpoint", "https://remote.example.invalid"
        ),
    ),
)
def test_schema_mutations_are_rejected(
    make_formal_config: Callable[..., PreflightConfig],
    mutation: Callable[[list[dict[str, object]]], object],
) -> None:
    events = copy.deepcopy(_events(make_formal_config))
    mutation(events)

    with pytest.raises(ValidationError):
        validate_events(events)


def test_sequence_run_id_and_event_id_are_strict(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    sequence = copy.deepcopy(_events(make_formal_config))
    sequence[2]["sequence"] = 99
    with pytest.raises(ValidationError, match="sequence"):
        validate_events(sequence)

    mixed = copy.deepcopy(_events(make_formal_config))
    mixed[2]["run_id"] = "run-other"
    with pytest.raises(ValidationError, match="run_id"):
        validate_events(mixed)

    duplicate = copy.deepcopy(_events(make_formal_config))
    duplicate[2]["event_id"] = duplicate[1]["event_id"]
    with pytest.raises(ValidationError, match="event_id"):
        validate_events(duplicate)


def test_terminal_must_be_unique_last_and_match_outcome(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    early = copy.deepcopy(_events(make_formal_config))
    early[2]["event_type"] = "run.completed"
    with pytest.raises(ValidationError, match="terminal"):
        validate_events(early)

    missing = copy.deepcopy(_events(make_formal_config))
    missing[-1]["event_type"] = "node.completed"
    with pytest.raises(ValidationError, match="terminal"):
        validate_events(missing)

    mismatch = copy.deepcopy(_events(make_formal_config))
    mismatch[-1]["event_type"] = "run.blocked"
    with pytest.raises(ValidationError, match="terminal|outcome"):
        validate_events(mismatch)


def test_terminal_is_recomputed_from_gate_results(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    events = copy.deepcopy(_events(make_formal_config))
    completed_gate = next(
        event
        for event in events
        if event["event_type"] == "node.completed" and event["payload"].get("gate_id") == "git.head"  # type: ignore[union-attr]
    )
    completed_gate["event_type"] = "node.failed"
    completed_gate["payload"]["outcome"] = "blocked"  # type: ignore[index]
    completed_gate["payload"]["blocking"] = True  # type: ignore[index]
    completed_gate["payload"]["code"] = "head_absent_formal"  # type: ignore[index]

    with pytest.raises(ValidationError, match="terminal|gate|outcome"):
        validate_events(events)


def test_formal_completed_rejects_empty_gate_evidence(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    events = copy.deepcopy(_events(make_formal_config))
    events[0]["payload"]["client_version"] = None  # type: ignore[index]
    events[0]["payload"]["git_head"] = None  # type: ignore[index]
    for event in events:
        if event["event_type"] == "node.completed":
            event["payload"]["evidence"] = {}  # type: ignore[index]

    with pytest.raises(
        ValidationError,
        match="Evidencia|evidencia|evidence|Hermes|HEAD|gate|Codigo",
    ):
        validate_events(events)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("client_version", None, "client_version"),
        ("git_head", None, "git_head"),
        ("network_evidence_ref", None, "red"),
        ("server_profile_evidence_ref", None, "perfil"),
    ),
)
def test_started_evidence_must_correlate_with_passed_gates(
    make_formal_config: Callable[..., PreflightConfig],
    field: str,
    value: object,
    message: str,
) -> None:
    events = copy.deepcopy(_events(make_formal_config))
    events[0]["payload"][field] = value  # type: ignore[index]

    with pytest.raises(ValidationError, match=message):
        validate_events(events)


def test_formal_mode_cannot_complete_with_exploratory_warning(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    events = copy.deepcopy(_events(make_formal_config))
    firewall = next(
        event
        for event in events
        if event["event_type"] == "node.completed"
        and event["payload"].get("gate_id") == "network.firewall"  # type: ignore[union-attr]
    )
    firewall["payload"].update(  # type: ignore[union-attr]
        {
            "outcome": "warning",
            "code": "locality_unproven_exploratory",
            "evidence": {"proof_present": False},
        }
    )
    events[0]["payload"]["network_evidence_ref"] = None  # type: ignore[index]
    events[-1]["payload"]["gate_counts"] = {"passed": 9, "warning": 1}  # type: ignore[index]

    with pytest.raises(ValidationError, match="Warning|formal"):
        validate_events(events)


def test_gate_lifecycle_cannot_be_removed_even_if_sequence_is_rewritten(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    events = copy.deepcopy(_events(make_formal_config))
    del events[1:3]
    for sequence, event in enumerate(events, start=1):
        event["sequence"] = sequence
        event["event_id"] = f"evt-{sequence:04d}"

    with pytest.raises(ValidationError, match="gate|nodo|node|requerid"):
        validate_events(events)


def test_physical_jsonl_contract_rejects_empty_blank_no_newline_and_invalid_utf8(
    tmp_path: Path,
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    empty = tmp_path / "empty.jsonl"
    empty.write_bytes(b"")
    with pytest.raises(ValidationError, match="vacio"):
        validate_path(empty)

    no_newline = tmp_path / "no-newline.jsonl"
    _write(no_newline, _events(make_formal_config), final_newline=False)
    with pytest.raises(ValidationError, match="newline"):
        validate_path(no_newline)

    blank = tmp_path / "blank.jsonl"
    _write(blank, _events(make_formal_config))
    blank.write_text(blank.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ValidationError, match="vacias"):
        validate_path(blank)

    invalid = tmp_path / "invalid-utf8.jsonl"
    invalid.write_bytes(b"{\xff}\n")
    with pytest.raises(ValidationError, match="UTF-8"):
        validate_path(invalid)


def test_duplicate_keys_and_non_finite_numbers_are_rejected(
    tmp_path: Path,
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    lines = [
        json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        for event in _events(make_formal_config)
    ]
    duplicate = tmp_path / "duplicate-key.jsonl"
    lines[0] = lines[0].replace(
        '"schema_version":"1.1",',
        '"schema_version":"1.1","schema_version":"1.1",',
        1,
    )
    duplicate.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValidationError, match="duplicada"):
        validate_path(duplicate)

    non_finite_events = _events(make_formal_config)
    non_finite_events[0]["metrics"] = {"value": float("nan")}
    non_finite = tmp_path / "nan.jsonl"
    _write(non_finite, non_finite_events)
    with pytest.raises(ValidationError, match="Constante|invalido"):
        validate_path(non_finite)


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="no existe"):
        validate_path(tmp_path / "missing.jsonl")
