from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

import pytest

from sales_curator.cli import cli
from sales_curator.config import Settings
from sales_curator.contracts.research import BookResearchReport, DocumentRights, RightsStatus
from sales_curator.orchestration.service import AuditRunFailed, CuratorService


def _rights_file(path: Path) -> Path:
    rights = DocumentRights(
        rights_status=RightsStatus.EXPLICIT_PERMISSION,
        license="school-permission",
        usage_basis="Permiso escrito de la escuela para investigación",
        jurisdiction="MX",
        retention_allowed=True,
        extraction_allowed=True,
        quotation_allowed=True,
        redistribution_allowed=False,
        notebooklm_upload_allowed=False,
        evidence="Carta local revisada por el operador responsable",
    )
    path.write_text(rights.model_dump_json(indent=2), encoding="utf-8")
    return path


def test_cli_version_comes_from_distribution_metadata(monkeypatch, capsys) -> None:
    monkeypatch.setattr("sales_curator.cli._application_version", lambda: "0.2.0")

    with pytest.raises(SystemExit) as exit_info:
        cli(["--version"])

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == "sales-curator 0.2.0"


def test_web_help_preserves_crawl4ai_attribution(capsys) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli(["web", "--help"])

    assert exit_info.value.code == 0
    assert "Crawl4AI by UncleCode" in capsys.readouterr().out


def test_cli_demo_stages_then_explicit_hash_publishes(
    monkeypatch, settings: Settings, corpus
) -> None:
    service = CuratorService(settings)

    def fake_service() -> CuratorService:
        return service

    monkeypatch.setattr("sales_curator.cli._service", fake_service)
    output = StringIO()
    code = cli(
        ["demo", "--fixture", str(corpus), "--reviewer", "operador-local", "--reason", "demo cli"],
        output=output,
    )
    assert code == 0
    text = output.getvalue()
    assert "candidate_id=" in text
    assert "candidate_hash=" in text
    assert "candidate_diff=" in text
    assert "state=staging" in text
    assert "release=" not in text

    staged = service.get_run(service.store.list_runs()[-1]["run_id"])
    publish_output = StringIO()
    code = cli(
        [
            "release",
            "publish",
            "--run",
            staged.workflow.run_id,
            "--candidate",
            staged.candidate_id,
            "--expected-hash",
            staged.candidate_hash,
            "--reviewer",
            "operador-local",
            "--reason",
            "Aprobacion CLI posterior sobre hash exacto",
        ],
        output=publish_output,
    )
    assert code == 0
    assert "state=published" in publish_output.getvalue()
    assert "release=" in publish_output.getvalue()


def test_cli_release_build_only_stages_without_reviewer_arguments(
    monkeypatch, settings: Settings, corpus
) -> None:
    service = CuratorService(settings)
    snapshot = service.start_audit(corpus)
    service.approve_publishable_claims(
        snapshot.workflow.run_id,
        "operador-local",
        "Aprobaciones de afirmaciones previas al candidato",
    )
    reviews_before = len(service.get_run(snapshot.workflow.run_id).reviews)
    monkeypatch.setattr("sales_curator.cli._service", lambda: service)
    output = StringIO()

    code = cli(
        ["release", "build", "--run", snapshot.workflow.run_id],
        output=output,
    )

    staged = service.get_run(snapshot.workflow.run_id)
    assert code == 0
    assert staged.workflow.state.value == "staging"
    assert len(staged.reviews) == reviews_before
    assert "candidate_id=" in output.getvalue()
    assert "candidate_hash=" in output.getvalue()


def test_cli_audit_propagates_extractor_and_domain_with_settings_default(
    monkeypatch, tmp_path: Path
) -> None:
    seen: list[dict[str, object]] = []
    snapshot = SimpleNamespace(
        workflow=SimpleNamespace(
            run_id="run_cli_audit",
            state=SimpleNamespace(value="review_pending"),
        ),
        sources=[],
        claims=[],
        conflicts=[],
        gaps=[],
        release_id=None,
        candidate_id=None,
        candidate_hash=None,
        candidate_diff=None,
        jsonl_path=".local/runs/run_cli_audit.jsonl",
    )

    class FakeService:
        settings = SimpleNamespace(research_domain="configured-school-sales")

        def start_audit(self, source: Path, **kwargs):
            seen.append({"source": source, **kwargs})
            return snapshot

    monkeypatch.setattr("sales_curator.cli._service", FakeService)
    source = tmp_path / "sources"
    source.mkdir()

    assert (
        cli(
            ["audit", "--source", str(source), "--extractor", "ollama"],
            output=StringIO(),
        )
        == 0
    )
    assert seen[-1]["extractor"] == "ollama"
    assert seen[-1]["domain"] == "configured-school-sales"

    assert (
        cli(
            [
                "audit",
                "--source",
                str(source),
                "--extractor",
                "deterministic",
                "--domain",
                "explicit-school-sales",
            ],
            output=StringIO(),
        )
        == 0
    )
    assert seen[-1]["extractor"] == "deterministic"
    assert seen[-1]["domain"] == "explicit-school-sales"


