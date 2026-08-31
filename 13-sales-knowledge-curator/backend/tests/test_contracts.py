from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from sales_curator.contracts.models import ClaimRecord, SourceRecord

LAB_ROOT = Path(__file__).resolve().parents[2]


def test_valid_source_fixture_is_accepted() -> None:
    payload = json.loads(
        (LAB_ROOT / "fixtures/expected/valid/source-min.json").read_text(encoding="utf-8")
    )
    SourceRecord.model_validate(payload)


def test_extra_truth_score_is_rejected() -> None:
    payload = json.loads(
        (LAB_ROOT / "fixtures/expected/invalid/source-extra-field.json").read_text(encoding="utf-8")
    )
    with pytest.raises(ValidationError):
        SourceRecord.model_validate(payload)


def test_invalid_claim_type_is_rejected() -> None:
    payload = json.loads(
        (LAB_ROOT / "fixtures/expected/invalid/claim-bad-type.json").read_text(encoding="utf-8")
    )
    with pytest.raises(ValidationError):
        ClaimRecord.model_validate(payload)
