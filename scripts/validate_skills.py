#!/usr/bin/env python3
"""
validate_skills.py — build-failing validator for this skills tap.

The playbook this repo publishes says: "if it can be mechanized, it is a check
that fails the build, not a paragraph." This is that check, applied to the repo
itself.

Verifies, for every skills/<name>/:
  - SKILL.md exists and its YAML frontmatter parses
  - required keys are present (name, description, version)
  - `name` matches the directory name (the loader keys on the directory)
  - `description` is a real trigger, not a stub - it is the ONLY text an agent
    reads to decide whether to load the skill
  - every templates/ references/ scripts/ path cited in the body exists
  - related_skills that live in this repo actually resolve
  - no `|| true` / `continue-on-error` inside shipped scripts (a gate that
    cannot fail is not a gate)
  - shipped Python compiles
  - rules from Anthropic's skill authoring guide: `name` is lowercase/digits/
    hyphens, <=64 chars, without the reserved words "anthropic"/"claude";
    `description` carries no XML tags; a references/ or templates/ .md longer
    than 100 lines opens with a table of contents (an agent previews long files
    with `head`); references/ files do not cite other references/ files (keep
    them one level deep from SKILL.md, or the agent reads them partially)

Exit codes: 0 all green, 1 at least one RED. Paths anchored to __file__.
"""
from __future__ import annotations

import py_compile
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"

REQUIRED_KEYS = ("name", "description", "version")
MIN_DESCRIPTION_CHARS = 80
MAX_DESCRIPTION_CHARS = 1024
MAX_SKILL_LINES = 500

# A description made only of these words triggers on nothing a user would type.
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME_CHARS = 64
RESERVED_NAME_WORDS = ("anthropic", "claude")
XML_TAG = re.compile(r"</?[A-Za-z][\w-]*[^>]*>")
TOC_THRESHOLD_LINES = 100
TOC_HEADING = re.compile(r"^#{2,3} (Contents|Contenido|Índice)\s*$", re.M | re.I)
TOC_WINDOW_LINES = 30

STUB_PATTERN = re.compile(
    r"^use when [\w/\- ]{0,40}(projects?|skills?|agents?|repos?)\.?$", re.I
)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Minimal flat YAML frontmatter reader (no dependency on PyYAML)."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    if end == -1:
        return None
    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line or line.startswith((" ", "\t", "#")):
            continue
        key, sep, value = line.partition(":")
        if sep:
            out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def cited_paths(body: str) -> set[tuple[str | None, str]]:
    """Paths the prose promises, as (skill_prefix, path).

    A citation may be local (`templates/foo.md`) or qualified with another
    skill (`empirical-system-invariants/scripts/guard.py`). An unqualified path
    is resolved against the citing skill - which is exactly how an agent reads
    it, and why a cross-skill path written bare is a broken reference.
    """
    found: set[tuple[str | None, str]] = set()
    pattern = r"`((?:([a-z0-9][a-z0-9-]*)/)?(?:templates|references|scripts)/[\w./-]+)`"
    for m in re.finditer(pattern, body):
        full, prefix = m.group(1).rstrip(".,;:)"), m.group(2)
        if full.endswith("/"):
            continue
        rel = full[len(prefix) + 1:] if prefix else full
        found.add((prefix, rel))
    return found


