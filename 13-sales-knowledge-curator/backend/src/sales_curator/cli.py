"""CLI didáctica del curador. La aprobación humana exige hash explícito."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import date
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import TextIO

from sales_curator.config import Settings, configuration_scope, find_env_file, lab_root
from sales_curator.connectors.documents import import_document
from sales_curator.connectors.network import SafeHttpClient, system_resolver
from sales_curator.connectors.web_crawler import capture_web_page
from sales_curator.contracts.research import BookResearchReport, DocumentRights
from sales_curator.evaluation.gate import claim_identity_hash
from sales_curator.evaluation.jsonl import validate_run
from sales_curator.orchestration.service import AuditRunFailed, CuratorService
from sales_curator.research.books import BookResearcher, write_book_research_report
from sales_curator.research.packages import build_notebooklm_packet, build_rag_packet

PACKAGE_NAME = "bl-loops-sales-knowledge-curator"


def _application_version() -> str:
    return version(PACKAGE_NAME)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sales-curator")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_application_version()}",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    audit = commands.add_parser("audit", help="Auditar un directorio local de fuentes.")
    audit.add_argument("--source", required=True, type=Path)
    audit.add_argument("--as-of", default="2026-08-30")
    audit.add_argument("--domain")
    audit.add_argument(
        "--extractor",
        choices=["deterministic", "ollama"],
        default="deterministic",
    )
    audit.add_argument("--dry-run", action="store_true")

    commands.add_parser("plan", help="Mostrar huecos y tareas de la última corrida.")
    plan = commands.add_parser(
        "research", help="Alias de auditoría local; la red permanece apagada."
    )
    plan.add_argument("--fixture", required=True, type=Path)

    claims = commands.add_parser("claims", help="Listar afirmaciones.")
    claims.add_argument("action", choices=["list"])
    claims.add_argument("--status")
    claims.add_argument("--run", required=True)

    review = commands.add_parser(
        "review", help="Registrar una decisión humana sobre un hash exacto."
    )
    review.add_argument("--candidate", required=True)
    review.add_argument("--run", required=True)
    review.add_argument("--object-type", default="claim", choices=["claim", "release_candidate"])
    review.add_argument(
        "--decision", required=True, choices=["approved", "rejected", "changes_requested"]
    )
    review.add_argument("--reviewer", required=True)
    review.add_argument("--reason", required=True)
    review.add_argument("--expected-hash", required=True)

    build = commands.add_parser("release", help="Construir, publicar o validar un release.")
    build.add_argument("action", choices=["build", "publish", "validate", "rollback"])
    build.add_argument("--candidate")
    build.add_argument("--expected-hash")
    build.add_argument("--release")
    build.add_argument("--run")
    build.add_argument("--reviewer")
    build.add_argument("--reason")

    validate = commands.add_parser("validate", help="Validar un release publicado.")
    validate.add_argument("--release", required=True)

    export = commands.add_parser("export-run", help="Exportar JSONL sanitizado.")
    export.add_argument("--run", required=True)

    demo = commands.add_parser(
        "demo", help="Recorrido vertical con fixtures y revisión del operador."
    )
    demo.add_argument("--fixture", type=Path, default=Path("fixtures/corpus"))
    demo.add_argument("--reviewer", default="operador-local")
    demo.add_argument("--reason", default="Aprobacion didactica del operador sobre el hash actual")

    document = commands.add_parser("document", help="Importar documentos locales autorizados.")
    document_actions = document.add_subparsers(dest="document_action", required=True)
    document_import = document_actions.add_parser("import", help="Convertir PDF/DOCX a Markdown.")
    document_import.add_argument("--source", required=True, type=Path)
    document_import.add_argument("--inbox", required=True, type=Path)
    document_import.add_argument("--output", required=True, type=Path)
    document_import.add_argument("--title", required=True)
    document_import.add_argument("--author", required=True)
    document_import.add_argument("--language", required=True, choices=["en", "es"])
    document_import.add_argument("--rights", required=True, type=Path)
    document_import.add_argument("--topic", action="append", default=[])

    book = commands.add_parser("book", help="Investigar acceso bibliográfico multifuente.")
    book_actions = book.add_subparsers(dest="book_action", required=True)
    book_research = book_actions.add_parser("research", help="Consultar catálogos permitidos.")
    book_research.add_argument("--title", required=True)
    book_research.add_argument("--author")
    book_research.add_argument("--isbn")
    book_research.add_argument("--jurisdiction", required=True)
    book_research.add_argument("--language", action="append", choices=["en", "es"], default=[])
    book_research.add_argument(
        "--provider",
        action="append",
        choices=["open_library", "google_books"],
        default=[],
    )
    book_research.add_argument("--max-results", type=int, default=10)
    book_research.add_argument("--url-budget", required=True, type=int)
    book_research.add_argument("--authorize-network", required=True, action="store_true")
    book_research.add_argument("--output", required=True, type=Path)

    web = commands.add_parser(
        "web",
        help="Capturar una página permitida con navegador.",
        epilog="Crawl4AI by UncleCode - https://github.com/unclecode/crawl4ai",
    )
    web_actions = web.add_subparsers(dest="web_action", required=True)
    web_capture = web_actions.add_parser(
        "capture",
        help="Comprobar robots y guardar Markdown.",
        epilog="Crawl4AI by UncleCode - https://github.com/unclecode/crawl4ai",
    )
    web_capture.add_argument("--url", required=True)
    web_capture.add_argument("--language", required=True, choices=["en", "es"])
    web_capture.add_argument("--rights", required=True, type=Path)
    web_capture.add_argument("--url-budget", required=True, type=int)
    web_capture.add_argument("--authorize-network", required=True, action="store_true")
    web_capture.add_argument("--output", required=True, type=Path)

    notebooklm = commands.add_parser(
        "notebooklm", help="Preparar un paquete manual para NotebookLM."
    )
    notebooklm_actions = notebooklm.add_subparsers(dest="notebooklm_action", required=True)
    notebooklm_export = notebooklm_actions.add_parser(
        "export", help="Exportar fichas; nunca realiza una carga."
    )
    notebooklm_export.add_argument("--report", required=True, type=Path)
    notebooklm_export.add_argument("--output", required=True, type=Path)
    notebooklm_export.add_argument("--max-sources", type=int, default=50)

    rag = commands.add_parser("rag", help="Preparar metadatos RAG portables.")
    rag_actions = rag.add_subparsers(dest="rag_action", required=True)
    rag_export = rag_actions.add_parser("export", help="Exportar JSONL sin dependencia viva.")
    rag_export.add_argument("--report", required=True, type=Path)
    rag_export.add_argument("--output", required=True, type=Path)

    commands.add_parser("doctor", help="Mostrar preflight sanitizado de dependencias y gates.")
    return parser


def _settings() -> Settings:
    return Settings()


def _service() -> CuratorService:
    return CuratorService(_settings())


def _resolve_path(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _load_rights(root: Path, path: Path) -> DocumentRights:
    resolved = _resolve_path(root, path)
    return DocumentRights.model_validate_json(resolved.read_text(encoding="utf-8"))


def _load_book_report(root: Path, path: Path) -> BookResearchReport:
    resolved = _resolve_path(root, path)
    return BookResearchReport.model_validate_json(resolved.read_text(encoding="utf-8"))


def _package_status(package: str) -> dict[str, object]:
    try:
        installed_version = version(package)
    except PackageNotFoundError:
        return {"installed": False, "version": None}
    return {"installed": True, "version": installed_version}


def _doctor(settings: Settings) -> dict[str, object]:
    network_gates = {
        "configured": settings.network_enabled,
        "runtime_authorized": settings.runtime_network,
        "real_connectors_enabled": settings.allow_real_connectors,
        "allowlist_count": len(settings.allowed_domain_list),
    }
    return {
        "configuration_scope": configuration_scope(find_env_file()),
        "dependencies": {
            "markitdown": _package_status("markitdown"),
            "crawl4ai": _package_status("crawl4ai"),
        },
        "network": network_gates,
        "ollama": {
            "local_only": True,
            "model_configured": bool(settings.curator_model.strip()),
        },
        "safety": {
            "external_writes": False,
            "remote_telemetry": False,
        },
    }


def _print_snapshot(snapshot, output: TextIO) -> None:
    print(f"run_id={snapshot.workflow.run_id}", file=output)
    print(f"state={snapshot.workflow.state.value}", file=output)
    print(f"sources={len(snapshot.sources)} claims={len(snapshot.claims)}", file=output)
    print(
        f"conflicts={len(snapshot.conflicts)} gaps={len(snapshot.gaps)}",
        file=output,
    )
    if snapshot.release_id:
        print(f"release={snapshot.release_id}", file=output)
    if snapshot.candidate_id:
        print(f"candidate_id={snapshot.candidate_id}", file=output)
    if snapshot.candidate_hash:
        print(f"candidate_hash={snapshot.candidate_hash}", file=output)
    if snapshot.candidate_diff is not None:
        sanitized_diff = json.dumps(
            snapshot.candidate_diff,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        print(f"candidate_diff={sanitized_diff}", file=output)
    if snapshot.jsonl_path:
        print(f"jsonl={snapshot.jsonl_path}", file=output)


def cli(
    argv: Sequence[str] | None = None,
    *,
    output: TextIO = sys.stdout,
    error_output: TextIO = sys.stderr,
) -> int:
    args = _parser().parse_args(argv)
    try:
        root = lab_root()
        if args.command == "document":
            settings = _settings()
            inbox = _resolve_path(root, args.inbox)
            source = (
                args.source.resolve()
                if args.source.is_absolute()
                else (inbox / args.source).resolve()
            )
            output_root = _resolve_path(root, args.output)
            rights = _load_rights(root, args.rights)
            record = import_document(
                source,
                allowed_root=inbox,
                output_root=output_root,
                title=args.title,
                author=args.author,
                language=args.language,
                rights=rights,
                topics=tuple(args.topic),
                max_bytes=settings.max_bytes_per_source,
            )
            print(f"document_id={record.document_id}", file=output)
            print(f"manifest={output_root / record.manifest_path}", file=output)
            print(f"content_hash={record.content_hash}", file=output)
            return 0
        if args.command == "book":
            settings = _settings()
            policy = settings.network_policy().authorize(
                run_authorized=args.authorize_network,
                url_budget=args.url_budget,
            )
            languages = tuple(args.language or settings.research_language_list)
            providers = tuple(args.provider or ("open_library", "google_books"))
            with SafeHttpClient(policy) as http:
                report = BookResearcher(http).research(
                    title=args.title,
                    author=args.author,
                    isbn=args.isbn,
                    jurisdiction=args.jurisdiction,
                    languages=languages,
                    providers=providers,
                    max_results=args.max_results,
                )
            report_path = write_book_research_report(
                report,
                _resolve_path(root, args.output),
            )
            print(f"research_id={report.research_id}", file=output)
            print(f"offers={len(report.offers)} warnings={len(report.warnings)}", file=output)
            print(f"report={report_path}", file=output)
            return 0
        if args.command == "web":
            if args.url_budget < 2:
                raise ValueError("web capture requiere --url-budget de al menos 2")
            settings = _settings()
            policy = settings.network_policy().authorize(
                run_authorized=args.authorize_network,
                url_budget=args.url_budget,
            )
            output_root = _resolve_path(root, args.output)
            record = capture_web_page(
                args.url,
                policy=policy,
                output_root=output_root,
                rights=_load_rights(root, args.rights),
                language=args.language,
                resolver=system_resolver,
            )
            print(f"capture_id={record.capture_id}", file=output)
            print(f"manifest={output_root / record.manifest_path}", file=output)
            print(f"content_hash={record.content_hash}", file=output)
            return 0
        if args.command == "notebooklm":
            report = _load_book_report(root, args.report)
            output_root = _resolve_path(root, args.output)
            packet = build_notebooklm_packet(
                report,
                output_root,
                max_sources=args.max_sources,
            )
            print(f"packet_id={packet.packet_id}", file=output)
            print(f"mode={packet.mode}", file=output)
            print(f"manifest={output_root / packet.manifest_path}", file=output)
            return 0
        if args.command == "rag":
            report = _load_book_report(root, args.report)
            output_root = _resolve_path(root, args.output)
            packet = build_rag_packet(report, output_root)
            print(f"packet_id={packet.packet_id}", file=output)
            print(f"records={packet.record_count}", file=output)
            print(f"manifest={output_root / packet.manifest_path}", file=output)
            return 0
        if args.command == "doctor":
            print(json.dumps(_doctor(_settings()), ensure_ascii=False, indent=2), file=output)
            return 0
        if args.command == "audit":
            service = _service()
            source = _resolve_path(root, args.source)
            snapshot = service.start_audit(
                source,
                as_of=date.fromisoformat(args.as_of),
                domain=args.domain or service.settings.research_domain,
                dry_run=args.dry_run,
                extractor=args.extractor,
            )
            _print_snapshot(snapshot, output)
            return 0
        if args.command in {"plan", "research"}:
            service = _service()
            if args.command == "research":
                fixture = _resolve_path(root, args.fixture)
                snapshot = service.start_audit(fixture)
                _print_snapshot(snapshot, output)
                return 0
            runs = service.store.list_runs()
            if not runs:
                print("No hay corridas.", file=error_output)
                return 1
            snapshot = service.get_run(runs[-1]["run_id"])
            print(
                json.dumps(
                    [gap.model_dump(mode="json") for gap in snapshot.gaps],
                    ensure_ascii=False,
                    indent=2,
                ),
                file=output,
            )
            return 0
        if args.command == "claims":
            service = _service()
            items = service.list_claims(args.run, args.status)
            for claim in items:
                print(
                    f"{claim.claim_id}\t{claim.status.value}\t{claim_identity_hash(claim)}\t{claim.canonical_text}",
                    file=output,
                )
            return 0
        if args.command == "review":
            service = _service()
            decision = service.submit_review(
                args.run,
                object_type=args.object_type,
                object_id=args.candidate,
                decision=args.decision,
                reviewer=args.reviewer,
                reason=args.reason,
                expected_hash=args.expected_hash,
            )
            print(f"decision={decision.decision_id} hash={decision.approved_hash}", file=output)
            return 0
        if args.command == "release":
            service = _service()
            if args.action == "build":
                if not args.run:
                    print("release build requiere --run", file=error_output)
                    return 2
                snapshot = service.build_release(args.run)
                _print_snapshot(snapshot, output)
                return 0
            if args.action == "publish":
                required = {
                    "--run": args.run,
                    "--candidate": args.candidate,
                    "--expected-hash": args.expected_hash,
                    "--reviewer": args.reviewer,
                    "--reason": args.reason,
                }
                missing = [name for name, value in required.items() if not value]
                if missing:
                    print(
                        f"release publish requiere {' '.join(missing)}",
                        file=error_output,
                    )
                    return 2
                decision = service.submit_review(
                    args.run,
                    object_type="release_candidate",
                    object_id=args.candidate,
                    decision="approved",
                    reviewer=args.reviewer,
                    reason=args.reason,
                    expected_hash=args.expected_hash,
                )
                snapshot = service.publish_release(args.run)
                print(
                    f"decision={decision.decision_id} hash={decision.approved_hash}",
                    file=output,
                )
                _print_snapshot(snapshot, output)
                return 0
            if args.action == "validate":
                release_id = args.release or args.candidate
                if not release_id:
                    print("release validate requiere --release", file=error_output)
                    return 2
                report = service.validate_release(release_id)
                print(json.dumps(report, ensure_ascii=False, indent=2), file=output)
                return 0 if report.get("valid") else 1
            if args.action == "rollback":
                if not args.release:
                    print("release rollback requiere --release", file=error_output)
                    return 2
                service.rollback_release(args.release)
                print(f"rollback={args.release}", file=output)
                return 0
        if args.command == "validate":
            service = _service()
            report = service.validate_release(args.release)
            print(json.dumps(report, ensure_ascii=False, indent=2), file=output)
            return 0 if report.get("valid") else 1
        if args.command == "export-run":
            service = _service()
            path = service.export_run(args.run)
            summary = validate_run(path)
            print(json.dumps(summary, ensure_ascii=False, indent=2), file=output)
            return 0
        if args.command == "demo":
            service = _service()
            fixture = _resolve_path(root, args.fixture)
            snapshot = service.demo(fixture, args.reviewer, args.reason)
            _print_snapshot(snapshot, output)
            return 0
    except AuditRunFailed as exc:
        print(f"error: {exc.reason}", file=error_output)
        print(f"run_id={exc.run_id}", file=error_output)
        print("state=failed", file=error_output)
        print(f"jsonl={exc.jsonl_path}", file=error_output)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=error_output)
        return 1
    return 1


def main() -> None:
    raise SystemExit(cli())


if __name__ == "__main__":
    main()
