# Changelog

Una entrada por tag. Cada skill lleva su propia `version` en el frontmatter, y
`scripts/validate_skills.py` falla si una skill cambió desde el último tag sin subirla.
Cada release adjunta `SHA256SUMS` para verificar lo instalado (ver `SECURITY.md`).

## v1.5.0 — 2026-11-01

Segunda ronda de aprendizajes del proyecto de la distribuidora, y el benchmark de la fase 5.

- **`erp-business-analysis` 1.1.0:** `references/base-erp-legado.md` (modelo medido por
  partición, integridad que la base no declara, trampas de join, el universo de una suma,
  la fila que un `||` con NULL borra en DB2, leer la salida por contenido, el wrapper de solo
  lectura, exports) y la sección "Antes de calcular: ¿ya está medido?".
- **`agent-ready-project` 1.3.0:** `references/diseno-de-guardas.md` y
  `scripts/check_baseline.py` (regresión vs rojo declarado con condición de salida, chequeo
  desaparecido, sellar mezcla; con tests y pasada de mutación); §10 de `multi-agent-repo.md`
  (ramas vivas, worktrees que desaparecen).
- **`empirical-project-playbook` 1.2.0:** operar el entorno (gasto en modelos con tope y
  nunca programado, salud sin dato = STALE, logs sin datos de terceros, limpieza que lista).
- **9 escenarios de evals nuevos** (3 negativos). Se escribieron después de la prosa, contra
  la regla del tap; todavía no se corrieron.
- **`benchmarks/erp-trampas/`:** ocho trampas de exports con su cifra ingenua y la correcta,
  puntuación automática, runner con tope de gasto obligatorio. Primera corrida (Haiku y
  Sonnet, 0,67 USD): **no discrimina**, ver `benchmarks/erp-trampas/runs/2026-10-31/LECTURA.md`.
  **v2** (`benchmarks/erp-trampas/v2/`, con pre-registro commiteado antes de correr): exports
  de más de 1.000 filas, respuesta por script que el runner corre con un filtro, preguntas
  de negocio. Tampoco discrimina (0 caídas en 40 llamadas, 1,17 USD): ver su `LECTURA.md`.
  **La fase 5 se cierra con este resultado negativo**, sin una v3 ajustada hasta que la
  skill gane.
- **Anonimización:** el nombre del proyecto de origen salió de los 9 lugares donde seguía
  publicado, y de 3 líneas que entraron con la v1.4.0 (`docs/inventario-perfil-vs-tap.md` y
  `designing-mechanical-guards` 1.0.1, que además se cruza con `diseno-de-guardas.md`).
- Esta entrada se escribió como v1.4.0 y pasó a v1.5.0 al rebasar sobre la v1.4.0 publicada.

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
