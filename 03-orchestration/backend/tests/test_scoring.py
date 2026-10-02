from helpers import FAILING_GUIDE, PASSING_GUIDE
from orchestration.scoring import score_guide


def test_passing_guide_meets_every_check() -> None:
    result = score_guide(PASSING_GUIDE)

    assert result.passed is True
    assert result.checks_passed == result.checks_total
    assert "Objetivo" in result.headings


def test_failing_guide_detects_cloud_and_missing_structure() -> None:
    result = score_guide(FAILING_GUIDE)
    failed = {check.check_id: check for check in result.checks if not check.passed}

    assert result.passed is False
    assert "has_objetivo" in failed
    assert "mentions_ollama" in failed
    assert "has_powershell" in failed
    assert "no_cloud_fallback" in failed
    assert "chatgpt" in failed["no_cloud_fallback"].evidence.casefold()
