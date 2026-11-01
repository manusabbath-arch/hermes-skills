# Changelog

Una entrada por tag. Cada skill lleva su propia `version` en el frontmatter, y
`scripts/validate_skills.py` falla si una skill cambió desde el último tag sin subirla.
Cada release adjunta `SHA256SUMS` para verificar lo instalado (ver `SECURITY.md`).

## v1.5.0 — 2026-11-01

Ola 2 de destilación desde el perfil Hermes: cuatro skills portables más, sin datos de
cliente. Inventario en `docs/inventario-perfil-vs-tap.md`.

- **Nueva: `tests-over-changing-data-exports` 1.0.0.** Tests sobre exports que se
  re-descargan: no globar «el más nuevo», aserciones de forma, skip con motivo,
  caché opt-in por sha.
- **Nueva: `outbound-notification-channels` 1.0.0.** Canal de salida (mail, chat,
  webhook, ntfy): secreto en el almacén del SO, apagado por defecto, un `--enviar`
  a mano no publica. El script de `keyring` no viaja (el validador recorre imports
  también dentro de `try/except`).
- **Nueva: `recurring-report-design` 1.0.0.** Informe de cadencia: rotación, dosis,
  latido, reloj real versus hora nominal. Tres referencias de layout, scheduler y
  bloques de trabajo.
- **Nueva: `documentation-drift-audit` 1.0.0.** Auditoría de docs contra el sistema.
  Script `check_docs_integrity.py` (stdlib); el punto de entrada por defecto es
  `README.md`.
- El README y el plugin pasan de 11 a 15 skills. Las evals están escritas; la
  corrida ciega de Haiku/Sonnet/Opus sigue siendo la de las 7 de v1.3.0.

## v1.4.0 — 2026-10-31

Ola 1 de destilación desde el perfil Hermes: cuatro skills portables, sin datos de
cliente. Inventario en `docs/inventario-perfil-vs-tap.md`.

- **Nueva: `designing-mechanical-guards` 1.0.0.** Procedimiento para convertir una
  regla en un check. El catálogo de pitfalls y las 22 recetas viven en `references/`.
- **Nueva: `unattended-run-verification` 1.0.0.** Verificar una corrida desatendida
  y su artefacto real (Task Scheduler, cron, spooler, procesos huérfanos, escuchas).
- **Nueva: `external-data-source-intake` 1.0.0.** Ingesta de una fuente que no es el
  sistema de registro (GPS, CKAN, telemetría, APIs vivas), con tres referencias.
- **Nueva: `grounded-citations` 1.0.0.** Ledger `scripts/sources.py` (stdlib) y
  verificación de citas. El import de `hermes_constants` no viaja: el tap resuelve
  `HERMES_HOME` / `~/.hermes` solo con stdlib.
- El README y el plugin pasan de 7 a 11 skills. Las evals de las cuatro nuevas están
  escritas (`evals/evals.json`); todavía no hay corrida ciega en Haiku/Sonnet/Opus
  (el cuadro de `EVALS.md` sigue siendo el de las 7 de v1.3.0).

## v1.3.0 — 2026-10-19

Kit de arranque *agent-ready* (fase 4 del plan).

- **`kit/` y `scripts/new_project.py`:** generan un proyecto con `AGENTS.md` (mapa corto)
  y `CLAUDE.md` que lo importa; `init.sh`, pre-commit y CI que corren la misma compuerta;
  `feature_list.json`, `progress.md` y plantillas de plan y decisión.
- **`tools/kit_check.py`**, la compuerta del proyecto generado, cada guarda con su
  denominador: guardas vendorizadas contra su sha (`SOURCES.json` con la versión del tap),
  phantom-wiring con línea base de trinquete, docs verificadas, secretos, `feature_list`
  (`passes: true` exige `evidence`), el hook de producción ejecutado con un `DROP TABLE` de
  prueba (un intérprete que no existe es rojo, no una guarda apagada) y worktrees.
- **Tests de mutación:** cada guarda del kit, rota a propósito, da rojo; el pre-commit
  rechaza un commit en rojo. El CI lo prueba en Linux y en Windows, y genera un proyecto
  y corre su `init.sh`.
- **`agent-ready-project` 1.2.0:** sección que apunta al kit.
- **`SHA256SUMS` cubre también `kit/`**; `--only skills` verifica una copia sin kit. La
  política de confianza (stdlib, sin red, `subprocess` en lista) se aplica al kit.

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
