"""Hermetic tests for provenance_seal. Only tmp_path files, no network, no clock."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "provenance_seal.py"

spec = importlib.util.spec_from_file_location("provenance_seal", SCRIPT)
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)

EXPORT = (
    "Ventas por vendedor\n"
    "Entre 01/01/26 y 30/06/26\n"
    "vendedor;importe\n"
    "ANA;100,50\n"
    "JOSE;200,00\n"
    "TOTAL GENERAL;300,50\n"
    ";\n"
)


def _write(tmp_path, text, name="export.csv", encoding="utf-8"):
    p = tmp_path / name
    p.write_bytes(text.encode(encoding))
    return p


def _seal(path, **kw):
    kw.setdefault("delimiter", ";")
    kw.setdefault("header_rows", 3)
    return ps.seal(path, "SAS", **kw)


def test_counts_read_and_discarded_rows(tmp_path):
    s = _seal(_write(tmp_path, EXPORT), skip_regex="TOTAL")
    assert s["filas_leidas"] == 2
    assert s["filas_descartadas"] == 2  # TOTAL GENERAL + fila vacía
    assert s["entidad"] == "SAS"


def test_without_skip_regex_the_total_row_is_counted_as_data(tmp_path):
    # Gemelo del anterior: prueba que el descarte depende del regex, no del azar.
    s = _seal(_write(tmp_path, EXPORT))
    assert s["filas_leidas"] == 3


def test_period_comes_from_preamble_not_filename(tmp_path):
    s = _seal(_write(tmp_path, EXPORT, name="ventas 2026 YTD.csv"), skip_regex="TOTAL")
    assert s["periodo_declarado"] == "01/01/26 – 30/06/26"


def test_expect_period_mismatch_is_red(tmp_path):
    with pytest.raises(ps.SealError, match="período declarado"):
        _seal(_write(tmp_path, EXPORT), expect_period="01/01/26 – 01/07/26")


def test_expect_period_match_passes(tmp_path):
    s = _seal(_write(tmp_path, EXPORT), expect_period="01/01/26 – 30/06/26")
    assert s["filas_leidas"] == 3


def test_entity_is_mandatory(tmp_path):
    with pytest.raises(ps.SealError, match="entidad no declarada"):
        ps.seal(_write(tmp_path, EXPORT), "  ")


def test_zero_data_rows_is_red_not_empty_green(tmp_path):
    only_totals = "vendedor;importe\nTOTAL GENERAL;0\n"
    with pytest.raises(ps.SealError, match="verde vacío"):
        ps.seal(_write(tmp_path, only_totals), "SAS", delimiter=";", skip_regex="TOTAL")


@pytest.mark.parametrize("n_rows", [ps.XLS_ROW_CEILING, ps.XLS_ROW_CEILING - 1])
def test_xls_row_ceiling_is_flagged_as_truncated(tmp_path, n_rows):
    text = "a\n" + "x\n" * (n_rows - 1)
    with pytest.raises(ps.SealError, match="truncado"):
        ps.seal(_write(tmp_path, text), "SAS")


def test_one_row_below_ceiling_window_is_not_truncated(tmp_path):
    # Gemelo de frontera: el fixture roza el techo sin tocarlo.
    text = "a\n" + "x\n" * (ps.XLS_ROW_CEILING - 3)
    s = ps.seal(_write(tmp_path, text), "SAS")
    assert s["filas_leidas"] == ps.XLS_ROW_CEILING - 3


def test_declared_encoding_decodes_accented_byte(tmp_path):
    # 0xCD es 'Í' en cp1252; leerlo como cp850 daba '═'. Se fija el byte.
    p = _write(tmp_path, "cliente\nENVÍO SALTO\n", encoding="cp1252")
    assert p.read_bytes().count(b"\xcd") == 1
    s = ps.seal(p, "SAS", encoding="cp1252")
    assert s["filas_leidas"] == 1


def test_wrong_encoding_is_red_via_cli(tmp_path):
    p = _write(tmp_path, "cliente\nENVÍO SALTO\n", encoding="cp1252")
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(p), "--entity", "SAS"],
        capture_output=True,
    )
    assert r.returncode == 1
    assert b"SELLO-ROJO" in r.stderr


def test_sha_changes_when_file_changes(tmp_path):
    p = _write(tmp_path, EXPORT)
    before = _seal(p)["sha256"]
    p.write_bytes(EXPORT.replace("100,50", "100,51").encode())
    assert _seal(p)["sha256"] != before


def test_cli_json_and_exit_zero(tmp_path):
    p = _write(tmp_path, EXPORT)
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(p), "--entity", "SAS", "--delimiter", ";",
         "--header-rows", "3", "--skip-regex", "TOTAL", "--json"],
        capture_output=True,
    )
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout.decode("utf-8"))
    assert out["filas_leidas"] == 2
    assert out["export_mtime_utc"].endswith("+00:00")


def test_cli_without_entity_is_usage_error(tmp_path):
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(_write(tmp_path, EXPORT))],
        capture_output=True,
    )
    assert r.returncode == 2


def test_markdown_seal_says_when_period_is_missing(tmp_path):
    s = ps.seal(_write(tmp_path, "a\n1\n"), "SAS")
    assert "NO DECLARADO" in ps.as_markdown(s)
