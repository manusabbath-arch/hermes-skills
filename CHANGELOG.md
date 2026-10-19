# Changelog

Una entrada por tag. Cada skill lleva su propia `version` en el frontmatter, y
`scripts/validate_skills.py` falla si una skill cambió desde el último tag sin subirla.
Cada release adjunta `SHA256SUMS` para verificar lo instalado (ver `SECURITY.md`).

## v1.2.0 — 2026-10-19

Empaquetado para cualquier agente. Ninguna skill cambió de contenido.

- **Plugin de Claude Code:** `.claude-plugin/plugin.json` y `marketplace.json`; el CI corre
  `claude plugin validate --strict` e instala el plugin en una configuración limpia
  verificando que resuelvan las 7 skills.
- **Codex, Cursor y Hermes:** `scripts/install_skills.py` copia a `~/.agents/skills/` (o
  `~/.cursor`, `~/.claude`, `~/.hermes`, o una carpeta de proyecto) y verifica cada archivo
  contra el origen. Nunca pisa sin `--force` ni toca skills ajenas. Probado en Linux y
  Windows en el CI.
- El validador exige que `plugin.json`, el marketplace y la primera entrada de este
  CHANGELOG tengan la misma versión.

## v1.1.0 — 2026-10-19

Primer release con tag. Las skills de septiembre pasan a 1.1.0; la nueva arranca en 1.0.0.

### Skills
- **Nueva: `erp-business-analysis` 1.0.0.** Las ocho formas en que un análisis sobre un
  ERP publica una cifra falsa y plausible, procedencia, canario, retracciones y decisiones
  con dueño. Scripts `provenance_seal.py` y `doc_lifecycle.py`.
- **`agent-ready-project` 1.1.0.** Verde vacío, varios agentes en un repo, planes que
  declaran cómo fallan, sesiones largas, evaluador separado. Scripts `phantom_wiring.py`,
  `prod_write_guard.py` y `worktree_guard.py`.
- **Las otras cinco, 1.1.0.** Redactadas en neutro (los casos de origen en
  `references/casos.md`), con sección "Cuándo NO aplicarla" y límites declarados frente a
  sus vecinas. Los ejemplos de Delta corren de verdad, con test.

### Confianza
- El validador exige scripts solo con stdlib, sin red, `subprocess` en lista explícita, y
  texto sin inyección ni Unicode invisible.
- Datos del negocio de origen: rojo ante un monto preciso (3+ cifras significativas) que
  no diga `ficticio`, y ante los términos de un `.private-terms` local, ignorado por git.
- La versión de cada skill tiene que subir con su contenido (contra el último tag).
- `SHA256SUMS` por release; `.gitattributes` fija LF para que verifique también un clon
  de Windows; job de CI en Windows.

### Medición
- Evals ciegas en Haiku, Sonnet y Opus: con skill 88, 97 y 100 de 105 criterios; sin
  skill 54, 57 y 59. Detalle y límites en `EVALS.md`.

### Pendiente
- Tags firmados (no hay llave de firma configurada).
- Ronda C de evals y revisión de criterios por alguien ajeno.
