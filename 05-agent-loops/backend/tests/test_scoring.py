from agent_loops.scoring import score_output
from helpers import FAILING_OUTPUT, MID_OUTPUT, PASSING_OUTPUT


def test_passing_output_meets_every_check() -> None:
    result = score_output(PASSING_OUTPUT)

    assert result.passed is True
    assert result.checks_passed == 5
    assert result.checks_total == 5


def test_prose_fails_json_and_the_rest() -> None:
    result = score_output(FAILING_OUTPUT)
    failed = {check.check_id for check in result.checks if not check.passed}

    assert result.passed is False
    assert result.checks_passed == 0
    assert "is_json_object" in failed
    assert "has_title" in failed
    assert "has_stop_condition" in failed


def test_partial_json_scores_four_of_five() -> None:
    result = score_output(MID_OUTPUT)
    failed = {check.check_id for check in result.checks if not check.passed}

    assert result.passed is False
    assert result.checks_passed == 4
    assert failed == {"has_stop_condition"}
