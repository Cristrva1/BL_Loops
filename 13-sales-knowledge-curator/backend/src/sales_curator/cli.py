"""CLI didáctica del curador. La aprobación humana exige hash explícito."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import TextIO

from sales_curator.config import Settings, lab_root
from sales_curator.evaluation.gate import claim_identity_hash
from sales_curator.evaluation.jsonl import validate_run
from sales_curator.orchestration.service import CuratorService


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sales-curator")
    commands = parser.add_subparsers(dest="command", required=True)

    audit = commands.add_parser("audit", help="Auditar un directorio local de fuentes.")
    audit.add_argument("--source", required=True, type=Path)
    audit.add_argument("--as-of", default="2026-08-30")
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

    build = commands.add_parser("release", help="Construir o validar un release.")
    build.add_argument("action", choices=["build", "validate", "rollback"])
    build.add_argument("--candidate")
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
    return parser


def _service() -> CuratorService:
    return CuratorService(Settings())


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
    if snapshot.candidate_hash:
        print(f"candidate_hash={snapshot.candidate_hash}", file=output)
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
        service = _service()
        root = lab_root()
        if args.command == "audit":
            source = args.source if args.source.is_absolute() else root / args.source
            snapshot = service.start_audit(
                source,
                as_of=date.fromisoformat(args.as_of),
                dry_run=args.dry_run,
            )
            _print_snapshot(snapshot, output)
            return 0
        if args.command in {"plan", "research"}:
            if args.command == "research":
                fixture = args.fixture if args.fixture.is_absolute() else root / args.fixture
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
            items = service.list_claims(args.run, args.status)
            for claim in items:
                print(
                    f"{claim.claim_id}\t{claim.status.value}\t{claim_identity_hash(claim)}\t{claim.canonical_text}",
                    file=output,
                )
            return 0
        if args.command == "review":
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
            if args.action == "build":
                if not args.run or not args.reviewer or not args.reason:
                    print("release build requiere --run --reviewer --reason", file=error_output)
                    return 2
                snapshot = service.build_release(
                    args.run, reviewer=args.reviewer, reason=args.reason
                )
                _print_snapshot(snapshot, output)
                return 0
            if args.action == "validate":
                report = service.validate_release(args.release or args.candidate)
                print(json.dumps(report, ensure_ascii=False, indent=2), file=output)
                return 0 if report.get("valid") else 1
            if args.action == "rollback":
                service.rollback_release(args.release)
                print(f"rollback={args.release}", file=output)
                return 0
        if args.command == "validate":
            report = service.validate_release(args.release)
            print(json.dumps(report, ensure_ascii=False, indent=2), file=output)
            return 0 if report.get("valid") else 1
        if args.command == "export-run":
            path = service.export_run(args.run)
            summary = validate_run(path)
            print(json.dumps(summary, ensure_ascii=False, indent=2), file=output)
            return 0
        if args.command == "demo":
            fixture = args.fixture if args.fixture.is_absolute() else root / args.fixture
            snapshot = service.demo(fixture, args.reviewer, args.reason)
            exported = service.export_run(snapshot.workflow.run_id)
            _print_snapshot(snapshot, output)
            print(f"exported={exported.as_posix()}", file=output)
            return 0
    except Exception as exc:
        print(f"error: {exc}", file=error_output)
        return 1
    return 1


def main() -> None:
    raise SystemExit(cli())


if __name__ == "__main__":
    main()
