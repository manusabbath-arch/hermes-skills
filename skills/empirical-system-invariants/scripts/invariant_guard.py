#!/usr/bin/env python3
"""
invariant_guard.py — guard de invariantes por contrato de datos (agnóstico de proyecto).

Cada ETAPA del pipeline declara un CONTRATO: qué campo promete poblar y qué condición
atestigua que lo hizo. Este guard recorre los checks, marca ROJO el eslabón fallido
y sale con exit code distinto de 0 si algo no se cumple. NUNCA traga excepción sin marcar
ROJO; NUNCA usa || true; paths anclados a __file__ o a env, nunca al cwd.

Uso:
  python invariant_guard.py --contract /path/to/contract.json
  python invariant_guard.py --contract /path/contract.json --db file.db   # checks que leen db
  echo $?  # 0 = todos verdes, 1 = >=1 ROJO, 2 = error de contratación/schema

Contrato (JSON):
{
  "contracts": [
    {
      "etapa": "sports_model",
      "consumidor": "rejected_signals",
      "campo": "edge_elo",
      "check": "not_null_ratio",
      "min_ratio": 0.5,            # fraccion de filas NO NULL que exige (0..1)
      "null_es_defecto": true,     # true: NULL=defecto; false: NULL legitimo (0 medido)
      "query": "SELECT COUNT(*) AS total, COUNT(edge_elo) AS poblado FROM rejected_signals",
      "nulo_es_0": false           # si el dato legitimo se guarda como NULL/0
    }
  ]
}

check soportado: "not_null_ratio" (ratio de filas con el campo no nulo >= min_ratio).
Extender con los checks que el proyecto necesite (book_vacio_ratio, staleness, etc).
"""

import argparse
import json
import os
import sqlite3
import sys


def _load_contract(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Contrato no encontrado: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _connect_db(db_path):
    if not db_path:
        return None
    if not os.path.isfile(db_path):
        # No lanzar aqui: el check de db lo marca ROJO con eslabon. Pero un path
        # inexistente NO debe dar verde — devolver sentinel que el caller trata como error.
        return None
    # Conexion NUEVA, nunca el pool: el pool ve su propia transaccion sin commit.
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _query_one(conn, query):
    """Lee con conexion nueva. Devuelve la primera fila como dict o None si la query falla."""
    cur = conn.execute(query)
    row = cur.fetchone()
    cur.close()
    if row is None:
        return None
    return dict(row)


def run_contract(contract, db_path=None):
    """Evalua una lista de contratos. Devuelve (exit_code, report_lines)."""
    report = []
    failures = 0
    errores = 0

    for c in contract.get("contracts", []):
        etapa = c.get("etapa", "?")
        campo = c.get("campo", "?")
        check = c.get("check", "")

        if check == "not_null_ratio":
            query = c.get("query")
            if not query:
                report.append(f"[ROJO] {etapa}/{campo}: check not_null_ratio sin query")
                failures += 1
                continue
            if not db_path or not _connect_db(db_path):
                report.append(f"[ROJO] {etapa}/{campo}: no hay DB para resolver la query")
                errores += 1
                continue
            conn = _connect_db(db_path)
            try:
                row = _query_one(conn, query)
            except Exception as e:  # noqa: BLE001 — un guard nunca traga un fallo de DB sin marcarlo
                report.append(f"[ROJO] {etapa}/{campo}: query fallo -> {e}")
                errores += 1
                continue
            finally:
                if conn:
                    conn.close()
            if row is None:
                report.append(f"[ROJO] {etapa}/{campo}: query no devolvio fila")
                errores += 1
                continue

            total = row.get("total")
            poblado = row.get("poblado")
            try:
                ratio = (poblado / total) if total else 0.0
            except (TypeError, ZeroDivisionError):
                ratio = 0.0

            min_ratio = float(c.get("min_ratio", 1.0))
            null_es_defecto = c.get("null_es_defecto", True)
            expected = f"ratio={ratio:.3f} (min {min_ratio:.3f})" if total else "sin filas post-deploy"

            if c.get("nulo_es_0", False):
                # El dato legitimo se guarda como NULL/0 — no contar como defecto.
                report.append(f"[OK] {etapa}/{campo}: nulo es 0 (dato legitimo), {expected}")
                continue

            if total == 0:
                report.append(f"[ROJO] {etapa}/{campo}: no hay filas post-deploy para medir ({expected})")
                errores += 1
                continue

            if ratio >= min_ratio:
                report.append(f"[OK] {etapa}/{campo}: poblado {poblado}/{total} ({expected})")
            else:
                if null_es_defecto:
                    report.append(
                        f"[ROJO] {etapa}/{campo}: poblado {poblado}/{total} ({expected}); "
                        f"NULL es defecto (campo nunca escrito)"
                    )
                    failures += 1
                else:
                    report.append(f"[OK] {etapa}/{campo}: NULL legitimo ({expected})")
        else:
            report.append(f"[ROJO] {etapa}/{campo}: check desconocido '{check}'")
            failures += 1

    # Sintesis
    if errores:
        exit_code = 2  # error de contratacion/schema, distinto del ROJO de negocio
        report.insert(0, f"INVARIANT-GUARD: {len(contract.get('contracts', []))} checks, "
                         f"{failures} ROJO(s), {errores} error(es) de esquema/datos")
    elif failures:
        exit_code = 1
        report.insert(0, f"INVARIANT-GUARD: {len(contract.get('contracts', []))} checks, "
                         f"{failures} ROJO(s) -> ciclo ROJO")
    else:
        exit_code = 0
        report.insert(0, f"INVARIANT-GUARD: {len(contract.get('contracts', []))} checks, todos verdes")

    return exit_code, report


def main():
    parser = argparse.ArgumentParser(description="Guard de invariantes por contrato de datos")
    parser.add_argument("--contract", required=True, help="Path al JSON de contrato (obligatorio)")
    parser.add_argument("--db", help="Path a la DB sqlite para checks que leen db")
    parser.add_argument("--print-report", action="store_true", default=True,
                        help="Imprimir el reporte (default: si)")
    args = parser.parse_args()

    try:
        contract = _load_contract(args.contract)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"INVARIANT-GUARD: contrato invalido -> {e}", file=sys.stderr)
        return 2

    exit_code, report = run_contract(contract, db_path=args.db)

    for line in report:
        print(line)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
