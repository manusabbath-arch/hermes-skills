---
titulo: De cuaderno de lecciones a kit reutilizable y medido
fecha: 2026-10-18
estado: borrador          # borrador | aprobado | en-curso | integrado | cancelado
rama: ""                  # se completa al pasar a en-curso
dueño: manusabbath-arch
depends_on: PR #1 (erp-business-analysis, evals v1, skills en neutro)
---

# Plan: de cuaderno de lecciones a kit reutilizable y medido

## Contents

1. Norte y apuesta
2. Qué dice la investigación externa (y qué tomamos)
3. Fases (cada una con cómo falla y criterios con su control)
4. Lo que NO vamos a hacer
5. Orden y tamaño

## 1. Norte y apuesta

**Norte (un solo juez):** que alguien que no es el autor instale una skill del tap, la
use en su proyecto y la skill **cambie lo que el agente hace, medido**. Todo lo demás
(estrellas, cantidad de skills) es medio.

**Apuesta de posicionamiento:** *confianza verificable en el trabajo de agentes*, con
dos frentes donde el tap ya tiene material que casi nadie tiene:

- **Análisis de negocio sobre ERPs y planillas** (pymes, consultoras; español primero).
- **El arnés de repos construidos por varios agentes** (guardas, verde vacío, worktrees).

## 2. Qué dice la investigación externa (y qué tomamos)

| Fuente | Lección | Qué hacemos con ella |
|---|---|---|
| Guía de autoría de skills de Anthropic | Evaluaciones antes que prosa; probar con cada modelo; `description` en tercera persona con qué + cuándo | Evals v2 multi-modelo y medición de activación (fase 1) |
| Anthropic, "Effective harnesses for long-running agents" | Lista de features JSON que arranca fallando, progreso, `init.sh`, una feature por sesión | Kit de arranque (fase 4) |
| Anthropic, arnés de 3 agentes | El que juzga separado del que hace; cada pieza del arnés es una suposición que envejece | Evaluador ciego (ya hecho); re-medir al cambiar de modelo (fase 1) |
| OpenAI, "Harness engineering" | `AGENTS.md` corto como mapa; lo que no está en el repo no existe; reglas en CI, no en prosa | Plantilla de `AGENTS.md` de ~100 líneas en el kit (fase 4) |
| obra/superpowers | Flujo de trabajo, no lista suelta; el contenido separado del mecanismo de instalación; el cambio de plataforma volvió redundante su bootstrap | Empaquetar sin atar el valor al instalador (fase 2) |
| ClawHavoc / ToxicSkills (2026) | >1.000 skills maliciosas en un marketplace; escáneres evadidos >90%; tratar skills como código | La confianza como producto: sin red, sin dependencias, versionado y firmado (fase 3) |
| Encuestas 2026 (Databox, BCG vía Splunk) | 69% usa IA para análisis que van a dirección, 39% confía; la confianza es la barrera #1 | Benchmark de trampas de ERP: medir que el agente NO publica la cifra falsa (fase 5) |

## 3. Fases

### Fase 0 — Cerrar lo abierto

Mergear el PR #1 y propagar el tap a los perfiles por symlink.

- **Criterio 0.1:** `main` contiene las 7 skills con evals. *Control:* CI verde en
  `main` (`validate.yml`).

### Fase 1 — Medición que discrimine (evals v2)

Hoy las evals están en techo (58/58): ya no distinguen una skill buena de una mejor.

1. **Pedidos más difíciles**: 2 por skill, con una trampa que la respuesta genérica no ve.
2. **Casos negativos**: 1 por skill, un pedido donde la skill NO debería cambiar la
   respuesta (mide que no empuja de más).
3. **Activación**: un test donde el agente recibe las 7 `description` y un pedido, y dice
   cuál cargaría. Mide si la skill se elige sola, lo que hoy no se midió.
