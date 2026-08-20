"""CLI gate: ``python -m etl build|approve|release`` (R1-R3, D6).

Commands
--------
build
    Run the full ETL pipeline over both source Excels and render
    ``dashboard.html`` (vendored libraries inlined, offline-safe).
    BLOCKS on a join match rate < 90% (E2 edge): no output is written, a
    ``FAILED`` audit row with the match rate is appended, an alert is printed
    to stderr, and the process exits non-zero.

approve --approver NAME
    Record a human approval bound to the SHA-256 hex digest of the current
    ``dashboard.html`` plus its ``run_id`` (R2). Blocks if the artifact does
    not match the digest recorded at build time.

release --dest DIR
    Copy ``dashboard.html`` to *DIR* ONLY when the current digest matches the
    approval digest AND the approval belongs to the latest build run (R1, R3).

Exit codes
----------
0  success
1  gate block (approve/release precondition failed, missing artifact)
2  build failure (E1/E2/E3/E4 - data validation or join breach)
"""

from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import shutil
import sys
from datetime import datetime
from typing import Any

from etl import aggregate, audit, ingest, render, sanitize, validate

DASHBOARD = render.DASHBOARD_OUT
DATA_LOG = audit.DATA_LOG

EXIT_OK = 0
EXIT_GATE_BLOCK = 1
EXIT_BUILD_FAIL = 2


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _run_id() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def sha256_file(path: str | pathlib.Path) -> str:
    """SHA-256 hex digest of a file (R2 fingerprint)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _meta(run_id: str, match_rate: float, source_files: list[str]) -> dict:
    return {
        "period": aggregate.PERIOD,
        "run_id": run_id,
        "generated_at": _now_iso(),
        "match_rate": match_rate,
        "source_files": source_files,
    }


def cmd_build(args: argparse.Namespace) -> int:
    """Full ETL pipeline -> dashboard.html + audit row (E1-E7)."""
    run = _run_id()
    try:
        usuarios = ingest.load_usuarios(args.usuarios)
        ventas = ingest.load_ventas(args.ventas)

        # E3: numeric columns finite, no NaN, no text.
        validate.validate_numerics(usuarios, validate.USUARIOS_NUMERIC, "Usuarios")
        validate.validate_numerics(ventas, validate.VENTAS_NUMERIC, "Ventas")

        # E4: ISO dates -> datetime before month aggregation.
        validate.parse_dates(usuarios, validate.USUARIOS_DATES)
        validate.parse_dates(ventas, validate.VENTAS_DATES)

        # E2: inner join on ID Transacción + match-rate gate (fail-stop < 90%).
        joined, match_rate = validate.inner_join(usuarios, ventas)
        validate.check_match_rate(match_rate)

        # E5: sanitize string fields before JSON embedding.
        joined, sanitize_report = sanitize.sanitize_frame(joined)

        # E6: aggregates + meta.
        payload = aggregate.build_payload(
            joined, _meta(run, match_rate, [args.usuarios, args.ventas])
        )

        # D1/D2-D5: render single-file dashboard (vendored libs inlined).
        render.render_dashboard(payload, out_path=DASHBOARD)

        digest = sha256_file(DASHBOARD)
        audit.log_event(
            DATA_LOG,
            run_id=run,
            event="build",
            rows_usuarios=len(usuarios),
            rows_ventas=len(ventas),
            joined_rows=len(joined),
            match_rate=match_rate,
            validation_status="OK",
            sanitization_status=str(sanitize_report["cells_modified"]),
            outputs=f"{DASHBOARD},{render.PAYLOAD_OUT}",
            status="OK",
            artifact_sha256=digest,
        )

        print(f"[OK] build {run}: {len(joined)} transacciones, match_rate={match_rate:.2%}")
        print(f"     {DASHBOARD} ({digest[:12]}...) · {render.PAYLOAD_OUT} · auditado en {DATA_LOG}")
        return EXIT_OK

    except (ingest.IngestError, validate.ValidationError, validate.JoinBreachError) as exc:
        _log_failed_build(run, exc)
        print(f"[BLOQUEADO] {exc}", file=sys.stderr)
        print("No se generó dashboard.html. Corrija los datos y vuelva a ejecutar build.", file=sys.stderr)
        return EXIT_BUILD_FAIL


def _log_failed_build(run: str, exc: Exception) -> None:
    """Append the FAILED audit row for a blocked build (E2 edge / E3, E7)."""
    match_rate: float | None = None
    if isinstance(exc, validate.JoinBreachError):
        match_rate = _extract_match_rate(str(exc))
    audit.log_event(
        DATA_LOG,
        run_id=run,
        event="build",
        match_rate=match_rate,
        validation_status=str(exc),
        outputs="",
        status="FAILED",
    )


def _extract_match_rate(message: str) -> float | None:
    for token in message.split():
        if token.startswith("match_rate="):
            try:
                return float(token.split("=")[1])
            except (IndexError, ValueError):
                return None
    return None


def _require_dashboard() -> tuple[str, int | None]:
    """Return (digest, None) when dashboard.html exists, else (msg, exit code)."""
    if not os.path.isfile(DASHBOARD):
        return f"No existe {DASHBOARD}: ejecute primero 'python -m etl build'.", EXIT_GATE_BLOCK
    return sha256_file(DASHBOARD), None


def cmd_approve(args: argparse.Namespace) -> int:
    """Record human approval bound to digest + run_id (R2)."""
    digest, err = _require_dashboard()
    if err is not None:
        print(f"[BLOQUEADO] {digest}", file=sys.stderr)
        return err

    latest_build = audit.read_latest_event(DATA_LOG, event="build", status="OK")
    if latest_build is None:
        print(f"[BLOQUEADO] No hay build exitoso registrado en {DATA_LOG}.", file=sys.stderr)
        return EXIT_GATE_BLOCK

    if digest != latest_build["artifact_sha256"]:
        print(
            f"[BLOQUEADO] {DASHBOARD} cambió desde el build: sha256={digest[:12]}... "
            f"!= registrado {latest_build['artifact_sha256'][:12]}.... Re-ejecute build.",
            file=sys.stderr,
        )
        return EXIT_GATE_BLOCK

    approver = (args.approver or "").strip()
    if not approver:
        print("[BLOQUEADO] --approver no puede estar vacío.", file=sys.stderr)
        return EXIT_GATE_BLOCK

    approval_ts = _now_iso()
    audit.log_event(
        DATA_LOG,
        run_id=latest_build["run_id"],
        event="approve",
        rows_usuarios=latest_build.get("rows_usuarios") or None,
        rows_ventas=latest_build.get("rows_ventas") or None,
        joined_rows=latest_build.get("joined_rows") or None,
        match_rate=float(latest_build["match_rate"]) if latest_build.get("match_rate") else None,
        outputs=DASHBOARD,
        status="OK",
        approver=approver,
        approval_ts=approval_ts,
        artifact_sha256=digest,
    )
    print(f"[OK] Aprobación registrada: run_id={latest_build['run_id']}, "
          f"approver={approver}, sha256={digest[:12]}...")
    return EXIT_OK


def cmd_release(args: argparse.Namespace) -> int:
    """Copy dashboard.html to --dest only under approval gate (R1, R3, D6)."""
    digest, err = _require_dashboard()
    if err is not None:
        print(f"[BLOQUEADO] {digest}", file=sys.stderr)
        return err

    latest_build = audit.read_latest_event(DATA_LOG, event="build", status="OK")
    latest_approval = audit.read_latest_event(DATA_LOG, event="approve", status="OK")

    # R1: no approval -> blocked.
    if latest_approval is None:
        print(
            f"[BLOQUEADO] No hay aprobación registrada (R1). "
            f"Ejecute 'python -m etl approve --approver <nombre>'.",
            file=sys.stderr,
        )
        return EXIT_GATE_BLOCK

    # R3: approval from an older ETL run must not apply.
    if latest_build is None or latest_approval["run_id"] != latest_build["run_id"]:
        print(
            f"[BLOQUEADO] La aprobación pertenece al run {latest_approval.get('run_id', '?')} "
            f"y el build actual es {latest_build.get('run_id', '?')} (R3): "
            f"se requiere una aprobación fresca.",
            file=sys.stderr,
        )
        return EXIT_GATE_BLOCK

    # R1/R2 binding: artifact must be byte-identical to the approved one.
    if digest != latest_approval["artifact_sha256"]:
        print(
            f"[BLOQUEADO] {DASHBOARD} difiere del artefacto aprobado "
            f"({digest[:12]}... != {latest_approval['artifact_sha256'][:12]}...).",
            file=sys.stderr,
        )
        return EXIT_GATE_BLOCK

    dest = pathlib.Path(args.dest)
    try:
        dest.mkdir(parents=True, exist_ok=True)
        target = dest / DASHBOARD
        shutil.copy2(DASHBOARD, target)
    except OSError as exc:
        print(f"[ERROR] No se pudo copiar a {dest}: {exc}", file=sys.stderr)
        return EXIT_GATE_BLOCK

    audit.log_event(
        DATA_LOG,
        run_id=latest_build["run_id"],
        event="release",
        joined_rows=latest_build.get("joined_rows") or None,
        match_rate=float(latest_build["match_rate"]) if latest_build.get("match_rate") else None,
        outputs=f"{DASHBOARD}->{target}",
        status="OK",
        approver=latest_approval["approver"],
        approval_ts=latest_approval["approval_ts"],
        artifact_sha256=digest,
    )
    print(f"[OK] Publicado localmente: {target} (run_id={latest_build['run_id']}, "
          f"sha256={digest[:12]}...)")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m etl",
        description="Dashboard de Ventas 2026 - ETL, aprobación y release local (Ene-May 2026).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build", help="ETL completo -> dashboard.html (E1-E7)")
    b.add_argument("--usuarios", default=ingest.USUARIOS_FILE, help="Excel de usuarios/clientes")
    b.add_argument("--ventas", default=ingest.VENTAS_FILE, help="Excel de ventas/productos")

    a = sub.add_parser("approve", help="Registrar aprobación humana (R2)")
    a.add_argument("--approver", required=True, help="Nombre del aprobador")

    r = sub.add_parser("release", help="Copiar dashboard aprobado a un destino local (R1/R3/D6)")
    r.add_argument("--dest", required=True, help="Directorio local de destino")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "build":
            return cmd_build(args)
        if args.command == "approve":
            return cmd_approve(args)
        if args.command == "release":
            return cmd_release(args)
    except Exception as exc:  # unexpected - surface and exit non-zero
        print(f"[ERROR] {exc}", file=sys.stderr)
        return EXIT_GATE_BLOCK
    return EXIT_GATE_BLOCK  # unreachable


if __name__ == "__main__":  # pragma: no cover - __main__.py is the real entrypoint
    sys.exit(main())