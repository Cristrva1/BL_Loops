"""Contratos del estudio: configuración local, lectura de la salida del modelo y fallback visible."""

import json
from pathlib import Path

import httpx
import pytest
from pydantic import ValidationError

from open_genai_studio.config import ConfigurationError, Settings
from open_genai_studio.evaluation import export_evaluation_jsonl
from open_genai_studio.model_output import short_reason, strip_code_fence
from open_genai_studio.prompt_expander import PromptStudioExpander, parse_expansion
from open_genai_studio.schemas import (
    CameraMovement,
    EvaluationRecord,
    PromptExpansionRequest,
    ShotType,
    StoryboardProject,
)
from open_genai_studio.storyboard_engine import (
    DEFAULT_SHOTS,
    OpenGenAIStoryboardEngine,
    parse_shots,
)

RELEVANT = (
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "BL_LOOPS_MODEL_STANDARD",
    "HOST",
    "PORT",
    "ANIMATIC_FONT_FILE",
)

MODEL_SHOTS = [
    {
        "shot_type": "extreme wide shot",
        "camera_movement": "slow pan right",
        "headline": "Faro en la niebla",
        "description": "Un faro solitario aparece entre la bruma.",
        "prompt_expansion": "Wide establishing shot of a lonely lighthouse in dense fog, 35mm",
        "lighting": "Blue hour, soft haze",
        "accent_color": "#38bdf8",
    },
    {"shot_type": "Medium Shot", "camera_movement": "Tracking Shot", "headline": "La farera"},
    {"shot_type": "Close-up", "camera_movement": "Dolly In (Push In)", "headline": "La lámpara"},
    {"shot_type": "Wide Shot", "camera_movement": "Crane Down", "headline": "El barco"},
]


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for name in RELEVANT:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def mock_ollama(monkeypatch: pytest.MonkeyPatch, handler) -> None:
    """Sustituye la red por un transporte en memoria: las pruebas nunca llaman a Ollama."""

    real_client = httpx.AsyncClient

    def factory(**kwargs):
        return real_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", factory)


def ollama_reply(text: str):
    return lambda _request: httpx.Response(200, json={"response": text})


# --- Configuración -------------------------------------------------------------------------


def test_defaults_are_local(clean_env: pytest.MonkeyPatch, tmp_path: Path) -> None:
    settings = Settings.load(tmp_path / "lab")

    assert settings.ollama_base_url == "http://127.0.0.1:11434"
    assert settings.ollama_model == "qwen3.5:9b"
    assert (settings.host, settings.port, settings.font_file) == ("127.0.0.1", 8024, None)


def test_lab_env_overrides_workspace_env_key_by_key(
    clean_env: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    lab = tmp_path / "lab"
    lab.mkdir()
    (tmp_path / ".env").write_text(
        "BL_LOOPS_MODEL_STANDARD=qwen3.5:4b\nPORT=9024\n", encoding="utf-8"
    )
    (lab / ".env").write_text("PORT=9124\n", encoding="utf-8")

    settings = Settings.load(lab)

    assert settings.ollama_model == "qwen3.5:4b"
    assert settings.port == 9124


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("OLLAMA_BASE_URL", "http://example.com:11434", "HTTP local"),
        ("OLLAMA_BASE_URL", "https://127.0.0.1:11434", "HTTP local"),
        ("OLLAMA_MODEL", "qwen3.5:cloud", "no cloud"),
        ("HOST", "0.0.0.0", "HOST debe ser"),
        ("PORT", "80", "entre 1024 y 65535"),
        ("ANIMATIC_FONT_FILE", "no-existe.ttf", "ANIMATIC_FONT_FILE"),
    ],
)
def test_unsafe_configuration_is_rejected(
    clean_env: pytest.MonkeyPatch, tmp_path: Path, name: str, value: str, message: str
) -> None:
    clean_env.setenv(name, value)

    with pytest.raises(ConfigurationError, match=message):
        Settings.load(tmp_path / "lab")


def test_requests_reject_cloud_models_and_impossible_durations() -> None:
    with pytest.raises(ValidationError, match="no cloud"):
        StoryboardProject(model="gpt-oss:120b-cloud")
    with pytest.raises(ValidationError):
        StoryboardProject(total_duration_target=2.0)
    with pytest.raises(ValidationError, match="no cloud"):
        PromptExpansionRequest(model="qwen3.5:cloud")


# --- Lectura de la salida del modelo ------------------------------------------------------------


def test_strip_code_fence_and_short_reason() -> None:
    assert strip_code_fence('```json\n[{"a": 1}]\n```') == '[{"a": 1}]'
    assert strip_code_fence("Aquí está:\n```\n{}\n```") == "{}"
    assert strip_code_fence("  [1, 2] ") == "[1, 2]"
    assert short_reason(ValueError("uno\n  dos")) == "uno dos"
    assert len(short_reason(ValueError("x" * 500))) == 160


