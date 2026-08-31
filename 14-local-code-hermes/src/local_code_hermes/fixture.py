"""Preparacion y verificacion determinista del fixture B-CODE-003."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from local_code_hermes.config import BENCHMARK_CASE_ID, LAB_ROOT

CASE_ROOT = LAB_ROOT / "cases" / "B-CODE-003"
PROJECT_ROOT = CASE_ROOT / "project"
MANIFEST_PATH = CASE_ROOT / "manifest.json"
WORKSPACES_ROOT = LAB_ROOT / ".local" / "workspaces"
CACHE_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache"}
CheckExecutor = Callable[[tuple[str, ...], float], int]


@dataclass(frozen=True, slots=True)
class FixtureVerification:
    passed: bool
    codes: tuple[str, ...]
    changed_files: tuple[str, ...]


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_files(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("El fixture no admite enlaces simbolicos.")
        if not path.is_file() or any(part in CACHE_PARTS for part in path.parts):
            continue
        if path.suffix == ".pyc":
            continue
        relative = path.relative_to(root).as_posix()
        result[relative] = path
    return result


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, object]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("case_id") != BENCHMARK_CASE_ID:
        raise ValueError("Manifest de fixture invalido.")
    files = raw.get("files")
    allowed = raw.get("allowed_changes")
    if not isinstance(files, dict) or not isinstance(allowed, list):
        raise ValueError("Manifest incompleto.")
    if any(
        not isinstance(key, str)
        or not isinstance(value, str)
        or not re.fullmatch(r"[0-9a-f]{64}", value)
        for key, value in files.items()
    ):
        raise ValueError("Hashes del manifest invalidos.")
    if any(not isinstance(item, str) for item in allowed):
        raise ValueError("allowed_changes invalido.")
    return raw


def verify_source_fixture(
    project_root: Path = PROJECT_ROOT,
    manifest_path: Path = MANIFEST_PATH,
) -> None:
    manifest = load_manifest(manifest_path)
    expected = manifest["files"]
    actual_files = _relative_files(project_root)
    if set(actual_files) != set(expected):
        raise ValueError("Los archivos fuente no coinciden con el manifest.")
    for relative, path in actual_files.items():
        if _hash(path) != expected[relative]:
            raise ValueError(f"Hash fuente inesperado: {relative}")


def prepare_workspace(run_label: str, *, workspaces_root: Path | None = None) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,63}", run_label):
        raise ValueError("Identificador de workspace invalido.")
    verify_source_fixture()
    root = (workspaces_root or WORKSPACES_ROOT).resolve()
    destination = (root / run_label).resolve()
    if not destination.is_relative_to(root):
        raise ValueError("El workspace sale del laboratorio.")
    if destination.exists():
        raise FileExistsError("El workspace ya existe.")
    root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(PROJECT_ROOT, destination)
    return destination


def _safe_test_environment() -> dict[str, str]:
    allowed = ("PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "TEMP", "TMP")
    return {name: os.environ[name] for name in allowed if name in os.environ}


def _run_checks(
    workspace: Path,
    check_executor: CheckExecutor | None = None,
) -> tuple[bool, bool, bool]:
    environment = _safe_test_environment()

    def execute(args: tuple[str, ...], timeout: float) -> int:
        if check_executor is not None:
            return check_executor(args, timeout)
        completed = subprocess.run(
            args,
            cwd=workspace,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            shell=False,
        )
        return completed.returncode

    unit_code = execute(
        (sys.executable, "-I", "-m", "unittest", "discover", "-s", "tests", "-v"),
        30,
    )
    semantic_code = """
import runpy

f = runpy.run_path("src/pricing.py")["apply_discount"]
assert f(1000, 0) == 1000
assert f(1000, 25) == 750
assert f(1000, 100) == 0
for args in ((-1, 0), (1000, -1), (1000, 101)):
    try:
        f(*args)
    except ValueError:
        pass
    else:
        raise AssertionError(f"ValueError esperado para {args!r}")
""".strip()
    semantic_code_result = execute((sys.executable, "-I", "-c", semantic_code), 15)
    quality_code = """
import runpy
import unittest

