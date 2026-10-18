#!/usr/bin/env python3
"""
provenance_seal.py — sello de procedencia para una cifra que sale de un export.

La regla "toda cifra va con su fuente y su fecha" se vuelve mecánica: el sello
cita archivo, hora del export (no solo el día), sha256, filas leídas y
descartadas, período declarado por el propio archivo y la empresa/entidad bajo
la que se corrió. Un informe cierra con este bloque; quien lo lea puede
reproducir el número o descubrir que el archivo cambió.

Guardas que levantan error (exit 1) en vez de sellar un número dudoso:
  - entidad no declarada (--entity es obligatorio: no hay default "todas")
  - archivo sin filas de datos (un sello sobre cero filas es un verde vacío)
  - conteo de filas en el techo de .xls (65.536): export truncado sin aviso
  - período declarado en el preámbulo distinto del que pide --expect-period

Agnóstico y stdlib-only. Uso:
  python3 provenance_seal.py ventas.csv --entity "SAS" \
      --encoding cp1252 --delimiter ";" --skip-regex "TOTAL"
  python3 provenance_seal.py ventas.csv --entity "SAS" --json

Exit codes: 0 sello emitido, 1 guarda en rojo, 2 uso incorrecto.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Techo de filas de una hoja .xls (BIFF8). Un export con exactamente estas filas
# (o una menos, si el encabezado ocupa una) está truncado, no completo.
XLS_ROW_CEILING = 65_536

# "Entre 01/01/26 y 30/06/26", "Desde 2026-01-01 hasta 2026-06-30", etc.
PERIOD_PATTERN = re.compile(
    r"(?:entre|desde)\s+(\d{1,4}[/-]\d{1,2}[/-]\d{1,4})\s+(?:y|hasta|al?)\s+"
    r"(\d{1,4}[/-]\d{1,2}[/-]\d{1,4})",
    re.IGNORECASE,
)
PREAMBLE_LINES = 10


class SealError(Exception):
    """Una guarda en rojo: el sello no se emite."""


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def declared_period(lines: list[str]) -> str | None:
    """El período lo dice el preámbulo del archivo, nunca su nombre."""
    for line in lines[:PREAMBLE_LINES]:
        m = PERIOD_PATTERN.search(line)
        if m:
            return f"{m.group(1)} – {m.group(2)}"
    return None


def seal(
    path: Path,
    entity: str,
    *,
    encoding: str = "utf-8",
    delimiter: str = ",",
    header_rows: int = 1,
    skip_regex: str | None = None,
    expect_period: str | None = None,
) -> dict:
    if not entity or not entity.strip():
        raise SealError("entidad no declarada: una cifra sin empresa mezcla universos")
    if not path.is_file():
        raise SealError(f"no existe el archivo: {path}")

    text = path.read_bytes().decode(encoding)
    lines = text.splitlines()
    period = declared_period(lines)
    if expect_period is not None and period != expect_period:
        raise SealError(
            f"período declarado {period!r} != esperado {expect_period!r}: "
            "cruzar dos informes de distinto período no es un hallazgo"
        )

    rows = list(csv.reader(lines, delimiter=delimiter))
    body = rows[header_rows:]
    skip = re.compile(skip_regex, re.IGNORECASE) if skip_regex else None
    read, discarded = 0, 0
    for row in body:
        if not any(cell.strip() for cell in row):
            discarded += 1
        elif skip and any(skip.search(cell) for cell in row):
            discarded += 1
        else:
            read += 1

    if read == 0:
        raise SealError(
            f"cero filas de datos ({discarded} descartadas de {len(body)}): "
            "un sello sobre nada es un verde vacío"
        )
    if len(rows) in (XLS_ROW_CEILING, XLS_ROW_CEILING - 1):
        raise SealError(
            f"{len(rows)} filas = techo de .xls: el export está truncado; "
            "pedirlo en .csv o .xlsx"
        )

    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return {
        "archivo": path.name,
        "entidad": entity.strip(),
        "periodo_declarado": period,
        "export_mtime_utc": mtime.isoformat(timespec="seconds"),
        "sha256": sha256_of(path),
        "filas_leidas": read,
        "filas_descartadas": discarded,
    }


def as_markdown(s: dict) -> str:
    period = s["periodo_declarado"] or "NO DECLARADO en el preámbulo — decirlo en el informe"
    return (
        "> **Procedencia** — "
        f"`{s['archivo']}` · entidad **{s['entidad']}** · período {period} · "
        f"export {s['export_mtime_utc']} · sha256 `{s['sha256'][:12]}` · "
        f"{s['filas_leidas']} filas leídas, {s['filas_descartadas']} descartadas"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("file", type=Path)
    ap.add_argument("--entity", required=True, help="empresa/razón social bajo la que se corrió")
    ap.add_argument("--encoding", default="utf-8", help="declarada, nunca adivinada (ej. cp1252)")
    ap.add_argument("--delimiter", default=",")
    ap.add_argument("--header-rows", type=int, default=1)
    ap.add_argument("--skip-regex", help="filas de subtotal/total a descartar (ej. 'TOTAL')")
    ap.add_argument("--expect-period", help="falla si el preámbulo declara otro período")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        s = seal(
            args.file,
            args.entity,
            encoding=args.encoding,
            delimiter=args.delimiter,
            header_rows=args.header_rows,
            skip_regex=args.skip_regex,
            expect_period=args.expect_period,
        )
    except (SealError, UnicodeDecodeError) as exc:
        print(f"SELLO-ROJO: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(s, ensure_ascii=False, indent=2) if args.json else as_markdown(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
