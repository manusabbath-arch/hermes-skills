# Plan: convertir "¿funciona?" en checks reutilizables + ampliar skills con aprendizajes data-driven

> Para Hermes: ejecutar con subagent-driven-development, una tarea por skill/feature.

**Goal:** Terminar con el "nunca sé si el sistema mide lo que dice" — mecanizando la
capa de invariantes de contrato de datos como skill reutilizable en el tap
`manusabbath-arch/hermes-skills`, y aprovechar engram/Hermes/Claude como capas data-driven
(hacer que el ecosistema sea self-attesting, no más sesiones de debug ad-hoc).

**Architecture:** Un sistema empírico deja de "tener bugs" cuando cada eslabón del pipeline
publica un contrato de datos (campos que promete poblar) y un check continuo lo verifica
por ciclo, fallando ALTO. Eso se entrega como skill (`empirical-system-invariants`) con una
plantilla (`templates/data-contracts.md`) y un script de ejemplo (`scripts/invariant_guard.py`)
que es agnóstico del proyecto. El resto del plan es ampliar el ecosistema para que el agente
aprenda y se autocorrija (engram como memoria de veredictos, Hermes MCP como fuente única,
Claude/delegación para auditorías).

**Tech Stack:** Hermes Skills (SKILL.md + templates/ + scripts/), engram MCP (`mem_*`),
Hermes MCP resources, Claude Code CLI (delegación), los datos reales de
`/home/mamba/polymarket-trading-bot` como fuente de validación empírica.

---

## Contexto / diagnóstico (por qué este plan)

El usuario reporta el síntoma estructural: cada sesión encuentra una falla nueva
(phantom wirings, `edge_neto` siempre NULL porque el código nunca se escribió, flags que el
.env no tiene, docs que driftean). El `empirical-project-playbook` ya cataloga la **familia**
de silencios traidores como conocimiento. Lo que falta es la **batería operativa** que, por
ciclo, atestigüe que cada etapa hizo lo que dice — y que esa batería sea **reutilizable**
para cualquier proyecto empírico futuro (la estrategia declarada del usuario: extrapolar el
método a futuros proyectos y a la capa de análisis empresarial).

La skill `empirical-project-playbook` ya tiene "Si es mecanizable, es check que falla el
build" como mandamiento Nº3, pero no entrega EL MECANISMO por ciclo ni la herramienta
copia-pega. Este plan cierra ese hueco.

## Entregables

1. Skill nueva `empirical-system-invariants` en el tap (fuente canónica) + re-propagar.
2. Ampliación del `empirical-project-playbook`: sección de "capa de invariantes" + cómo
   aprovechar engram/Hermes/Claude como capas data-driven (puente a las oportunidades abajo).
3. Script de ejemplo agnóstico `scripts/invariant_guard.py` (guard por contrato de datos).
4. Plantilla `templates/data-contracts.md` (cómo declarar el contrato por etapa).
5. Actualizar README del tap con las skills nuevas.
6. Validación empírica: aplicar la plantilla a 2 etapas reales del polymarket-bot
   (`sports_model` → `rejected_signals` edge_populado; WS → book medido) como prueba de que
   la herramienta funciona sobre deuda REAL, no solo teoría.

---

# Track A — Skill de capa de invariantes (el núcleo)

### Task A1: Crear skill `empirical-system-invariants/SKILL.md`

**Objective:** skill que provea la definición operativa de "funcionando" y la batería
por ciclo.

**Files:**
- Create: `/home/mamba/hermes-skills/skills/empirical-system-invariants/SKILL.md`

**Contenido (frontmatter + cuerpo):**
- frontmatter: name, description "Use when auditing or operating an empirical/agent-built
  system that must prove it measures what it claims. Fail-high invariant battery.",
  version 1.0.0, related_skills: [empirical-project-playbook, systematic-debugging].
- Cuerpo con:
  - **Los 5 contratos de datos** (qué verificar por ciclo):
    1. WS/ingest: ¿entregó books, o procesó estalejos? (contador de stales)
    2. Modelo: ¿model_prob pobló los campos que el siguiente pasa consume, o escribió NULL?
    3. Rejected/trades: ¿edge_populado trae fuentes o phantom NULL?
    4. Guard→orden: ¿la señal que pasó guards es la misma que salió a orden? (no wiring fantasma)
    5. Shadow: ¿vio un book medido, no una fila degenerada sin book?
  - **Regla de semáforo**: ciclo ROJO si un check falla, con el eslabón exacto; la
    confianza la da la batería completa en verde, no la memoria del operador. NULL≠0.
  - **Falla alto**: cada check fallido loguea el eslabón + valor esperado vs real; nunca
    `|| true`; nunca swallow-exception.
  - **Cómo declarar un contrato** (pasos) + apuntar a la plantilla.
  - **Cómo correrla** (por ciclo vía systemd/cron, y bajo demanda vía CLI).
  - Sección "Verificar la skill": script de ejemplo + cómo comprobarlo sobre un proyecto real.