namespace = runpy.run_path("tests/test_pricing.py")
test_cases = {
    "test_zero_discount_keeps_total": (1000, 0),
    "test_quarter_discount": (1000, 25),
    "test_full_discount_is_zero": (1000, 100),
    "test_discount_above_100_is_rejected": (1000, 101),
}
classes = [
    value
    for value in namespace.values()
    if isinstance(value, type)
    and issubclass(value, unittest.TestCase)
    and value is not unittest.TestCase
]
for method_name, expected_call in test_cases.items():
    owner = next((candidate for candidate in classes if hasattr(candidate, method_name)), None)
    if owner is None:
        raise AssertionError(f"TestCase requerido no encontrado: {method_name}")
    method = getattr(owner, method_name)
    calls = []

    def mutant(*args, **kwargs):
        calls.append(args)
        return -999_999

    method.__globals__["apply_discount"] = mutant
    result = unittest.TestResult()
    owner(method_name).run(result)
    if expected_call not in calls:
        raise AssertionError(f"El test no ejercita {expected_call!r}: {method_name}")
    if result.wasSuccessful():
        raise AssertionError(f"El test no detecta una implementacion mutante: {method_name}")
""".strip()
    quality_code_result = execute((sys.executable, "-I", "-c", quality_code), 15)
    return unit_code == 0, semantic_code_result == 0, quality_code_result == 0


def verify_workspace(
    workspace: Path,
    *,
    manifest_path: Path = MANIFEST_PATH,
    execute_tests: bool = True,
    check_executor: CheckExecutor | None = None,
) -> FixtureVerification:
    manifest = load_manifest(manifest_path)
    expected = manifest["files"]
    allowed = set(manifest["allowed_changes"])
    actual = _relative_files(workspace)
    codes: list[str] = []
    if set(actual) != set(expected):
        codes.append("file_set_changed")
    changed = {
        relative
        for relative, expected_hash in expected.items()
        if relative in actual and _hash(actual[relative]) != expected_hash
    }
    if changed != allowed:
        codes.append("changed_files_mismatch")

    tests_path = workspace / "tests" / "test_pricing.py"
    if tests_path.is_file():
        try:
            test_tree = ast.parse(tests_path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeError):
            codes.append("tests_unparseable")
        else:
            discovered_methods = {
                item.name
                for node in test_tree.body
                if isinstance(node, ast.ClassDef)
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name.startswith("test_")
            }
            required_tests = manifest.get("required_test_methods", [])
            if (
                not isinstance(required_tests, list)
                or any(not isinstance(name, str) for name in required_tests)
                or not set(required_tests).issubset(discovered_methods)
            ):
                codes.append("required_tests_missing")
    else:
        codes.append("tests_missing")

    if execute_tests:
        if check_executor is None:
            unit_passed, semantic_passed, quality_passed = _run_checks(workspace)
        else:
            unit_passed, semantic_passed, quality_passed = _run_checks(
                workspace,
                check_executor,
            )
        if not unit_passed:
            codes.append("unittest_failed")
        if not semantic_passed:
            codes.append("hidden_semantic_check_failed")
        if not quality_passed:
            codes.append("test_quality_check_failed")
    return FixtureVerification(
        passed=not codes,
        codes=tuple(codes),
        changed_files=tuple(sorted(changed)),
    )


def cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepara o verifica B-CODE-003.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("run_label")
    verify = subparsers.add_parser("verify")
    verify.add_argument("run_label")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            destination = prepare_workspace(args.run_label)
            print(f"Workspace preparado: .local/workspaces/{destination.name}")
            return 0
        workspace = (WORKSPACES_ROOT / args.run_label).resolve()
        if not workspace.is_relative_to(WORKSPACES_ROOT.resolve()) or not workspace.is_dir():
            raise ValueError("Workspace no permitido o inexistente.")
        result = verify_workspace(workspace)
    except (FileExistsError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Fixture no verificable: {type(exc).__name__}")
        return 1
    if result.passed:
        print("Fixture aprobado; archivos permitidos y pruebas verificadas.")
        return 0
    print(f"Fixture no aprobado: {','.join(result.codes)}")
    return 1


def main() -> None:
    raise SystemExit(cli())
