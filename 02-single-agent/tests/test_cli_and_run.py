import io
import json
from pathlib import Path

from single_agent.cli import _configure_output_encoding, run_chat
from single_agent.config import Settings
from single_agent.ollama_client import ChatResult, OllamaError
from single_agent.validation import validate_run


class RememberingClient:
    def __init__(self) -> None:
        self.calls: list[list[dict[str, str]]] = []

    def chat(self, messages: list[dict[str, str]]) -> ChatResult:
        self.calls.append(messages)
        return ChatResult(
            content=f"respuesta-{len(self.calls)}",
            model="gemma4:e4b",
            total_duration_ms=15.0,
            prompt_tokens=8,
            output_tokens=3,
        )


class FailingClient:
    def chat(self, _messages: list[dict[str, str]]) -> ChatResult:
        raise OllamaError("fallo didactico")


class InterruptedClient:
    def chat(self, _messages: list[dict[str, str]]) -> ChatResult:
        raise KeyboardInterrupt


class ReconfigurableOutput(io.StringIO):
    def __init__(self) -> None:
        super().__init__()
        self.configuration: tuple[str, str] | None = None

    def reconfigure(self, *, encoding: str, errors: str) -> None:
        self.configuration = (encoding, errors)


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        root=tmp_path,
        base_url="http://127.0.0.1:11434",
        model="gemma4:e4b",
        timeout_seconds=10,
        runs_dir=tmp_path / ".local" / "runs",
    )


def _input_for(values: list[str]):
    iterator = iter(values)
    return lambda _prompt: next(iterator)


def test_chat_keeps_context_in_memory_and_exports_sanitized_jsonl(tmp_path: Path) -> None:
    client = RememberingClient()
    output = io.StringIO()

    exit_code = run_chat(
        _settings(tmp_path),
        client=client,
        input_fn=_input_for(["dato-ultrasecreto", "recuerdalo", "/salir"]),
        output=output,
    )

    assert exit_code == 0
    assert len(client.calls) == 2
    assert client.calls[1][1:] == [
        {"role": "user", "content": "dato-ultrasecreto"},
        {"role": "assistant", "content": "respuesta-1"},
        {"role": "user", "content": "recuerdalo"},
    ]
    assert "Agente > respuesta-2" in output.getvalue()

    run_path = next(_settings(tmp_path).runs_dir.glob("*.jsonl"))
    summary = validate_run(run_path)
    raw_log = run_path.read_text(encoding="utf-8")
    assert summary.terminal_event == "run.completed"
    assert "dato-ultrasecreto" not in raw_log
    assert "respuesta-1" not in raw_log


def test_expected_ollama_error_is_visible_and_session_closes_cleanly(tmp_path: Path) -> None:
    output = io.StringIO()

    exit_code = run_chat(
        _settings(tmp_path),
        client=FailingClient(),
        input_fn=_input_for(["hola", "/salir"]),
        output=output,
    )

    assert exit_code == 0
    assert "Error > fallo didactico" in output.getvalue()
    run_path = next(_settings(tmp_path).runs_dir.glob("*.jsonl"))
    events = [json.loads(line) for line in run_path.read_text(encoding="utf-8").splitlines()]
    assert any(event["event_type"] == "error.raised" for event in events)
    assert events[-1]["event_type"] == "run.completed"


def test_windows_output_is_reconfigured_for_unicode() -> None:
    output = ReconfigurableOutput()

    _configure_output_encoding(output)

    assert output.configuration == ("utf-8", "replace")


def test_interrupt_during_model_call_closes_the_active_node(tmp_path: Path) -> None:
    output = io.StringIO()

    exit_code = run_chat(
        _settings(tmp_path),
        client=InterruptedClient(),
        input_fn=_input_for(["hola"]),
        output=output,
    )

    assert exit_code == 0
    run_path = next(_settings(tmp_path).runs_dir.glob("*.jsonl"))
    events = [json.loads(line) for line in run_path.read_text(encoding="utf-8").splitlines()]
    assert [event["event_type"] for event in events[-3:]] == [
        "error.raised",
        "node.failed",
        "run.completed",
    ]
    assert events[-1]["payload"]["reason"] == "keyboard_interrupt"