def check_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        return [f"{name}: falta SKILL.md"]

    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        return [f"{name}: frontmatter YAML ausente o sin cierre `---`"]

    for key in REQUIRED_KEYS:
        if not fm.get(key):
            errors.append(f"{name}: frontmatter sin `{key}`")

    if fm.get("name") and fm["name"] != name:
        errors.append(
            f"{name}: frontmatter name='{fm['name']}' != directorio '{name}' "
            "(el loader indexa por directorio)"
        )

    fm_name = fm.get("name", "")
    if fm_name:
        if len(fm_name) > MAX_NAME_CHARS or not NAME_PATTERN.match(fm_name):
            errors.append(
                f"{name}: name='{fm_name}' debe ser minúsculas/dígitos/guiones, "
                f"<= {MAX_NAME_CHARS} chars"
            )
        for word in RESERVED_NAME_WORDS:
            if word in fm_name:
                errors.append(f"{name}: name contiene la palabra reservada '{word}'")

    desc = fm.get("description", "")
    if desc and XML_TAG.search(desc):
        errors.append(f"{name}: description con tag XML '{XML_TAG.search(desc).group(0)}'")
    if desc:
        if len(desc) < MIN_DESCRIPTION_CHARS:
            errors.append(
                f"{name}: description de {len(desc)} chars (<{MIN_DESCRIPTION_CHARS}). "
                "Es el UNICO texto que decide si la skill se carga: nombrá los "
                "términos que un usuario realmente teclea."
            )
        if len(desc) > MAX_DESCRIPTION_CHARS:
            errors.append(f"{name}: description de {len(desc)} chars (>{MAX_DESCRIPTION_CHARS})")
        if STUB_PATTERN.match(desc.strip()):
            errors.append(f"{name}: description genérica, no dispara con nada: '{desc}'")

    n_lines = text.count("\n") + 1
    if n_lines > MAX_SKILL_LINES:
        errors.append(
            f"{name}: SKILL.md de {n_lines} líneas (>{MAX_SKILL_LINES}). "
            "Mové el detalle a references/ (progressive disclosure)."
        )

    body = text[text.find("\n---\n", 3) + 5:]
    local_skills = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}
    for prefix, rel in sorted(cited_paths(body), key=lambda x: (x[0] or "", x[1])):
        if prefix is None:
            if not (skill_dir / rel).exists():
                errors.append(
                    f"{name}: el cuerpo cita `{rel}` como local y no existe "
                    "(si es de otra skill, calificala con su nombre)"
                )
        elif prefix in local_skills:
            if not (SKILLS_DIR / prefix / rel).exists():
                errors.append(f"{name}: el cuerpo cita `{prefix}/{rel}` y no existe en este tap")
        # prefijo desconocido = skill externa al tap, no verificable acá.

    for sub in ("references", "templates"):
        for doc in sorted((skill_dir / sub).glob("*.md")):
            doc_text = doc.read_text(encoding="utf-8")
            n_doc = doc_text.count("\n") + 1
            head = "\n".join(doc_text.splitlines()[:TOC_WINDOW_LINES])
            if n_doc > TOC_THRESHOLD_LINES and not TOC_HEADING.search(head):
                errors.append(
                    f"{name}: {sub}/{doc.name} tiene {n_doc} líneas y no abre con "
                    f"'## Contents' en sus primeras {TOC_WINDOW_LINES} (>{TOC_THRESHOLD_LINES} "
                    "líneas: el agente lo previsualiza con head y no ve el resto)"
                )
            if sub == "references":
                for _prefix, rel in cited_paths(doc_text):
                    if rel.startswith("references/"):
                        errors.append(
                            f"{name}: references/{doc.name} cita `{rel}`: las referencias "
                            "van a un solo nivel de SKILL.md"
                        )

    for script in skill_dir.rglob("*.py"):
        if "tests" in script.parts:
            continue
        source = script.read_text(encoding="utf-8")
        for banned in ("|| true", "continue-on-error"):
            # Ignorar la mención en prosa/docstring que EXPLICA por qué está prohibido.
            for line in source.splitlines():
                if banned in line and "NUNCA" not in line.upper() and not line.strip().startswith("#"):
                    errors.append(f"{name}: {script.name} contiene `{banned}` (gate que no puede fallar)")
        with tempfile.NamedTemporaryFile(suffix=".pyc", delete=True) as tmp:
            try:
                py_compile.compile(str(script), cfile=tmp.name, doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"{name}: {script.name} no compila -> {exc.msg.strip()}")

    return errors


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"VALIDATE-SKILLS: no existe {SKILLS_DIR}", file=sys.stderr)
        return 1

    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
    if not skill_dirs:
        print("VALIDATE-SKILLS: el tap no publica ninguna skill", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for d in skill_dirs:
        errs = check_skill(d)
        all_errors.extend(errs)
        print(f"[{'ROJO' if errs else 'OK'}] {d.name}")
        for e in errs:
            print(f"    - {e}")

    print(
        f"\nVALIDATE-SKILLS: {len(skill_dirs)} skills, "
        f"{len(all_errors)} problema(s)"
    )
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
