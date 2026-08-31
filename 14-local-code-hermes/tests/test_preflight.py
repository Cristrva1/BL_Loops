from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest
from conftest import FakeRunner, happy_results

from local_code_hermes.command import CommandRequest, CommandResult
from local_code_hermes.config import PreflightConfig
from local_code_hermes.preflight import (
    LMSTUDIO_PROCESS_SCRIPT,
    RAM_SCRIPT,
    REQUIRED_GATE_IDS,
    PreflightReport,
    check_firewall,
    check_git,
    check_hermes,
    check_lmstudio,
    check_model,
    check_ram,
    check_server_profile,
    check_vram,
    run_preflight,
)


def _result_for(results: dict[tuple[str, ...], CommandResult], executable: str) -> tuple[str, ...]:
    return next(args for args in results if args[0] == executable)


def test_formal_preflight_passes_with_complete_synthetic_evidence(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    runner = FakeRunner(happy_results())

    report = run_preflight(make_formal_config(), runner)

    assert report.outcome == "passed"
    assert report.terminal_event == "run.completed"
    assert tuple(gate.gate_id for gate in report.gates) == REQUIRED_GATE_IDS
    assert all(gate.outcome == "passed" for gate in report.gates)
    hermes = next(gate for gate in report.gates if gate.gate_id == "hermes.available")
    ram = next(gate for gate in report.gates if gate.gate_id == "resource.ram")
    vram = next(gate for gate in report.gates if gate.gate_id == "resource.vram")
    assert hermes.evidence == {"version": "0.3.1"}
    assert ram.evidence["commit_headroom_gib"] == 24.0
    assert ram.evidence["pagefile_used_mib"] == 1024
    assert vram.evidence["selected_free_mib"] == 13_000
    model = next(gate for gate in report.gates if gate.gate_id == "ollama.model")
    assert model.evidence["weights_match"] is True
    assert "synthetic9b" not in repr(model.evidence)


def test_ollama_request_is_pinned_to_loopback_without_claiming_server_profile(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    runner = FakeRunner(happy_results())
    config = make_formal_config(server_profile_proof="unverified", server_profile_proof_id=None)

    report = run_preflight(config, runner)

    model_request = next(request for request in runner.requests if request.args[0] == "ollama")
    assert model_request.env_overrides["OLLAMA_HOST"] == "http://127.0.0.1:11434"
    assert model_request.env_overrides["OLLAMA_NO_CLOUD"] == "1"
    profile = next(gate for gate in report.gates if gate.gate_id == "ollama.server_profile")
    assert profile.outcome == "blocked"
    assert report.terminal_event == "run.blocked"


def test_remote_endpoint_blocks_and_skips_ollama_command(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    runner = FakeRunner(happy_results())

    report = run_preflight(
        make_formal_config(ollama_base_url="https://models.example.invalid"),
        runner,
    )

    endpoint = next(gate for gate in report.gates if gate.gate_id == "network.endpoint")
    model = next(gate for gate in report.gates if gate.gate_id == "ollama.model")
    assert endpoint.code == "endpoint_not_loopback"
    assert model.code == "endpoint_not_approved"
    assert not any(request.args[0] == "ollama" for request in runner.requests)
    assert report.terminal_event == "run.blocked"


@pytest.mark.parametrize(
    ("alias_modelfile", "source_modelfile", "expected_code"),
    (
        (
            "FROM D:/ollama/blobs/sha256-alias\nPARAMETER num_ctx 65536\n",
            "FROM D:/ollama/blobs/sha256-source\n",
            "source_weights_mismatch",
        ),
        (
            "FROM D:/ollama/blobs/sha256-same\nPARAMETER num_ctx 32768\n",
            "FROM D:/ollama/blobs/sha256-same\n",
            "num_ctx_mismatch",
        ),
        (
            "FROM blob-a\nFROM blob-b\nPARAMETER num_ctx 65536\n",
            "FROM blob-a\n",
            "runtime_modelfile_unparseable",
        ),
    ),
)
def test_model_identity_and_context_fail_closed(
    tmp_path: Path,
    alias_modelfile: str,
    source_modelfile: str,
    expected_code: str,
) -> None:
    (tmp_path / "Modelfile").write_text(
        "FROM qwen3.5:9b\nPARAMETER num_ctx 65536\n",
        encoding="utf-8",
    )
    alias_command = ("ollama", "show", "local-code-9b-64k", "--modelfile")
    source_command = ("ollama", "show", "qwen3.5:9b", "--modelfile")
    runner = FakeRunner(
        {
            alias_command: CommandResult(0, stdout=alias_modelfile),
            source_command: CommandResult(0, stdout=source_modelfile),
        }
    )
    config = PreflightConfig(lab_root=tmp_path, python_version=(3, 12))

    gate = check_model(config, runner, endpoint_approved=True)

    assert gate.outcome == "blocked"
    assert gate.code == expected_code


def test_local_modelfile_contract_is_checked_before_any_ollama_command(tmp_path: Path) -> None:
    (tmp_path / "Modelfile").write_text(
        "FROM qwen3.5:4b\nPARAMETER num_ctx 65536\n",
        encoding="utf-8",
    )
    runner = FakeRunner({})

    gate = check_model(
        PreflightConfig(lab_root=tmp_path, python_version=(3, 12)),
        runner,
        endpoint_approved=True,
    )

    assert gate.outcome == "blocked"
    assert gate.code == "model_contract_source_mismatch"
    assert runner.requests == []


def test_hermes_version_is_captured_without_raw_output(tmp_path: Path) -> None:
    sentinel = "RAW_OUTPUT_MUST_NOT_BE_RECORDED"
    runner = FakeRunner(
        {
            ("hermes", "--version"): CommandResult(
                0,
                stdout=f"Hermes {sentinel}",
                stderr="version v1.2.3+local",
            )
        }
    )

    gate = check_hermes(
        PreflightConfig(lab_root=tmp_path, python_version=(3, 12)),
        runner,
    )

    assert gate.outcome == "passed"
    assert gate.evidence == {"version": "1.2.3+local"}
    assert sentinel not in repr(gate.evidence)


def test_hermes_missing_or_unversioned_blocks(tmp_path: Path) -> None:
    config = PreflightConfig(lab_root=tmp_path, python_version=(3, 12))
    missing = FakeRunner({("hermes", "--version"): CommandResult(127, error_kind="not_found")})
    unversioned = FakeRunner(
        {("hermes", "--version"): CommandResult(0, stdout="Hermes development build")}
    )

    assert check_hermes(config, missing).code == "command_not_found"
    assert check_hermes(config, unversioned).code == "version_not_captured"


def test_dirty_git_tree_blocks_without_recording_file_names(tmp_path: Path) -> None:
    runner = FakeRunner(
        {
            ("git", "rev-parse", "--verify", "HEAD"): CommandResult(
                0,
                stdout="a" * 40 + "\n",
            ),
            ("git", "status", "--porcelain=v1"): CommandResult(
                0,
                stdout=" M private-not-to-be-recorded.py\n?? another-file.txt\n",
            ),
        }
    )

    gate = check_git(
        PreflightConfig(lab_root=tmp_path, python_version=(3, 12)),
        runner,
    )

    assert gate.outcome == "blocked"
    assert gate.code == "worktree_dirty"
    assert gate.evidence == {
        "head": "a" * 40,
        "worktree_clean": False,
        "changed_entry_count": 2,
    }
    assert "private-not-to-be-recorded.py" not in repr(gate.evidence)


def test_git_status_failure_blocks_without_claiming_clean_tree(tmp_path: Path) -> None:
    runner = FakeRunner(
        {
            ("git", "rev-parse", "--verify", "HEAD"): CommandResult(
                0,
                stdout="a" * 40 + "\n",
            ),
            ("git", "status", "--porcelain=v1"): CommandResult(128),
        }
    )

    gate = check_git(
        PreflightConfig(lab_root=tmp_path, python_version=(3, 12)),
        runner,
    )

    assert gate.outcome == "blocked"
    assert gate.code == "worktree_state_unknown"


def test_lmstudio_loaded_model_is_a_conflict(tmp_path: Path) -> None:
    runner = FakeRunner(
        {("lms", "ps", "--json"): CommandResult(0, stdout='{"models":[{"id":"x"}]}')}
    )

    gate = check_lmstudio(
        PreflightConfig(lab_root=tmp_path, python_version=(3, 12)),
        runner,
    )

    assert gate.outcome == "blocked"
    assert gate.code == "lmstudio_model_loaded"
    assert gate.evidence["loaded_model_count"] == 1


def test_missing_lms_cli_uses_hermetic_process_fallback(tmp_path: Path) -> None:
    lms = ("lms", "ps", "--json")
    process = (
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        LMSTUDIO_PROCESS_SCRIPT,
    )
    runner = FakeRunner(
        {
            lms: CommandResult(127, error_kind="not_found"),
            process: CommandResult(
                0,
                stdout='{"loaded_model_processes":0,"unknown_model_processes":0}',
            ),
        }
    )

    gate = check_lmstudio(
        PreflightConfig(lab_root=tmp_path, python_version=(3, 12)),
        runner,
    )

    assert gate.outcome == "passed"
    assert gate.code == "lms_absent_no_model_process_observed"
    assert [request.args for request in runner.requests] == [lms, process]


def test_lmstudio_fallback_blocks_inaccessible_process_identity(tmp_path: Path) -> None:
    lms = ("lms", "ps", "--json")
    process = (
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        LMSTUDIO_PROCESS_SCRIPT,
    )
    runner = FakeRunner(
        {
            lms: CommandResult(127, error_kind="not_found"),
            process: CommandResult(
                0,
                stdout='{"loaded_model_processes":0,"unknown_model_processes":1}',
            ),
        }
    )

    gate = check_lmstudio(
        PreflightConfig(lab_root=tmp_path, python_version=(3, 12)),
        runner,
    )

    assert gate.outcome == "blocked"
    assert gate.code == "lmstudio_state_unknown"


def test_unknown_lmstudio_state_blocks(tmp_path: Path) -> None:
    runner = FakeRunner({("lms", "ps", "--json"): CommandResult(0, stdout="not-json")})

    gate = check_lmstudio(
        PreflightConfig(lab_root=tmp_path, python_version=(3, 12)),
        runner,
    )

    assert gate.outcome == "blocked"
    assert gate.code == "lmstudio_state_unknown"


def test_git_head_absent_blocks_formal_but_warns_exploratory(tmp_path: Path) -> None:
    result = CommandResult(128, error_kind="nonzero")
    command = ("git", "rev-parse", "--verify", "HEAD")

    formal = check_git(
        PreflightConfig(mode="formal", lab_root=tmp_path, python_version=(3, 12)),
        FakeRunner({command: result}),
    )
    exploratory = check_git(
        PreflightConfig(mode="exploratory", lab_root=tmp_path, python_version=(3, 12)),
        FakeRunner({command: result}),
    )

    assert (formal.outcome, formal.code) == ("blocked", "head_absent_formal")
    assert (exploratory.outcome, exploratory.code) == (
        "warning",
        "head_absent_exploratory",
    )


def test_abbreviated_git_head_never_satisfies_exact_sha_gate(tmp_path: Path) -> None:
    command = ("git", "rev-parse", "--verify", "HEAD")
    gate = check_git(
        PreflightConfig(mode="formal", lab_root=tmp_path, python_version=(3, 12)),
        FakeRunner({command: CommandResult(0, stdout="abcdef0\n")}),
    )

    assert gate.outcome == "blocked"
    assert gate.code == "head_not_exact"


def test_firewall_and_server_profile_are_manual_formal_gates(tmp_path: Path) -> None:
    formal = PreflightConfig(mode="formal", lab_root=tmp_path, python_version=(3, 12))
    exploratory = PreflightConfig(
        mode="exploratory",
        lab_root=tmp_path,
        python_version=(3, 12),
    )

    assert check_firewall(formal).outcome == "blocked"
    assert check_server_profile(formal).outcome == "blocked"
    assert check_firewall(exploratory).outcome == "warning"
    assert check_server_profile(exploratory).outcome == "warning"


def test_ram_gate_records_physical_commit_and_pagefile_fields(tmp_path: Path) -> None:
    gib = 1024**3
    command = (
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        RAM_SCRIPT,
    )
    runner = FakeRunner(
        {
            command: CommandResult(
                0,
                stdout=json.dumps(
                    {
                        "total_bytes": 64 * gib,
                        "available_bytes": 7 * gib,
                        "commit_limit_bytes": 96 * gib,
                        "commit_headroom_bytes": 6 * gib,
                        "pagefile_used_mib": 2048,
                    }
                ),
            )
        }
    )

    gate = check_ram(
        PreflightConfig(lab_root=tmp_path, python_version=(3, 12)),
        runner,
    )

    assert gate.outcome == "blocked"
    assert gate.code == "ram_headroom_low"
    assert gate.evidence["available_gib"] == 7.0
    assert gate.evidence["commit_headroom_gib"] == 6.0
    assert gate.evidence["pagefile_used_mib"] == 2048


def test_vram_gate_records_headroom_and_blocks_below_threshold(tmp_path: Path) -> None:
    command = (
        "nvidia-smi",
        "--query-gpu=index,memory.total,memory.free",
        "--format=csv,noheader,nounits",
    )
    runner = FakeRunner({command: CommandResult(0, stdout="0, 16384, 11000\n")})

    gate = check_vram(
        PreflightConfig(lab_root=tmp_path, python_version=(3, 12)),
        runner,
    )

    assert gate.outcome == "blocked"
    assert gate.code == "vram_headroom_low"
    assert gate.evidence["selected_total_mib"] == 16_384
    assert gate.evidence["selected_free_mib"] == 11_000


def test_runner_exception_becomes_failed_gate_and_failed_terminal(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    class ExplodingRunner:
        def run(self, request: CommandRequest) -> CommandResult:
            raise RuntimeError("synthetic runner failure")

    report = run_preflight(make_formal_config(), ExplodingRunner())

    assert report.outcome == "failed"
    assert report.terminal_event == "run.failed"
    assert any(gate.code == "internal_check_error" for gate in report.gates)


def test_report_terminal_is_derived_from_gate_outcomes() -> None:
    from local_code_hermes.preflight import GateResult

    passed = GateResult("a", "passed", False, "ok", {})
    blocked = GateResult("b", "blocked", True, "no_evidence", {})
    failed = GateResult("c", "failed", True, "internal", {})

    assert PreflightReport("formal", (passed,)).terminal_event == "run.completed"
    assert PreflightReport("formal", (passed, blocked)).terminal_event == "run.blocked"
    assert PreflightReport("formal", (blocked, failed)).terminal_event == "run.failed"


def test_all_preflight_commands_are_satisfied_by_the_double(
    make_formal_config: Callable[..., PreflightConfig],
) -> None:
    results = happy_results()
    runner = FakeRunner(results)

    run_preflight(make_formal_config(), runner)

    assert {request.args for request in runner.requests} == set(results)
    assert all(isinstance(request.args, tuple) for request in runner.requests)
