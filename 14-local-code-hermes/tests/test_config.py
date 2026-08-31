from pathlib import Path

import pytest

from local_code_hermes.config import (
    BENCHMARK_CASE_ID,
    MODEL_NAME,
    NUM_CTX,
    PREFLIGHT_CASE_ID,
    SCHEMA_VERSION,
    SOURCE_MODEL,
    PreflightConfig,
    contained_path,
    is_loopback_http_endpoint,
    is_safe_proof_id,
)


@pytest.mark.parametrize(
    "endpoint",
    (
        "http://127.0.0.1:11434",
        "http://127.12.34.56:11434/",
        "http://localhost:11434",
        "http://LOCALHOST.:11434",
        "http://[::1]:11434",
    ),
)
def test_loopback_http_endpoints_are_accepted(endpoint: str) -> None:
    assert is_loopback_http_endpoint(endpoint)


@pytest.mark.parametrize(
    "endpoint",
    (
        "https://127.0.0.1:11434",
        "http://192.168.1.10:11434",
        "http://127.0.0.1.example:11434",
        "http://user:password@127.0.0.1:11434",
        "http://127.0.0.1:11434/api/tags",
        "http://127.0.0.1:11434?model=cloud",
        "file:///tmp/ollama.sock",
        "not-a-url",
    ),
)
def test_non_loopback_or_ambiguous_endpoints_are_rejected(endpoint: str) -> None:
    assert not is_loopback_http_endpoint(endpoint)


def test_proof_ids_are_restricted_identifiers() -> None:
    assert is_safe_proof_id("FW-LOCAL-001")
    assert is_safe_proof_id("FW-LOCAL-001", required_prefix="FW-")
    assert is_safe_proof_id("OLLAMA-PROFILE-001", required_prefix="OLLAMA-")
    assert not is_safe_proof_id("sk-ABC123secret", required_prefix="FW-")
    assert not is_safe_proof_id("FW-LOCAL-001", required_prefix="OLLAMA-")
    assert not is_safe_proof_id(None)
    assert not is_safe_proof_id("x")
    assert not is_safe_proof_id("proof with spaces")
    assert not is_safe_proof_id("C:\\private\\proof.txt")


def test_contained_path_rejects_absolute_and_parent_escape(tmp_path: Path) -> None:
    assert contained_path(tmp_path, Path(".local/runs")) == tmp_path / ".local" / "runs"
    with pytest.raises(ValueError, match="relativa"):
        contained_path(tmp_path, tmp_path / "outside")
    with pytest.raises(ValueError, match="sale"):
        contained_path(tmp_path, Path("../outside"))


def test_contract_constants_use_master_case_taxonomy() -> None:
    assert SCHEMA_VERSION == "1.1"
    assert PREFLIGHT_CASE_ID == "F-LOCAL-CODE-004@0.1.0"
    assert BENCHMARK_CASE_ID == "B-CODE-003@0.1.0"
    assert MODEL_NAME == "local-code-9b-64k"
    assert SOURCE_MODEL == "qwen3.5:9b"
    assert NUM_CTX == 65_536


def test_defaults_are_conservative_for_a_9b_64k_preflight() -> None:
    config = PreflightConfig(python_version=(3, 12))

    assert config.min_ram_available_gib >= 8
    assert config.min_commit_headroom_gib >= 8
    assert config.min_vram_free_mib >= 12_000
    assert config.network_proof == "unverified"
    assert config.server_profile_proof == "unverified"


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("mode", "unknown"),
        ("network_proof", "socket-observed"),
        ("server_profile_proof", "client-env-only"),
        ("expected_num_ctx", 0),
        ("min_ram_available_gib", -1),
        ("min_commit_headroom_gib", -1),
        ("min_vram_free_mib", -1),
        ("command_timeout_seconds", 0),
    ),
)
def test_invalid_configuration_fails_closed(field: str, value: object) -> None:
    with pytest.raises(ValueError):
        PreflightConfig(**{field: value})  # type: ignore[arg-type]