def test_cli_audit_failure_exposes_failed_run_and_jsonl(monkeypatch, tmp_path: Path) -> None:
    failure = AuditRunFailed(
        run_id="run_failed_cli",
        jsonl_path=tmp_path / "run_failed_cli.jsonl",
        reason="modelo ausente",
    )

    class FakeService:
        settings = SimpleNamespace(research_domain="configured-school-sales")

        def start_audit(self, *_args, **_kwargs):
            raise failure

    monkeypatch.setattr("sales_curator.cli._service", FakeService)
    errors = StringIO()

    code = cli(
        ["audit", "--source", str(tmp_path), "--extractor", "ollama"],
        error_output=errors,
    )

    assert code == 1
    assert "run_id=run_failed_cli" in errors.getvalue()
    assert "state=failed" in errors.getvalue()
    assert f"jsonl={failure.jsonl_path}" in errors.getvalue()


def test_cli_imports_authorized_document_with_explicit_inbox_and_rights(
    monkeypatch, tmp_path: Path
) -> None:
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    source = inbox / "authorized.pdf"
    source.write_bytes(b"synthetic-pdf")
    rights_path = _rights_file(tmp_path / "rights.json")
    output_root = tmp_path / "documents"
    seen: dict[str, object] = {}

    def fake_import(path: Path, **kwargs):
        seen.update({"path": path, **kwargs})
        return SimpleNamespace(
            document_id="doc_0123456789abcdef",
            manifest_path="doc_0123456789abcdef/manifest.json",
            content_hash="a" * 64,
        )

    monkeypatch.setattr("sales_curator.cli.import_document", fake_import)
    output = StringIO()
    code = cli(
        [
            "document",
            "import",
            "--source",
            str(source),
            "--inbox",
            str(inbox),
            "--output",
            str(output_root),
            "--title",
            "Libro autorizado",
            "--author",
            "Escuela local",
            "--language",
            "es",
            "--rights",
            str(rights_path),
            "--topic",
            "ventas",
        ],
        output=output,
    )

    assert code == 0
    assert seen["path"] == source
    assert seen["allowed_root"] == inbox
    assert seen["output_root"] == output_root
    assert seen["topics"] == ("ventas",)
    assert seen["rights"].jurisdiction == "MX"
    assert "document_id=doc_0123456789abcdef" in output.getvalue()
    assert f"manifest={output_root / 'doc_0123456789abcdef/manifest.json'}" in output.getvalue()


def test_cli_book_research_requires_and_propagates_explicit_network_authorization(
    monkeypatch, settings: Settings, tmp_path: Path
) -> None:
    configured = settings.model_copy(
        update={
            "network_enabled": True,
            "runtime_network": True,
            "allow_real_connectors": True,
            "allowed_domains": "openlibrary.org,www.googleapis.com",
            "max_urls_per_run": 3,
        }
    )
    monkeypatch.setattr("sales_curator.cli._settings", lambda: configured)
    seen: dict[str, object] = {}

    class FakeHttpClient:
        def __init__(self, policy) -> None:
            seen["policy"] = policy

        def __enter__(self):
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    class FakeResearcher:
        def __init__(self, http) -> None:
            seen["http"] = http

        def research(self, **kwargs):
            seen["research"] = kwargs
            return BookResearchReport.create(
                query="SPIN Selling — Neil Rackham",
                jurisdiction="MX",
                languages=["en", "es"],
                offers=[],
                warnings=["fixture sin red"],
            )

    monkeypatch.setattr("sales_curator.cli.SafeHttpClient", FakeHttpClient)
    monkeypatch.setattr("sales_curator.cli.BookResearcher", FakeResearcher)
    output_root = tmp_path / "book-research"
    output = StringIO()
    code = cli(
        [
            "book",
            "research",
            "--title",
            "SPIN Selling",
            "--author",
            "Neil Rackham",
            "--jurisdiction",
            "MX",
            "--language",
            "en",
            "--language",
            "es",
            "--provider",
            "open_library",
            "--url-budget",
            "3",
            "--authorize-network",
            "--output",
            str(output_root),
        ],
        output=output,
    )

    assert code == 0
    assert seen["policy"].run_authorized is True
    assert seen["policy"].url_budget == 3
    assert seen["research"] == {
        "title": "SPIN Selling",
        "author": "Neil Rackham",
        "isbn": None,
        "jurisdiction": "MX",
        "languages": ("en", "es"),
        "providers": ("open_library",),
        "max_results": 10,
    }
    report_path = next(output_root.glob("*/report.json"))
    assert f"report={report_path}" in output.getvalue()


