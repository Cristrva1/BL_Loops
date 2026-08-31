from __future__ import annotations

import json
from pathlib import Path

import pytest

from local_code_hermes.benchmark import (
    BenchmarkConfig,
    BenchmarkReport,
    build_hermes_command,
    build_hermes_environment,
    parse_ollama_ps,
    parse_usage_report,
    run_benchmark,
)
from local_code_hermes.benchmark_log import write_benchmark_report
from local_code_hermes.preflight import REQUIRED_GATE_IDS, GateResult, PreflightReport
from local_code_hermes.sandbox import DockerSandbox
from local_code_hermes.validation import validate_path


def _passed_preflight() -> PreflightReport:
    return PreflightReport(
        mode="formal",
        gates=tuple(
            GateResult(gate_id, "passed", False, "synthetic_ok", {})
            for gate_id in REQUIRED_GATE_IDS
        ),
    )


def test_ollama_ps_requires_the_target_model_and_100_percent_gpu() -> None:
    parsed = parse_ollama_ps(
        "NAME                    ID              SIZE      PROCESSOR    CONTEXT    UNTIL\n"
        "local-code-9b-64k       abc             6.6 GB    100% GPU     65536      4 minutes\n"
    )

    assert parsed == {
        "model_name": "local-code-9b-64k",
        "processor": "100% GPU",
        "context_tokens": 65536,
        "gpu_resident": True,
    }


def test_ollama_ps_rejects_cpu_or_wrong_context() -> None:
    with pytest.raises(ValueError, match="context"):
        parse_ollama_ps(
            "NAME ID SIZE PROCESSOR CONTEXT UNTIL\n"
            "local-code-9b-64k abc 6GB 50%/50% CPU/GPU 32768 1m\n"
        )


def test_usage_report_accepts_counts_but_not_raw_content(tmp_path: Path) -> None:
    usage = tmp_path / "usage.json"
    usage.write_text(
        json.dumps(
            {
                "model": "local-code-9b-64k",
                "prompt_tokens": 123,
                "completion_tokens": 45,
                "total_tokens": 168,
                "api_calls": 4,
            }
        ),
        encoding="utf-8",
    )

    assert parse_usage_report(usage) == {
        "prompt_tokens": 123,
        "completion_tokens": 45,
        "total_tokens": 168,
        "api_calls": 4,
    }

    usage.write_text(json.dumps({"response": "must not be persisted"}), encoding="utf-8")
    with pytest.raises(ValueError, match="usage"):
        parse_usage_report(usage)


def test_hermes_command_and_environment_cannot_fall_back_to_cloud(tmp_path: Path) -> None:
    config = BenchmarkConfig(lab_root=tmp_path, hermes_home=tmp_path / "hermes-home")
    command = build_hermes_command(config, tmp_path / "workspace", tmp_path / "usage.json")
    environment = build_hermes_environment(config, tmp_path / "workspace")

    assert command[:2] == ("hermes", "-z")
    assert "--provider" in command and command[command.index("--provider") + 1] == "custom"
    assert "--ignore-user-config" not in command
    assert environment["HERMES_HOME"] == str(tmp_path / "hermes-home")
    assert environment["TERMINAL_ENV"] == "docker"
    assert environment["TERMINAL_DOCKER_NETWORK"] == "false"
    assert environment["TERMINAL_DOCKER_FORWARD_ENV"] == "[]"
    assert "OPENROUTER_API_KEY" not in environment


def test_docker_sandbox_uses_no_network_and_only_workspace_mount(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_run(args: tuple[str, ...], **kwargs: object) -> object:
        captured["args"] = args
        captured.update(kwargs)
        return type("Completed", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr("local_code_hermes.sandbox.subprocess.run", fake_run)
    sandbox = DockerSandbox(tmp_path, image="python:3.12-alpine")

    result = sandbox.run(("python", "-I", "-c", "print('ok')"))

    args = captured["args"]
    assert isinstance(args, tuple)
    assert "--network=none" in args
    assert "--cap-drop=ALL" in args
    assert "--security-opt=no-new-privileges" in args
    assert any(str(tmp_path) in item for item in args)
    assert result.returncode == 0


def test_run_benchmark_blocks_without_invoking_hermes_when_preflight_is_not_green(
    tmp_path: Path,
) -> None:
    calls: list[object] = []
    config = BenchmarkConfig(lab_root=tmp_path, hermes_home=tmp_path / "hermes-home")
    blocked = PreflightReport(
        mode="formal",
        gates=tuple(
            GateResult(
                gate_id,
                "blocked" if gate_id == "git.head" else "passed",
                gate_id == "git.head",
                "worktree_dirty" if gate_id == "git.head" else "synthetic_ok",
                {},
            )
            for gate_id in REQUIRED_GATE_IDS
        ),
    )

    result = run_benchmark(
        config,
        preflight=blocked,
        process_runner=lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    assert result.outcome == "blocked"
    assert result.reason == "preflight_not_green"
    assert calls == []


def test_benchmark_report_roundtrips_as_sanitized_jsonl(tmp_path: Path) -> None:
    config = BenchmarkConfig(
        lab_root=tmp_path,
        runs_dir=tmp_path / ".local" / "runs",
        hermes_home=tmp_path / ".local" / "hermes-home",
        network_proof_id="FW-LOCAL-001",
        server_profile_proof_id="OLLAMA-PROFILE-001",
    )
    report = BenchmarkReport(
        outcome="blocked",
        reason="preflight_not_green",
        run_id="run-benchmark-synthetic",
        preflight_outcome="blocked",
    )
    path = write_benchmark_report(
        report,
        config.runs_dir,
        config,
        PreflightReport(mode="formal", gates=()),
    )

    summary = validate_path(path)

    assert summary["terminal_event"] == "run.blocked"
    serialized = path.read_text(encoding="utf-8")
    assert "preflight_not_green" in serialized
    assert "Solve the B-CODE" not in serialized
