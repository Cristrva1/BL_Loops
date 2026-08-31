from __future__ import annotations

from datetime import UTC, datetime

import pytest
from prompt_agent_factory.api_models import FactoryIntake
from prompt_agent_factory.contracts import AgentSpec, PromptSpec
from prompt_agent_factory.factory import build_artifact
from prompt_agent_factory.hashing import has_valid_content_hash
from pydantic import ValidationError

FIXED_TIME = datetime(2026, 8, 28, 12, 0, tzinfo=UTC)


def test_models_reject_unknown_fields(prompt_intake: FactoryIntake) -> None:
    payload = prompt_intake.model_dump(mode="json") | {"invented_field": True}
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        FactoryIntake.model_validate(payload)


def test_prompt_contract_is_strict_and_hashed(prompt_intake: FactoryIntake) -> None:
    result = build_artifact(prompt_intake, now=FIXED_TIME)

    assert isinstance(result.artifact, PromptSpec)
    assert result.artifact.generator_model == "deterministic-template@1.0.0"
    assert result.artifact.permissions.default_effect == "deny"
    assert result.artifact.permissions.runtime_network is False
    assert has_valid_content_hash(result.artifact)
    assert len(result.artifact.content_hash) == 64


def test_agent_contract_bounds_authority(agent_intake: FactoryIntake) -> None:
    result = build_artifact(agent_intake, now=FIXED_TIME)

    assert isinstance(result.artifact, AgentSpec)
    assert result.artifact.max_steps == 4
    assert result.artifact.memory.long_term is False
    assert result.artifact.memory.stores_raw_pii is False
    assert result.artifact.tools[0].mode == "simulated"
    assert result.artifact.tools[0].requires_approval is True
    assert result.artifact.permissions.default_effect == "deny"
    assert result.artifact.permissions.external_writes is False


def test_content_change_invalidates_hash(prompt_intake: FactoryIntake) -> None:
    artifact = build_artifact(prompt_intake, now=FIXED_TIME).artifact
    artifact.title = "Título modificado después de validar"

    assert has_valid_content_hash(artifact) is False


def test_generated_schema_forbids_extra_properties() -> None:
    prompt_schema = PromptSpec.model_json_schema()
    agent_schema = AgentSpec.model_json_schema()

    assert prompt_schema["additionalProperties"] is False
    assert agent_schema["additionalProperties"] is False
