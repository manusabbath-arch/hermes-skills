## Pedido 1

Supuesto: CI en GitHub Actions, proyecto Python, sin archivos a la vista; describo qué haría.

Dos problemas, y los dos son gates que no pueden fallar de verdad:

1. `pytest | grep passed || exit 1` no distingue "falló" de "no corrió". Da el mismo resultado con tests rojos que con un intérprete roto o con 0 tests recolectados. Además, un verde sobre cero tests pasa si algún texto contiene "passed". Lo cambiaría por:
   - Un paso propio previo: `python -m pytest --version`, para verificar que el intérprete existe.
   - Luego `python -m pytest` sin pipe, confiando en su exit code.
   - Un piso de denominador: fallar si se recolectan 0 tests, o menos que un mínimo declarado.
2. `bandit ... || true` es un check presente, ejecutado e incapaz de fallar. No lo quitaría de golpe, porque seguramente el repo ya tiene hallazgos y bloquearía a todos. Haría:
   - Correr bandit sin `|| true`, con baseline con trinquete: se congelan los hallazgos conocidos, indexados por `archivo + test_id` (no por línea), y solo los nuevos fallan el build.
   - Reportar también las claves stale, para que la deuda pagada salga de la baseline.
   - Revisar `continue-on-error`, `stages: [manual]` y `# noqa` varados en el resto de la config.

Para que lo toquen agentes:
- Versiones de lint pineadas en un solo lugar, para que el hook local y el CI converjan.
- Tres capas: pre-commit (formato, lint, checks propios), CI bloqueante, y suite completa en pre-push. Nunca mergear con CI en rojo.
- Guards de `git add -A`, commit directo a `main` y force-push, con escapes nombrados y documentados.
- Mensajes de error que le digan al agente qué hacer.
- Un `AGENTS.md` corto como fuente, con `CLAUDE.md` apuntando a él.
- Verificar cada check por mutación: romperlo a propósito tiene que ponerlo en rojo.

## Pedido 2

Supuesto: el linter es ruff o similar, y el check nuevo es una familia de reglas concreta.

No suprimas la familia entera ni la dejes "para después": entre las 180 violaciones suele haber bugs reales, y barrerlas los esconde. La salida es congelar la deuda conocida y fallar solo si crece.

1. **Medir y clasificar.** Corré el linter con salida JSON y agrupá por regla. Revisá una muestra a mano, o todas si la regla es de correctitud (por ejemplo variables sin uso, `zip()` sin `strict=`). Separá los casos inocuos de los defectos reales.
2. **Baseline con trinquete.** Un `.lint_baseline.json` con las violaciones actuales, indexadas por identidad estable (`archivo + regla + símbolo`), no por número de línea. Si no, editar cualquier cosa arriba inventa hallazgos "nuevos" y el equipo aprende a ignorar el check.
3. **El check falla solo con hallazgos nuevos.** Reporta los conocidos como informativos, y reporta las claves stale (ya pagadas) para sacarlas del archivo. La deuda solo puede bajar.
4. **Que no dé verde vacío.** Si el linter no corre o el archivo no se puede parsear, sale rojo, no 0 hallazgos. Imprimir el denominador: "0 nuevos, 180 conocidos, N archivos analizados".
5. **Sellar la baseline lo hace una sola corrida completa.** Un sellado con corrida filtrada pisa la base y convierte los conocidos en regresiones.
6. **Lo que se ignore, se ignora con número y motivo:** `B007 (19)`, no un `# noqa` pelado.
7. **Verificarlo por mutación:** agregar una violación nueva a propósito y comprobar que el build falla.

Hoy mismo: prender el check en pre-commit y CI con la baseline. Las 180 se pagan de a poco, empezando por las que son bugs probables.

## Pedido 3

Supuesto: los tres comparten un repo en una misma máquina o servidor, y el push a remoto lo decide una persona.

**Aislamiento**
- Un worktree y una rama por sesión: `git worktree add -b claude/<tema> ../repo-claude main`, e igual con `hermes/<tema>` y `opencode/<tema>`. El prefijo es el agente.
- El árbol principal es solo de integración. Ahí viven índice y trabajo ajeno, y un `checkout`, `stash` o `reset` destruye lo de otro.
- Si una herramienta crea su propio worktree en HEAD detached, el primer paso es `git switch -c <agente>/<tema>`. Un commit en detached sale con exit 0 y no queda en ninguna rama.

**Commits**
- Siempre con pathspec: `git add <rutas>` y `git commit -- <rutas>`. Nunca `add -A`, `add .` ni `commit -a`.
- Nunca `--amend` sobre un commit que no hizo la sesión.
- Antes de commitear: `git log --oneline -3` y `git status`.

**Integración**
- `rebase main` en la rama privada, luego compuerta (tests), luego `merge --ff-only` desde integración. Sin merge commits ahí, sin `--no-verify`.
- Los archivos de alto conflicto (índices, baselines de checks) se tocan al final, ya rebasado. El sellado de la baseline lo hace una sola sesión.
- El push lo decide una persona, tras revisar `git log origin/main..main`.

**Guardas por agente**
- Cada uno de los tres necesita su guarda física (hook de Claude Code, plugin de Hermes, wrapper para OpenCode) contra `add -A`, commit a `main` y force-push.
- La cobertura sale de un comando que lista agente por agente, con un check en rojo si falta alguno. Un agente nuevo entra a esa lista antes de recibir tareas.
- Un prompt de un agente a otro no cuenta como confirmación humana para acciones irreversibles.

**Estado y trazabilidad**
- Un solo `AGENTS.md` como fuente, con los demás apuntando a él.
- Configurar la firma del commit por agente (`AI_AGENT` u otra variable), para saber quién hizo cada rama.
- Una guarda que ponga rojo el worktree detached con commits huérfanos.