4. **Multi-modelo y repeticiones**: Haiku, Sonnet y Opus; 3 corridas por condición.
5. **Criterios de un tercero**: que alguien que no escribió la skill escriba o revise
   los criterios (hoy los escribió el mismo autor).
6. **Re-medir al cambiar de modelo**: la corrida se repite con cada modelo nuevo; si una
   skill deja de aportar, se adelgaza o se retira.

**Cómo puede fallar → control:**
- Evals que siguen en techo → la tabla muestra con skill < 100% en algún modelo; si da
  100% en todo, los pedidos no son difíciles.
- La skill se activa en pedidos que no le corresponden → el test de activación reporta
  falsos positivos por skill.
- Ruido presentado como señal → con 3 corridas, se reporta el rango, no un número.

**Criterios de aceptación:**
- 1.1 Cada skill tiene ≥ 5 escenarios, ≥ 1 negativo. *Control:* `validate_skills.py`
  (subir `MIN_EVALS` a 5 y exigir `"negativo": true` en al menos uno).
- 1.2 Hay tabla por modelo con rango de 3 corridas. *Control:* `eval_report.py` con
  `--runs` y el diff del CI.
- 1.3 Hay tasa de activación correcta por skill. *Control:* script de activación con su
  tabla en `EVALS.md`, regenerada en CI.

### Fase 2 — Empaquetado para cualquier agente

El formato `SKILL.md` ya lo leen Claude Code, Codex, Cursor y Copilot; el tap hoy solo
documenta Hermes.

1. Cumplir la especificación abierta de Agent Skills (agentskills.io) y validarlo.
2. Manifiesto de marketplace de plugins para Claude Code, para instalar con un comando.
3. Instrucciones de instalación para Codex y Cursor (rutas de skills de proyecto).
4. **Versionado**: tags semver, `CHANGELOG.md`, y la versión del frontmatter que sube con
   cada cambio de contenido.
5. Descripciones en inglés (activan en cualquier agente); cuerpo en español, declarado.

**Cómo puede fallar → control:**
- El manifiesto no instala → un job de CI instala el tap en un directorio limpio y
  verifica que cada skill resuelve.
- La versión no sube con el contenido → un check compara el diff de cada `SKILL.md`
  contra su `version` respecto del último tag.

**Criterios:** 2.1 instalación limpia en CI por cada agente soportado (*control:* job de
instalación); 2.2 `CHANGELOG` con una entrada por tag (*control:* check de versión).

### Fase 3 — La confianza como producto

Lo que el mercado de skills no ofrece hoy, y lo que ya sabemos mecanizar.

1. **Reglas mecanizadas para scripts publicados**: solo stdlib; sin red (`socket`,
   `urllib`, `http`); `subprocess` solo en una lista explícita (hoy: `worktree_guard.py`,
   que corre `git`). Un check del validador las hace cumplir.
2. **Escaneo del texto de las skills** buscando instrucciones de prompt injection
   ("ignorá las instrucciones anteriores", URLs a ejecutar, `curl | sh`).
3. `SECURITY.md`: qué hacen los scripts, qué no, cómo reportar.
4. **Manifiesto de checksums por release** y tags firmados, para que quien instala
   verifique que recibió lo publicado.

**Cómo puede fallar → control:** un script nuevo importa `requests` → rojo del
validador; una skill suma un `curl | sh` → rojo del escaneo; un release sin checksums →
el job de release falla.

**Criterios:** 3.1 los checks de red, dependencias e injection existen y se verificaron
por mutación (*control:* tests del validador); 3.2 cada tag trae checksums verificables
(*control:* job de release).

### Fase 4 — Kit de arranque *agent-ready*

Un repo plantilla que trae conectado lo que hoy son skills sueltas:

- pre-commit y CI con `phantom_wiring`, `doc_verify`, `worktree_guard`, escaneo de
  secretos y la baseline con trinquete;
