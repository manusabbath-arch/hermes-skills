# Changelog

Una entrada por tag. Cada skill lleva su propia `version` en el frontmatter, y
`scripts/validate_skills.py` falla si una skill cambió desde el último tag sin subirla.
Cada release adjunta `SHA256SUMS` para verificar lo instalado (ver `SECURITY.md`).

## v1.6.2 — 2026-11-02

Límites de activación entre skills que se pisan (decisión del dueño del tap).

- **Descriptions con "Not for X: use Y"** en `designing-mechanical-guards` 1.1.1,
  `unattended-run-verification` 1.0.1, `agent-ready-project` 1.3.1,
  `empirical-project-playbook` 1.2.1 y `empirical-system-invariants` 1.1.1. La de
  `empirical-project-playbook` ahora dice que cubre operar el entorno (gasto con tope, salud
  sin dato = STALE), que la skill trae desde v1.6.0.
- **Activación medida otra vez con la misma semilla**
  (`evals/runs/2026-11-02-activacion-limites/`, pre-registrada en el mismo commit).

## v1.6.1 — 2026-11-02

Mediciones de las skills que entraron sin corrida, y criterios que se pueden medir.

- **Ronda D de evals** (`evals/runs/2026-11-02-ronda-d/`, pre-registrada): las 4 skills de
  v1.5.0, Haiku y Sonnet, 0,67 USD. Las tres hipótesis se cumplen: no negativos con / sin
  skill, Haiku 37/9 y Sonnet 44/8 (de 48).
- **Activación con las 15 skills** (`.../ronda-d/activation/`, pre-registrada; runner nuevo
  `evals/activacion.py`): las 8 nuevas se eligen solas (28, 28 y 30 de 32) y ningún pedido
  ajeno carga una skill, pero se quedan con pedidos de las viejas: H2 falla en Haiku (31 de
  41). Falta un "Not for X: use Y" entre skills que se pisan.
- **Criterios medibles:** `grounded-citations` 1.0.1 (9 criterios) y
  `documentation-drift-audit` 1.0.1 (2) pedían ejecutar comandos que el protocolo de evals
  no permite; ahora piden proponerlo. Lo que se exige saber no cambia.
- **Ronda E** (`evals/runs/2026-11-02-ronda-e/`, pre-registrada): las dos skills con los
  criterios nuevos, 0,30 USD. `documentation-drift-audit` +8 y +10; `grounded-citations` +10
  en Sonnet (era +5 con los criterios viejos) y +1 en Haiku, que lee la skill y no aplica el
  procedimiento sin herramientas.

## v1.6.0 — 2026-11-01

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
  la regla del tap; se midieron en la ronda C (abajo).
- **Ronda C de evals** (`evals/runs/2026-11-01-ronda-c/`, pre-registrada): los 9 escenarios
  nuevos y las 4 skills de v1.4.0, Haiku y Sonnet, 1,30 USD. Las tres hipótesis se cumplen
  (escenarios nuevos +8 en los dos modelos; skills de v1.4.0 +19 y +25 de 48; negativos 14
  de 14). `grounded-citations` no se puede medir sin comandos ni web, y está dicho así.
  Runner nuevo: `evals/ronda.py` (con tope de gasto obligatorio y notas incompletas = rojo).
- **Guardas unificadas:** `designing-mechanical-guards` 1.1.0 suma lo que solo estaba en el
  catálogo de `agent-ready-project` (rechazo barato antes del trabajo caro, regla nueva sobre
  un corpus viejo por fecha de corte, permisos versionados), y cada sección de
  `diseno-de-guardas.md` apunta a su procedimiento general.
- **CI:** acciones con runtime Node 24 (checkout v5, setup-python v6, setup-node v5), también
  en el CI que genera el kit.
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
- **`validate_skills.py`: ruta personal = rojo.** Una ruta absoluta con el usuario de la
  máquina (`C:\Users\<x>\…`, `/home/<x>/…`) se caza sin lista privada, también en
  `benchmarks/`; pasan los marcadores y `/home/runner`. Salieron 2 que estaban publicadas.
- **`validate_skills.py`: índice de relleno o dentro de código = rojo.** En v1.4.0, 8
  referencias abrían con un `## Contents` que no listaba nada ("See headings below") y una
  herramienta había metido 5 más dentro de bloques de Python, que dejaban de compilar (2
  ejemplos de `designing-mechanical-guards`). Índices reales generados de los encabezados,
  ejemplos que vuelven a compilar; `designing-mechanical-guards` y
  `external-data-source-intake` 1.0.1.
- **CI:** los términos privados se cargan desde el secreto `PRIVATE_TERMS`; sin él, el job
  deja un aviso visible en vez de pasar en silencio.
- Esta entrada se escribió como v1.4.0 y pasó a v1.6.0 al integrar las v1.4.0 y v1.5.0
  publicadas mientras estaba en revisión.

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
