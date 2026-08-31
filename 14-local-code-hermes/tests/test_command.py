from pathlib import Path
from types import SimpleNamespace

import pytest

from local_code_hermes.command import (
    OUTPUT_LIMIT,
    CommandRequest,
    SubprocessCommandRunner,
)


def test_real_runner_contract_uses_argv_shell_false_and_timeout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    def fake_run(args: tuple[str, ...], **kwargs: object) -> SimpleNamespace:
        captured["args"] = args
        captured.update(kwargs)
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("local_code_hermes.command.subprocess.run", fake_run)
    request = CommandRequest(
        args=("synthetic-tool", "--version"),
        cwd=tmp_path,
        env_overrides={"SYNTHETIC_FLAG": "1"},
        timeout_seconds=3,
    )

    result = SubprocessCommandRunner().run(request)

    assert result.returncode == 0
    assert captured["args"] == request.args
    assert captured["cwd"] == tmp_path
    assert captured["shell"] is False
    assert captured["check"] is False
    assert captured["timeout"] == 3
    assert captured["env"]["SYNTHETIC_FLAG"] == "1"  # type: ignore[index]


def test_real_runner_maps_missing_command_and_timeout_without_executing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = CommandRequest(args=("synthetic-tool",))
    monkeypatch.setattr(
        "local_code_hermes.command.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError()),
    )
    missing = SubprocessCommandRunner().run(request)
    assert (missing.returncode, missing.error_kind) == (127, "not_found")

    from subprocess import TimeoutExpired

    monkeypatch.setattr(
        "local_code_hermes.command.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutExpired("synthetic", 1)),
    )
    timed_out = SubprocessCommandRunner().run(request)
    assert (timed_out.returncode, timed_out.error_kind) == (124, "timeout")


def test_real_runner_caps_captured_output(monkeypatch: pytest.MonkeyPatch) -> None:
    oversized = "x" * (OUTPUT_LIMIT + 100)
    monkeypatch.setattr(
        "local_code_hermes.command.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout=oversized,
            stderr=oversized,
        ),
    )

    result = SubprocessCommandRunner().run(CommandRequest(args=("synthetic-tool",)))

    assert len(result.stdout) == OUTPUT_LIMIT
    assert len(result.stderr) == OUTPUT_LIMIT