- `prod_write_guard.py` ya registrado como hook de Claude Code, con su config de ejemplo;
- `AGENTS.md` de ~100 líneas como mapa, y `CLAUDE.md` que apunta a él;
- el arnés de sesiones largas: `feature_list.json` (todo arranca en `passes: false`),
  `progress.md` e `init.sh`;
- plantillas de plan (cómo falla + criterios con control) y de decisión.

**Cómo puede fallar → control:** el kit trae un check que no puede fallar → un test del
kit rompe cada guarda a propósito y espera rojo; la plantilla deriva del tap → el kit
copia los scripts del tag del tap y un check compara los sha.

**Criterios:** 4.1 `git clone` + `init.sh` deja un repo con CI verde (*control:* CI del
propio kit); 4.2 cada guarda del kit tiene su test de mutación (*control:* suite del kit).

### Fase 5 — Benchmark de trampas de ERP (el diferencial)

El problema #1 del público es no poder confiar en la cifra. Lo medible: dado un export
con errores conocidos, ¿el agente los encuentra antes de publicar?

1. **Exports sintéticos** (CSV/XLSX, sin datos reales) con las ocho trampas sembradas:
   fila `TOTAL GENERAL`, columnas que cambian de lugar entre reexports, período del
   preámbulo distinto del nombre, dos razones sociales mezcladas, montos en dos monedas,
   `0.00` de campos muertos, encoding cp1252, duplicados.
2. **Para cada trampa, la cifra ingenua y la correcta**, calculadas por un script de
   referencia.
3. **Eval:** el agente responde "¿cuánto vendimos / cuál es el margen?" con y sin
   `erp-business-analysis`; se cuenta cuántas trampas evitó.
4. Publicarlo como dataset abierto: sirve para evaluar cualquier agente de análisis, no
   solo el nuestro, y es lo que vuelve el tap referencia del nicho.

**Cómo puede fallar → control:** una trampa que ningún agente cae (no discrimina) → se
reporta la tasa de caída sin skill por trampa; una trampa que la referencia calcula mal →
la cifra correcta se verifica con una identidad independiente (canario) en un test.

**Criterios:** 5.1 ocho trampas con su cifra correcta testeada (*control:* tests del
benchmark); 5.2 tabla de trampas evitadas con y sin skill (*control:* `eval_report.py`
extendido y diff del CI).

### Fase 6 — Volver a NG

Usar el tap en `ng-distribuidora` por symlink, reemplazar sus copias de las guardas por
las del tap donde sean iguales, y medir con el benchmark de la fase 5 sobre exports
reales anonimizados. Cierra el ciclo: el proyecto que originó las reglas valida su
versión portable.

**Criterio:** 6.1 NG corre las guardas del tap sin regresiones (*control:* su
`ng.py validar` contra la línea base).

## 4. Lo que NO vamos a hacer

- Sumar skills nuevas antes de que las 7 actuales discriminen en las evals (fase 1).
- Un marketplace propio o un instalador propio: el valor vive en el contenido y los
  checks, no en el mecanismo (lección de superpowers).
- Traducir todo al inglés: las descripciones sí, el cuerpo en español es el diferencial.

## 5. Orden y tamaño

| Fase | Tamaño | Depende de | Por qué en este orden |
|---|---|---|---|
| 0 | chico | — | Lo hecho tiene que estar en `main` |
| 1 | mediano | 0 | Sin medición que discrimine, todo lo demás es opinión |
| 3 | chico | 0 | Barato, y es la ventaja frente al mercado de skills |
| 2 | mediano | 1, 3 | Distribuir algo medido y seguro, no antes |
| 5 | grande | 1 | El diferencial del nicho; reutiliza el método de evals |
| 4 | grande | 2, 3 | Empaqueta todo lo anterior |
| 6 | mediano | 5 | Valida en el proyecto real |

Recomendación de arranque: **fase 1 y fase 3 en paralelo**. Son las que convierten lo
que hoy afirmamos ("sirve", "es seguro") en algo que un check prueba.