### Task A2: Script de ejemplo `scripts/invariant_guard.py`

**Objective:** guard agnóstico y copia-pega que un proyecto adapta declarando su contrato.

**Files:**
- Create: `/home/mamba/hermes-skills/skills/empirical-system-invariants/scripts/invariant_guard.py`

**Comportamiento:**
- Recibe un contrato (dict: etapa → {campo, condición}) vía JSON o hardcode de ejemplo.
- Recorre cada check: ¿existe el campo? ¿no es NULL? ¿tiene valores plausibles? ¿la
  firma que se consume existe?
- Exit code: 0 = todos verdes, 1 = al menos un ROJO (con detalle del eslabón). Nunca traga
  excepción sin marcar ROJO.
- Sin dependencias fuera de stdlib (portable a cualquier venv); paths anclados a `__file__`
  o inyectados por env, nunca al cwd.
- Modo `--contract <path.json>` para reusarlo en cualquier proyecto sin tocar el script.

### Task A3: Plantilla `templates/data-contracts.md`

**Objective:** cómo un proyecto declara sus contratos de datos por etapa.

**Files:**
- Create: `/home/mamba/hermes-skills/skills/empirical-system-invariants/templates/data-contracts.md`

**Contenido:** tabla por etapa (etapa fuente → etapa consumidora → campo prometido →
condición que atestigua que se pobló → query/log de PRODUCCIÓN que lo demuestra). Incluye
ejemplo real del polymarket-bot (`sports_model.edge_*` → `rejected_signals`, que hoy vive
NULL y es la deuda documentada) y el "gemelo de frontera" para cada condición.

### Task A4: Propagar la skill al perfil default y a los que la usan

**Objective:** que la skill esté instalada y cargable.

**Files:**
- Modify: `/home/mamba/hermes-skills/README.md` (agregar fila en tabla Skills)

**Pasos:**
1. `git add` explícito de las rutas nuevas.
2. Commit conventional + push a main del tap (`feat: add empirical-system-invariants skill`).
3. `hermes skills install manusabbath-arch/hermes-skills/skills/empirical-system-invariants`
   (perfil default) + re-propagar a los otros perfiles que usan el tap.
4. Verificar con `skill_view(name='empirical-system-invariants')` y
   `hermes skills inspect manusabbath-arch/hermes-skills/skills/empirical-system-invariants`.

---

# Track B — Aprovechar engram / Hermes / Claude como capas data-driven

Objetivo transversal: que el ecosistema sea **self-attesting y self-amplificador** — cada
veredicto queda registrado, cada check nuevo se aprende, y las auditorías se delegan.

### Task B1: Ampliar `empirical-project-playbook` — sección "Capa de invariantes y veredictos"

**Objective:** unir el playbook con la nueva skill y formalizar las oportunidades de
engram/Hermes/Claude.

**Files:**
- Modify: `/home/mamba/hermes-skills/skills/empirical-project-playbook/SKILL.md`
  (agregar sección nueva, patch, no reescribir).

**Contenido nuevo (data-driven, con números del fuente):**
- **La batería por ciclo precede a cualquier métrica de producto.** Un feed de datos no se
  puede vender ni un edge confiar si el sistema no puede probar que mide lo que dice.
  Referenciar `empirical-system-invariants`.
- **Engram como memoria de veredictos, no de logs.** Guardar los RESULTADOS de checks y
  findings (veredicto, n, EV, kill/success, dataset_version) como observaciones con
  `topic_key` estable — no el ruido de progreso. Un nuevo check aprendido tras un incidente
  se registra para que cualquier agente futuro lo cargue. (Hermes ya sabe que engram y
  Hermes tienen memorias nativas separadas; el criterio de qué silo guarda qué es explícito.)
- **Hermes MCP como fuente única del estado.** Exponer health/checks/veredictos como
  recursos MCP para que agentes y dashboards lean el MISMO dato que el sistema usa — nunca
  una copia que drifta. (Esto ya es el patrón "MCP como capa de integración" del playbook;
  acá se vuelve parte del contrato de datos.)
