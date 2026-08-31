from __future__ import annotations

import json
import runpy
import shutil
from pathlib import Path

import pytest

from local_code_hermes import fixture


def _candidate(tmp_path: Path) -> Path:
    destination = tmp_path / "candidate"
    shutil.copytree(fixture.PROJECT_ROOT, destination)
    return destination


def _apply_expected_fix_and_test(workspace: Path) -> None:
    source = workspace / "src" / "pricing.py"
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "discount_percent >= 100",
            "discount_percent > 100",
        ),
        encoding="utf-8",
    )
    tests = workspace / "tests" / "test_pricing.py"
    test_text = tests.read_text(encoding="utf-8")
    added = (
        "\n    def test_discount_above_100_is_rejected(self) -> None:\n"
        "        with self.assertRaises(ValueError):\n"
        "            apply_discount(1000, 101)\n"
    )
    tests.write_text(
        test_text.replace("\n\nif __name__", f"{added}\nif __name__"),
        encoding="utf-8",
    )


def test_frozen_fixture_hashes_match_manifest() -> None:
    fixture.verify_source_fixture()


def test_frozen_fixture_starts_red_at_the_100_percent_boundary() -> None:
    namespace = runpy.run_path(fixture.PROJECT_ROOT / "src" / "pricing.py")
    apply_discount = namespace["apply_discount"]

    assert apply_discount(1000, 25) == 750
    with pytest.raises(ValueError):
        apply_discount(1000, 100)


def test_manifest_maps_local_fixture_to_master_benchmark_case() -> None:
    manifest = fixture.load_manifest()

    assert manifest["case_id"] == "B-CODE-003@0.1.0"
    assert manifest["fixture_id"] == "pricing-boundary-v1"
    assert set(manifest["allowed_changes"]) == {
        "src/pricing.py",
        "tests/test_pricing.py",
    }
    assert "test_discount_above_100_is_rejected" in manifest["required_test_methods"]


def test_unmodified_fixture_is_not_a_passing_solution(tmp_path: Path) -> None:
    workspace = _candidate(tmp_path)

    result = fixture.verify_workspace(workspace, execute_tests=False)

    assert not result.passed
    assert "changed_files_mismatch" in result.codes
    assert "required_tests_missing" in result.codes
    assert result.changed_files == ()


def test_expected_test_first_change_set_is_accepted_without_running_processes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _candidate(tmp_path)
    _apply_expected_fix_and_test(workspace)
    monkeypatch.setattr(
        fixture.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("No se debe ejecutar subprocess con execute_tests=False")
        ),
    )

    result = fixture.verify_workspace(workspace, execute_tests=False)

    assert result.passed
    assert result.codes == ()
    assert result.changed_files == ("src/pricing.py", "tests/test_pricing.py")


def test_empty_named_tests_cannot_satisfy_test_first_contract(tmp_path: Path) -> None:
    workspace = _candidate(tmp_path)
    source = workspace / "src" / "pricing.py"
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "discount_percent >= 100",
            "discount_percent > 100",
        ),
        encoding="utf-8",
    )
    methods = "\n".join(
        f"    def {name}(self) -> None:\n        pass"
        for name in fixture.load_manifest()["required_test_methods"]
    )
    (workspace / "tests" / "test_pricing.py").write_text(
        f"import unittest\n\nclass PricingTests(unittest.TestCase):\n{methods}\n",
        encoding="utf-8",
    )

    result = fixture.verify_workspace(workspace, execute_tests=True)

    assert not result.passed
    assert "test_quality_check_failed" in result.codes


def test_hidden_semantics_preserve_negative_input_regressions(tmp_path: Path) -> None:
    workspace = _candidate(tmp_path)
    _apply_expected_fix_and_test(workspace)
    source = workspace / "src" / "pricing.py"
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "discount_percent < 0 or discount_percent > 100",
            "discount_percent > 100",
        ),
        encoding="utf-8",
    )

    result = fixture.verify_workspace(workspace, execute_tests=True)

    assert not result.passed
    assert "hidden_semantic_check_failed" in result.codes


def test_verifier_uses_injected_check_result_instead_of_real_subprocess(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _candidate(tmp_path)
    _apply_expected_fix_and_test(workspace)
    monkeypatch.setattr(fixture, "_run_checks", lambda workspace: (True, False, True))

    result = fixture.verify_workspace(workspace, execute_tests=True)

    assert not result.passed
    assert result.codes == ("hidden_semantic_check_failed",)


def test_extra_file_or_test_only_edit_is_rejected(tmp_path: Path) -> None:
    extra_workspace = _candidate(tmp_path / "extra")
    (extra_workspace / "notes.txt").write_text("synthetic", encoding="utf-8")
    extra = fixture.verify_workspace(extra_workspace, execute_tests=False)
    assert "file_set_changed" in extra.codes

    test_only_workspace = _candidate(tmp_path / "test-only")
    tests = test_only_workspace / "tests" / "test_pricing.py"
    tests.write_text(
        tests.read_text(encoding="utf-8").replace(
            "\n\nif __name__",
            "\n    def test_discount_above_100_is_rejected(self) -> None:\n"
            "        with self.assertRaises(ValueError):\n"
            "            apply_discount(1000, 101)\n\n"
            "if __name__",
        ),
        encoding="utf-8",
    )
    test_only = fixture.verify_workspace(test_only_workspace, execute_tests=False)
    assert "changed_files_mismatch" in test_only.codes


def test_prepare_workspace_is_contained_and_non_overwriting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspaces = tmp_path / "workspaces"
    monkeypatch.setattr(fixture, "WORKSPACES_ROOT", workspaces)

    created = fixture.prepare_workspace("run-001")

    assert created == workspaces / "run-001"
    assert (created / "src" / "pricing.py").is_file()
    with pytest.raises(FileExistsError):
        fixture.prepare_workspace("run-001")
    with pytest.raises(ValueError):
        fixture.prepare_workspace("../escape")


def test_manifest_rejects_wrong_case_or_invalid_hash(tmp_path: Path) -> None:
    bad_case = tmp_path / "bad-case.json"
    bad_case.write_text(
        json.dumps(
            {
                "case_id": "CODE-LOCAL-001@1.0.0",
                "files": {"src/pricing.py": "a" * 64},
                "allowed_changes": ["src/pricing.py"],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Manifest"):
        fixture.load_manifest(bad_case)

    bad_hash = tmp_path / "bad-hash.json"
    bad_hash.write_text(
        json.dumps(
            {
                "case_id": "B-CODE-003@0.1.0",
                "files": {"src/pricing.py": "not-a-sha"},
                "allowed_changes": ["src/pricing.py"],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Hashes"):
        fixture.load_manifest(bad_hash)
