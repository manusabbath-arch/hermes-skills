# Seguridad

Una skill no es documentación: es texto que un agente obedece y scripts que un agente
ejecuta con los permisos de quien la instaló. En 2026 se confirmaron más de mil skills
maliciosas en un marketplace público, y los escáneres automáticos se evadieron en la
gran mayoría de los casos. Este tap trata sus skills como código de supply chain, y
cada regla de abajo es un check que falla el build, no una promesa.

## Qué garantiza el tap (y qué lo verifica)

| Garantía | Check |
|---|---|
| Los scripts publicados importan **solo la biblioteca estándar** de Python: sin dependencias que instalar ni que se puedan secuestrar | `scripts/validate_skills.py` (análisis AST de imports) |
| **Ningún script sale a la red** (`socket`, `urllib`, `http`, `ssl`, `asyncio`…) | `scripts/validate_skills.py` |
| **`subprocess` solo donde está declarado** y con motivo: `doc_verify.py` (solo con `--allow-command`) y `worktree_guard.py` (corre `git`) | `SUBPROCESS_ALLOWED` en `scripts/validate_skills.py`; agregar uno queda visible en el diff |
| El texto de las skills **no trae frases de inyección** ("ignore previous instructions", "ignorá las instrucciones anteriores"), **instalaciones a ciegas** (`curl … \| sh`) ni **caracteres Unicode invisibles o bidireccionales** | `scripts/validate_skills.py` sobre todo `.md` y `.json` de cada skill |
| Lo que instalás es **exactamente lo publicado** en un tag | `SHA256SUMS` adjunto a cada release (`.github/workflows/release.yml`) |
| Ningún gate puede quedar en verde sin correr: sin `\|\| true` ni `continue-on-error` en scripts ni en CI | `scripts/validate_skills.py` y revisión de los workflows |

Las reglas tienen tests que las rompen a propósito (`scripts/tests/`).

## Verificar una instalación

```bash
# Bajar SHA256SUMS del release (por ejemplo v1.3.0) y, desde un clon del tap en ese tag:
python3 scripts/release_manifest.py --root /ruta/a/la/copia --check SHA256SUMS
# Una copia que solo trae skills/ (sin el kit de arranque):
python3 scripts/release_manifest.py --root /ruta/a/la/copia --check SHA256SUMS --only skills
```

El manifiesto cubre `skills/` y `kit/`. `install_skills.py` verifica cada skill contra el
origen al instalarla, y `kit_check.py` verifica en cada commit las guardas copiadas a un
proyecto contra los sha de `tools/guards/SOURCES.json`.

Falla si un archivo **cambió**, **falta** o **sobra**. Un archivo que nadie publicó y
aparece en tu copia es exactamente lo que hay que mirar.

## Qué NO garantiza

- **Que el agente no haga algo dañino por su cuenta.** Las skills de este tap proponen
  guardas (`prod_write_guard.py`, worktrees, commits con pathspec), pero instalarlas y
  configurarlas es decisión de cada proyecto.
- **El contenido de terceros que el agente lee mientras trabaja** (páginas web, issues,
  READMEs de dependencias). Eso es prompt injection en tiempo de uso; ver
  `skills/empirical-project-playbook/references/agent-security.md`.
- **Los tags no están firmados todavía.** El checksum prueba que la copia coincide con el
  release, no quién lo publicó. Firmar tags está en el plan.

## Reportar un problema

Abrí un issue privado (GitHub → Security → *Report a vulnerability*) en
`manusabbath-arch/hermes-skills`, con la skill, el archivo y cómo reproducirlo. No
publiques el detalle de una vulnerabilidad en un issue abierto hasta que esté resuelta.