- **Claude Code y delegación para auditorías atómicas con verificación de handle.** Delegar
  (codex/claude/opencode) solo tareas atómicas de auditoría; verificar el handle real
  (query de prod, SHA, valores plausibles) uno mismo — nunca self-report. Esto corta el ciclo
  de "sesión de debug que encuentra el próximo phantom wiring": la auditoría se ejecuta como
  tarea acotada y su output se verifica contra la batería.

### Task B2: Ampliar README del tap

**Objective:** documentar la ampliación.

**Files:**
- Modify: `/home/mamba/hermes-skills/README.md`

**Contenido:** fila/descripción de la nueva skill y la sección nueva del playbook; nota de
que `empirical-system-invariants` trae la herramienta (script) + plantilla.

### Task B3: Validación empírica sobre deuda real (polymarket-bot)

**Objective:** probar la plantilla y el script sobre 2 contratos REALES para que la skill
"pase su propio criterio de adopción" con presencia=utility.

**Files:**
- Create (borrador, NO tocar el repo del bot salvo leer): un contrato JSON de prueba en
  `/home/mamba/hermes-skills/` o `/tmp` con los 2 contratos.
- Solo lectura de `/home/mamba/polymarket-trading-bot` y de la DB de prod vía query.

**Los 2 contratos a validar:**
1. `sports_model` → `rejected_signals`: campo `edge_elo`/`edge_form`/`edge_casino` prometido
   pero NULL. Check: COUNT(*) con edge_populado vs total; ROJO si 0% poblado. (Esto ya está
   documentado como deuda estructural en el playbook/skill de sports analysis; la batería lo
   convierte en ROJO medible.)
2. WS → book medido: `orderbook_snapshots` con `bids`+`asks` no vacíos; el shadow ledger no
   escribe fila sin book. Check: filas con book vacío > 0 → ROJO.

**Criterio de éxito (la skill demuestra utilidad):**
- El script devuelve exit 1 con detalle de eslabón en al menos el contrato #1 (esperado:
  está roto hoy → es la prueba de que el guard DETECTA la deuda real).
- La plantilla queda rellenable con los nombres reales del bot.

---

## Pasos mecánicos de ejecución (para el implementador)

Cada tarea es 2-5 min. TDD donde aplique; los cambios al tap usan `git add <paths>`
explícitos (nunca -A), commit conventional, push; la propagación usa
`hermes skills install`.

## Archivos que van a cambiar
- Crear: `skills/empirical-system-invariants/SKILL.md`
- Crear: `skills/empirical-system-invariants/scripts/invariant_guard.py`
- Crear: `skills/empirical-system-invariants/templates/data-contracts.md`
- Modificar: `skills/empirical-project-playbook/SKILL.md`
- Modificar: `README.md`

## Validación
- `skill_view('empirical-system-invariants')` carga sin error; linked_files muestra
  scripts/ y templates/.
- `python3 skills/empirical-system-invariants/scripts/invariant_guard.py --contract /tmp/example.json`
  sobre el contrato #1 devuelve exit 1 con el eslabón identificado (prueba que detecta).
- `hermes skills inspect manusabbath-arch/hermes-skills/skills/empirical-system-invariants`
  resuelve nombre/descripción legibles.
- Los 2 contratos reales quedan documentados (números reales, no estimaciones).

## Riesgos / tradeoffs / preguntas abiertas

- **Alcance del contrato vs costo por ciclo:** la batería debe ser ligera (stdlib, sin
  cargar modelos). No meter bootstrap caro in-cycle — separar check barato (per ciclo) de
  análisis caro (CLI). Señal de costo: ciclos que caen en múltiplos exactos.
- **NULL≠0:** el contrato debe declarar si "campo ausente" es defecto (NULL) o dato legítimo
  (0). Un check que trate 0 como fallo eterno → fatiga de alertas. Diseñar el contrato con
  ese campo explícito.
- **¿Aplicar la batería también como pre-deploy gate?** Pregunta abierta sujeta al usuario:
  ¿el guard solo monitorea en prod, o también bloquea el deploy si un contrato no se cumple?
  (Recomendado: monitor primero, gate después de medir en prod durante horas.)
- **Engram vs Hermes memory:** cada uno tiene su silo; el criterio (qué guarda cuál) debe
  quedar explícito en el playbook antes de propagar cualquier hábito de escritura. No
  escribir desde sesiones Hermes al engram del proyecto (convención ya documentada).

## Orden sugerido
A1 → A2 → A3 → B1 → B2 → B4(validación) → A4(propagar al final, para no propagar a medio
cambio). Alternativamente propagar tras A3 en el perfil default para poder testear con la
skill instalada.