def test_parse_shots_accepts_fences_wrappers_and_case_insensitive_enums() -> None:
    fenced = "```json\n" + json.dumps(MODEL_SHOTS) + "\n```"
    wrapped = json.dumps({"shots": MODEL_SHOTS})

    for raw in (fenced, wrapped):
        shots = parse_shots(raw, duration_seconds=2.5)
        assert [shot.shot_number for shot in shots] == [1, 2, 3, 4]
        assert shots[0].shot_type is ShotType.EXTREME_WIDE
        assert shots[0].camera_movement is CameraMovement.SLOW_PAN_RIGHT
        assert {shot.duration_seconds for shot in shots} == {2.5}


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ("no es json", "Expecting value"),
        (json.dumps({"titulo": "sin planos"}), "no contiene una lista"),
        (json.dumps(MODEL_SHOTS[:1]), "se esperaban 4 planos y llegaron 1"),
        (json.dumps([*MODEL_SHOTS[:3], "texto"]), "el plano 4 no es un objeto"),
        (
            json.dumps([*MODEL_SHOTS[:3], {"shot_type": "Plano holandés"}]),
            "shot_type desconocido",
        ),
    ],
)
def test_parse_shots_explains_why_a_response_is_rejected(payload: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse_shots(payload, duration_seconds=3.0)


def test_parse_expansion_normalizes_the_four_keys() -> None:
    raw = json.dumps(
        {
            "positive_prompt": "Lighthouse in fog, anamorphic 35mm",
            "camera_settings": {"lens": "35mm", "aperture": "f/2.0"},
            "mood_palette": "#0ea5e9, amber",
        }
    )

    result = parse_expansion(raw)

    assert result == {
        "positive_prompt": "Lighthouse in fog, anamorphic 35mm",
        "negative_prompt": "",
        "camera_settings": "lens: 35mm, aperture: f/2.0",
        "mood_palette": ["#0ea5e9", "amber"],
    }
    with pytest.raises(ValueError, match="positive_prompt"):
        parse_expansion(json.dumps({"negative_prompt": "blurry"}))


# --- Fallback visible ---------------------------------------------------------------------------


async def test_storyboard_uses_the_model_when_it_honours_the_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_ollama(monkeypatch, ollama_reply(json.dumps(MODEL_SHOTS)))
    engine = OpenGenAIStoryboardEngine()

    shots = await engine.generate_storyboard(StoryboardProject(total_duration_target=10.0))

    assert engine.last_source == "ollama"
    assert engine.last_fallback_reason is None
    assert shots[0].headline == "Faro en la niebla"
    assert sum(shot.duration_seconds for shot in shots) == 10.0


async def test_storyboard_fallback_explains_an_out_of_contract_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_ollama(monkeypatch, ollama_reply(json.dumps(MODEL_SHOTS[:2])))
    engine = OpenGenAIStoryboardEngine()

    shots = await engine.generate_storyboard(StoryboardProject())

    assert engine.last_source == "fallback"
    assert engine.last_fallback_reason == (
        "respuesta no válida: se esperaban 4 planos y llegaron 2"
    )
    assert [shot.headline for shot in shots] == [shot.headline for shot in DEFAULT_SHOTS]


async def test_storyboard_fallback_when_ollama_is_unreachable() -> None:
    engine = OpenGenAIStoryboardEngine(base_url="http://127.0.0.1:9", model="no-existe")

    shots = await engine.generate_storyboard(StoryboardProject())

    assert len(shots) == len(DEFAULT_SHOTS)
    assert engine.last_source == "fallback"
    assert "al consultar Ollama" in (engine.last_fallback_reason or "")


async def test_prompt_expander_reports_http_errors_as_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_ollama(monkeypatch, lambda _request: httpx.Response(404, json={"error": "model"}))
    expander = PromptStudioExpander()

    result = await expander.expand_prompt(PromptExpansionRequest(raw_idea="Un faro en la niebla"))

    assert expander.last_source == "fallback"
    assert expander.last_fallback_reason == "Ollama respondió HTTP 404"
    assert "Un faro en la niebla" in result["positive_prompt"]


# --- Exportación ----------------------------------------------------------------------------


def test_export_appends_one_json_line_per_run(tmp_path: Path) -> None:
    record = EvaluationRecord(
        case_id="EVAL-OPEN-GENAI-001",
        model="qwen3.5:9b",
        success=True,
        duration_actual=12.0,
        duration_expected=12.0,
        render_time_seconds=3.1,
        file_size_kb=120.5,
        shots_count=4,
        metrics={"director_source": "fallback"},
    )
    target = tmp_path / "eval.jsonl"

    export_evaluation_jsonl(record, target)
    export_evaluation_jsonl(record, target)

    lines = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 2
    assert lines[0]["lab_id"] == "24-open-generative-ai-studio"
    assert lines[0]["metrics"] == {"director_source": "fallback"}
