#!/usr/bin/env python3
"""
prod_write_guard.py — hook PreToolUse que hace física la regla "producción es solo lectura".

Lee el payload JSON del agente por stdin y BLOQUEA (exit 2, motivo por stderr)
cuando la acción puede escribir en un sistema real:
  - un comando que invoca un cliente SQL declarado con una sentencia que
    modifica (INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER, MERGE, CREATE,
    GRANT, REVOKE);
  - un comando que escribe (cp, mv, rm, >, tee, sed -i, Set-Content...) sobre una
    ruta protegida;
  - una herramienta de archivo (Write, Edit, patch) cuyo DESTINO es una ruta
    protegida. Se mira el destino, nunca el contenido: un documento que cita la
    ruta no escribe en ella.

Origen: proyecto NG. El hook original en `sed` cortaba el valor de `command`
en la ÚLTIMA comilla del JSON; con el payload de Hermes o Antigravity, donde
`command` va seguido de otros campos, el valor quedaba contaminado y una
escritura pasaba sin bloquear. Acá el payload se parsea como JSON.

Contratos de entrada soportados (uno por agente, todos en el mismo script):
  Claude Code / Qwen / Kimi: {"tool_input": {"command": ...}} o {"tool_input": {"file_path": ...}}
  Hermes:                    {"tool_input": {"command"|"path": ...}, "session_id": ...}
  Antigravity:               {"CommandLine": ...}

Una entrada que no se puede leer se BLOQUEA: una guarda que no pudo mirar no
puede decir que es seguro. Una orden de otro agente no es la confirmación de una
persona: este hook corta igual.

Config (JSON, ruta por --config o env PROD_GUARD_CONFIG):
  {"sql_clients": ["psql", "db2", "sqlcmd", "mysql"],
   "protected_paths": ["/srv/erp", "C:/erp"]}

Exit codes: 0 permitido, 2 bloqueado (contrato PreToolUse de Claude Code).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_CONFIG = {"sql_clients": ["psql", "db2", "sqlcmd", "mysql", "sqlite3"], "protected_paths": []}

SQL_WRITE = re.compile(
    r"\b(insert\s+into|update\s+\S+\s+set|delete\s+from|drop|truncate|alter|merge\s+into|create|grant|revoke)\b",
    re.IGNORECASE,
)
SHELL_WRITE = re.compile(
    r"(>|\b(cp|mv|rm|rmdir|tee|touch|del|copy|move|ren|rename|xcopy|robocopy|mkdir"
    r"|set-content|add-content|out-file|remove-item|move-item|copy-item|new-item)\b|\bsed\s+-i)",
    re.IGNORECASE,
)
FILE_KEYS = ("file_path", "notebook_path", "path")
PATCH_TARGET = re.compile(r"^\*\*\* (?:Update|Add|Delete) File: (.+)$", re.MULTILINE)


class GuardInputError(Exception):
    pass


def norm(text: str) -> str:
    """Minúsculas y barras unificadas: C:\\ERP, c:/erp y C://erp dan lo mismo."""
    return re.sub(r"/+", "/", text.replace("\\", "/")).lower()


def extract(payload: dict) -> tuple[str, list[str]]:
    """(comando, destinos de archivo) del payload de cualquier agente soportado."""
    ti = payload.get("tool_input")
    ti = ti if isinstance(ti, dict) else {}
    command = ti.get("command") or payload.get("command") or payload.get("CommandLine") or ""
    if not isinstance(command, str):
        raise GuardInputError("`command` no es texto")
    targets = [v for k in FILE_KEYS for v in (ti.get(k), payload.get(k)) if isinstance(v, str) and v]
    patch = ti.get("patch") or ti.get("input") or ""
    if isinstance(patch, str):
        targets += PATCH_TARGET.findall(patch)
    return command, targets


def decide(payload: dict, config: dict) -> str | None:
    """Motivo del bloqueo, o None si la acción se permite."""
    command, targets = extract(payload)
    protected = [norm(p).rstrip("/") for p in config.get("protected_paths", []) if p]

    for t in targets:
        nt = norm(t)
        for p in protected:
            if nt == p or nt.startswith(p + "/"):
                return f"escritura de archivo sobre ruta protegida {p!r}: producción es solo lectura"

    if command:
        nc = norm(command)
        for client in config.get("sql_clients", []):
            if re.search(rf"(^|[\s/;&|(]){re.escape(client.lower())}(\.exe|\.bat|\.cmd)?\b", nc):
                m = SQL_WRITE.search(nc)
                if m:
                    return (f"sentencia que modifica ({m.group(1).split()[0].upper()}) vía {client!r}: "
                            "la base de producción es solo lectura; pedir confirmación a una persona")
        for p in protected:
            if p in nc and SHELL_WRITE.search(nc):
                return f"comando que escribe sobre ruta protegida {p!r}: producción es solo lectura"
    return None


def load_config(path: str | None) -> dict:
    path = path or os.environ.get("PROD_GUARD_CONFIG")
    if not path:
        return DEFAULT_CONFIG
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {**DEFAULT_CONFIG, **data}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config", help="JSON con sql_clients y protected_paths")
    args = ap.parse_args(argv)
    try:
        config = load_config(args.config)
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise GuardInputError("el payload no es un objeto JSON")
        reason = decide(payload, config)
    except (json.JSONDecodeError, GuardInputError, OSError) as exc:
        print(f"PROD-GUARD: bloqueado, no se pudo leer la entrada ({exc}); "
              "una guarda que no miró no puede decir que es seguro", file=sys.stderr)
        return 2
    if reason:
        print(f"PROD-GUARD: bloqueado — {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
