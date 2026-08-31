from __future__ import annotations

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
from local_code_hermes.run_log import build_preflight_events, write_preflight_report


def _report(
    *,
    mode: str = "formal",
    override: GateResult | None = None,
) -> PreflightReport:
    gates = [
        GateResult(gate_id, "passed", False, "synthetic_ok", {}) for gate_id in REQUIRED_GATE_IDS
    ]
    if override is not None:
        index = REQUIRED_GATE_IDS.index(override.gate_id)
        gates[index] = override
    return PreflightReport(mode=mode, gates=tuple(gates))


def test_build_events_has_strict_sequence_lifecycle_and_completed_terminal(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    events = build_preflight_events(
        _report(),
        make_formal_config(),
        run_id="run-synthetic-0001",
    )

    assert events[0]["event_type"] == "run.started"
    assert events[-1]["event_type"] == "run.completed"
    assert [event["sequence"] for event in events] == list(range(1, len(events) + 1))
    assert {event["run_id"] for event in events} == {"run-synthetic-0001"}
    assert len({event["event_id"] for event in events}) == len(events)
    assert len(events) == 2 + 2 * len(REQUIRED_GATE_IDS)
    for offset, gate_id in enumerate(REQUIRED_GATE_IDS):
        started, finished = events[1 + offset * 2 : 3 + offset * 2]
        assert started["event_type"] == "node.started"
        assert finished["event_type"] == "node.completed"
        assert started["node"] == {"id": gate_id, "kind": "preflight_gate"}
        assert finished["payload"]["gate_id"] == gate_id  # type: ignore[index]


@pytest.mark.parametrize(
    ("gate", "terminal"),
    (
        (
            GateResult("git.head", "blocked", True, "head_absent_formal", {}),
            "run.blocked",
        ),
        (
            GateResult("git.head", "failed", True, "internal_check_error", {}),
            "run.failed",
        ),
    ),
)
def test_terminal_and_node_failure_are_derived_from_gate(
    make_formal_config: Callable[..., PreflightConfig],
    gate: GateResult,
    terminal: str,
) -> None:
    events = build_preflight_events(
        _report(override=gate),
        make_formal_config(),
        run_id="run-synthetic-0002",
    )

    gate_event = next(
        event
        for event in events
        if event["event_type"] == "node.failed" and event["payload"].get("gate_id") == gate.gate_id  # type: ignore[union-attr]
    )
    assert gate_event["payload"]["outcome"] == gate.outcome  # type: ignore[index]
    assert events[-1]["event_type"] == terminal
    assert events[-1]["payload"]["outcome"] == gate.outcome  # type: ignore[index]


def test_warning_completes_but_remains_visible(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    warning = GateResult(
        "network.firewall",
        "warning",
        False,
        "locality_unproven_exploratory",
        {"proof_present": False},
    )

    events = build_preflight_events(
        _report(mode="exploratory", override=warning),
        make_formal_config(mode="exploratory"),
        run_id="run-synthetic-0003",
    )

    assert events[-1]["event_type"] == "run.completed"
    assert events[-1]["payload"]["gate_counts"]["warning"] == 1  # type: ignore[index]


def test_writer_creates_compact_utf8_jsonl_atomically_inside_lab(
    tmp_path: Path,
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    runs_dir = tmp_path / ".local" / "runs"
    config = make_formal_config()
    report = run_preflight(config, FakeRunner(happy_results()))

    path = write_preflight_report(report, runs_dir, config)

    raw = path.read_bytes()
    lines = raw.decode("utf-8").splitlines()
    assert path.parent == runs_dir
    assert raw.endswith(b"\n")
    assert lines
    assert all(line.startswith("{") and line.endswith("}") for line in lines)
    assert all("\n" not in line and ": " not in line for line in lines)
    assert not list(runs_dir.glob("*.tmp"))
    assert json.loads(lines[-1])["event_type"] == "run.completed"


def test_writer_rejects_destination_outside_lab(
    tmp_path: Path,
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    outside = tmp_path.parent / "outside-hermes-runs"

    with pytest.raises(ValueError, match="laboratorio"):
        write_preflight_report(_report(), outside, make_formal_config())


@pytest.mark.parametrize(
    "evidence",
    (
        {"stdout": "RAW_STDOUT_SENTINEL"},
        {"stderr": "RAW_STDERR_SENTINEL"},
        {"api_token": "SECRET_TOKEN_SENTINEL"},
        {"prompt": "PRIVATE_PROMPT_SENTINEL"},
        {"email": "person@example.invalid"},
        {"path": "C:\\private\\operator\\file.txt"},
    ),
)
def test_writer_rejects_or_redacts_sensitive_gate_evidence(
    make_formal_config: Callable[..., PreflightConfig],
    evidence: dict[str, object],
) -> None:
    sentinel = next(iter(evidence.values()))
    unsafe = GateResult("hermes.available", "passed", False, "version_captured", evidence)

    try:
        events = build_preflight_events(
            _report(override=unsafe),
            make_formal_config(),
            run_id="run-sensitive-evidence",
        )
    except ValueError:
        return

    def string_values(value: object) -> list[str]:
        if isinstance(value, str):
            return [value]
        if isinstance(value, dict):
            return [item for child in value.values() for item in string_values(child)]
        if isinstance(value, list):
            return [item for child in value for item in string_values(child)]
        return []

    assert str(sentinel) not in string_values(events)


def test_invalid_endpoint_credentials_never_reach_serialized_model(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    config = make_formal_config(ollama_base_url="http://operator:ENDPOINT_SECRET@127.0.0.1:11434")

    try:
        events = build_preflight_events(
            _report(
                override=GateResult(
                    "network.endpoint",
                    "blocked",
                    True,
                    "endpoint_not_loopback",
                    {},
                )
            ),
            config,
            run_id="run-sensitive-endpoint",
        )
    except ValueError:
        return

    assert "ENDPOINT_SECRET" not in json.dumps(events)


def test_proof_references_are_hashed_and_both_are_exported(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    events = build_preflight_events(
        _report(),
        make_formal_config(),
        run_id="run-proof-references",
    )
    payload = events[0]["payload"]
    serialized = json.dumps(events)

    assert str(payload["network_evidence_ref"]).startswith("sha256:")  # type: ignore[index]
    assert str(payload["server_profile_evidence_ref"]).startswith("sha256:")  # type: ignore[index]
    assert "FW-LOCAL-001" not in serialized
    assert "OLLAMA-PROFILE-001" not in serialized
