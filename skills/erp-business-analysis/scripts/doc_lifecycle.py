#!/usr/bin/env python3
"""
doc_lifecycle.py — retracciones que se propagan y decisiones con dueño.

Dos chequeos sobre el frontmatter de las notas Markdown de un proyecto de
análisis (los de `templates/validation-note.md` y `templates/decision-note.md`):

  RETRACCIÓN  una nota que declara `depends_on` sobre otra con `retractado` (o
              `estado: stale`) es ROJO, salvo que ella misma esté retractada.
              En NG, un informe retractado seguía citado como base por tres
              documentos y nada lo distinguía de la cita que lo retracta.
  DECISIÓN    una nota con campo `dueño`/`owner` (es una decisión):
                - `abierta` sin dueño, o sin `fecha_limite` ni
                  `disparador_revision`  -> ROJO;
                - cerrada (`decidida|rechazada|superada`) que escribió
                  `hipotesis` y `metrica_esperada` pero no `resultado_observado`
                  ni `estado_evaluacion` -> ROJO (se comprometió a medir).

Las referencias se resuelven por nombre de archivo sin extensión, así que
`depends_on: "[[2026-09-22-margen]]"`, `margen.md` o una lista funcionan igual.
Una referencia a una nota que no existe también es ROJO: la dependencia no se
puede verificar.

Denominador siempre en el reporte; cero notas revisadas es ROJO.

Uso:  python3 doc_lifecycle.py validaciones/ decisiones/ informes/
Exit: 0 sin rojos, 1 al menos un rojo.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

CLOSED = {"decidida", "rechazada", "superada", "decided", "rejected", "superseded"}
OPEN = {"abierta", "open"}
REF_TOKEN = re.compile(r"[^\s\[\],'\"|]+")


@dataclass
class Note:
    path: Path
    fm: dict[str, str]

    @property
    def key(self) -> str:
        return self.path.stem

    def get(self, *names: str) -> str:
        for n in names:
            v = self.fm.get(n, "").strip()
            if v:
                return v
        return ""

    @property
    def retracted(self) -> bool:
        return bool(self.get("retractado", "retracted")) or self.get("estado", "status").lower() == "stale"


def frontmatter(text: str) -> dict[str, str] | None:
    """Frontmatter plano (clave: valor), sin depender de PyYAML."""
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    out: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return out
        if not line or line[0] in " \t#-":
            continue
        k, sep, v = line.partition(":")
        if sep:
            v = re.sub(r"\s+#.*$", "", v).strip()
            out[k.strip()] = v.strip('"').strip("'")
    return None


def refs(value: str) -> list[str]:
    return [Path(t).stem for t in REF_TOKEN.findall(value) if t not in {"-", "nada", "none"}]


def load(targets: list[Path]) -> list[Note]:
    notes = []
    for t in targets:
        files = [t] if t.is_file() else sorted(t.rglob("*.md"))
        for f in files:
            fm = frontmatter(f.read_text(encoding="utf-8", errors="replace"))
            if fm is not None:
                notes.append(Note(f, fm))
    return notes


def check(notes: list[Note]) -> list[str]:
    reds: list[str] = []
    by_key = {n.key: n for n in notes}
    for n in notes:
        if not n.retracted:
            for r in refs(n.get("depends_on")):
                dep = by_key.get(r)
                if dep is None:
                    reds.append(f"{n.path}: depends_on '{r}' no existe entre las notas revisadas")
                elif dep.retracted:
                    reds.append(f"{n.path}: deriva de '{r}', que está retractada/stale "
                                f"(motivo: {dep.get('retractado', 'retracted') or 'stale'})")
        if "dueño" in n.fm or "owner" in n.fm:
            estado = n.get("estado", "status").lower()
            if estado in OPEN:
                if not n.get("dueño", "owner"):
                    reds.append(f"{n.path}: decisión abierta sin dueño")
                if not n.get("fecha_limite", "deadline", "disparador_revision", "review_trigger"):
                    reds.append(f"{n.path}: decisión abierta sin fecha_limite ni disparador_revision "
                                "(nunca inventar una fecha: un evento alcanza)")
            elif estado in CLOSED and n.get("hipotesis") and n.get("metrica_esperada"):
                if not (n.get("resultado_observado") and n.get("estado_evaluacion")):
                    reds.append(f"{n.path}: decisión {estado} con hipótesis y métrica, sin resultado "
                                "observado (si no era medible, vaciar hipotesis y metrica_esperada)")
    return reds


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("targets", nargs="+", type=Path)
    args = ap.parse_args(argv)
    notes = load(args.targets)
    decisions = sum(1 for n in notes if "dueño" in n.fm or "owner" in n.fm)
    print(f"DOC-LIFECYCLE: {len(notes)} nota(s) con frontmatter, {decisions} decisión(es)")
    if not notes:
        print("  ROJO: ninguna nota revisada (un check que no miró nada está apagado)")
        return 1
    reds = check(notes)
    for r in reds:
        print(f"  ROJO {r}")
    if not reds:
        print("  OK: sin derivaciones de notas retractadas y decisiones con dueño y disparador")
    return 1 if reds else 0


if __name__ == "__main__":
    sys.exit(main())