def test_cli_web_capture_uses_rights_and_authorized_policy(
    monkeypatch, settings: Settings, tmp_path: Path
) -> None:
    configured = settings.model_copy(
        update={
            "network_enabled": True,
            "runtime_network": True,
            "allow_real_connectors": True,
            "allowed_domains": "openlibrary.org",
            "max_urls_per_run": 3,
        }
    )
    monkeypatch.setattr("sales_curator.cli._settings", lambda: configured)
    rights_path = _rights_file(tmp_path / "rights.json")
    output_root = tmp_path / "web"
    seen: dict[str, object] = {}

    def fake_capture(url: str, **kwargs):
        seen.update({"url": url, **kwargs})
        return SimpleNamespace(
            capture_id="web_0123456789abcdef",
            manifest_path="web_0123456789abcdef/manifest.json",
            content_hash="b" * 64,
        )

    monkeypatch.setattr("sales_curator.cli.capture_web_page", fake_capture)
    output = StringIO()
    code = cli(
        [
            "web",
            "capture",
            "--url",
            "https://openlibrary.org/works/OL1W",
            "--language",
            "es",
            "--rights",
            str(rights_path),
            "--url-budget",
            "3",
            "--authorize-network",
            "--output",
            str(output_root),
        ],
        output=output,
    )

    assert code == 0
    assert seen["policy"].run_authorized is True
    assert seen["rights"].rights_status == RightsStatus.EXPLICIT_PERMISSION
    assert seen["language"] == "es"
    assert callable(seen["resolver"])
    assert f"manifest={output_root / 'web_0123456789abcdef/manifest.json'}" in output.getvalue()


def test_cli_exports_manual_notebooklm_and_portable_rag_packets(tmp_path: Path) -> None:
    report = BookResearchReport.create(
        query="Educational sales books",
        jurisdiction="MX",
        languages=["en", "es"],
        offers=[],
        warnings=[],
    )
    report_path = tmp_path / "report.json"
    report_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    notebook_output = tmp_path / "notebooklm"
    rag_output = tmp_path / "rag"

    notebook_text = StringIO()
    assert (
        cli(
            [
                "notebooklm",
                "export",
                "--report",
                str(report_path),
                "--output",
                str(notebook_output),
                "--max-sources",
                "25",
            ],
            output=notebook_text,
        )
        == 0
    )
    assert "mode=manual_notebooklm_import" in notebook_text.getvalue()
    assert (notebook_output / "manifest.json").is_file()

    rag_text = StringIO()
    assert (
        cli(
            ["rag", "export", "--report", str(report_path), "--output", str(rag_output)],
            output=rag_text,
        )
        == 0
    )
    assert "records=0" in rag_text.getvalue()
    assert (rag_output / "manifest.json").is_file()


def test_cli_doctor_is_sanitized_and_reports_optional_dependencies(
    monkeypatch, settings: Settings
) -> None:
    configured = settings.model_copy(
        update={
            "allowed_domains": "secret-school.example,openlibrary.org",
            "curator_model": "qwen3.5:4b",
        }
    )
    monkeypatch.setattr("sales_curator.cli._settings", lambda: configured)
    monkeypatch.setattr(
        "sales_curator.cli._package_status",
        lambda package: {"installed": package == "markitdown", "version": "test"},
    )
    output = StringIO()

    assert cli(["doctor"], output=output) == 0
    payload = json.loads(output.getvalue())
    assert payload["dependencies"]["markitdown"]["installed"] is True
    assert payload["dependencies"]["crawl4ai"]["installed"] is False
    assert payload["network"]["allowlist_count"] == 2
    assert payload["ollama"]["model_configured"] is True
    assert "secret-school.example" not in output.getvalue()
