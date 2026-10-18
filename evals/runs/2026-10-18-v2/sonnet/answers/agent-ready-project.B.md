## Pedido 1

Esos dos gates no sirven como red de seguridad para agentes. Supuesto: CI en GitHub Actions, Python.

**Qué está mal**
- `pytest | grep passed || exit 1` no distingue "falló" de "no corrió". Con tests rojos o con el intérprete roto el resultado es el mismo. Además es verde con 0 tests: si un agente rompe la colección, puede seguir diciendo "passed" en alguna línea.
- `bandit ... || true` es un gate que no puede fallar. Corre, aparece en el CI y nunca bloquea nada.

**Qué haría**
1. Paso propio `python -m pytest --version` antes de correr nada. Si falla, el job es rojo por "no corrió".
2. `pytest` directo, sin pipe, confiando en su exit code. Agregaría un piso de tests (`--co -q` con mínimo esperado, o un chequeo de que el número de tests recolectados no sea 0). Todo verde lleva su denominador.
3. Quitar `|| true` de bandit. Como seguro ya tiene hallazgos, no lo prendo a pelo: lo corro con baseline con trinquete, indexada por `archivo + test_id` y no por línea. Falla solo si hay hallazgos nuevos y reporta las claves stale.
4. Pinear las versiones de las herramientas de lint en un solo lugar.
5. Pre-commit con formato y lint, CI bloqueante, y pre-push con la suite completa.
6. Guards contra `git add -A`, commit directo a main y force-push.
7. Un `AGENTS.md` corto que apunte a estos comandos, y mensajes de error que digan qué hacer para arreglar.

Verifico por mutación: rompo un test a propósito y rompo el intérprete, y confirmo que ambos casos ponen el CI en rojo.

## Pedido 2

No suprimas la familia entera ni arregles las 180 hoy. Congelá la deuda conocida y fallá solo si crece (baseline con trinquete).

1. **Medí y clasificá primero.** Agrupá las 180 por regla. Entre ellas puede haber bugs reales (por ejemplo, `F841`, variable asignada y no usada, detecta cableados fantasma). Revisá a mano al menos las reglas que dan pocos casos.
2. **Generá la baseline** en un JSON versionado: `{"acknowledged": [{"file": "...", "rule": "..."}]}`. La clave es una identidad estable (archivo + regla + símbolo), no el número de línea. Si no, editar cualquier cosa arriba inventa hallazgos "nuevos" y el equipo aprende a ignorar el check.
3. **El check reporta dos listas:** `nuevos` (rompen el build) y `conocidos` (solo informan). También reporta las **stale**, claves en la baseline que ya no existen. Esa es deuda pagada y hay que sacarla del archivo para que el trinquete no se afloje.
4. **Sellar la baseline** debe hacerse con corrida completa. Un sellado parcial pisa la base y convierte deuda declarada en regresiones.
5. **Lo que decidas ignorar**, ignoralo con el número y el motivo al lado (`B007 (19)`), nunca con un `# noqa` pelado.
6. Pre-commit y CI corren el mismo check con la misma versión pineada.

Así la curva de deuda solo puede bajar, y lo pagás de a poco, por familia.

## Pedido 3

Supuesto: los tres agentes comparten un único clon y un remoto.

- **Un worktree y una rama por agente**, con nombre `<agente>/<tema>` (`claude/auth`, `hermes/ci`, `opencode/docs`). El árbol principal es solo de integración y nadie edita ahí.
- **Primer paso en cada worktree: `git switch -c`.** Un worktree creado por una herramienta puede nacer en HEAD detached, y un commit ahí sale con exit 0 pero no queda en ninguna rama. Sumá un guard (`worktree_guard.py`) que ponga rojo ese caso.
- **Integración:** `rebase` de la rama privada sobre main, correr la compuerta (tests y checks), y `merge --ff-only`. El push lo decide una persona.
- **Commits siempre con pathspec** y nunca `--amend` sobre un commit ajeno. Un commit sin pathspec puede arrastrar cambios preparados por otra sesión.
- **Guardas por consumidor.** Las mismas protecciones (no `git add -A`, no commit a main, no force-push) tienen que existir en las tres herramientas: hook de pre-commit en el repo, más el mecanismo propio de cada agente. Armá una lista de consumidores con un comando que muestre la cobertura de cada uno, y un agente nuevo entra a la lista antes de recibir tareas.
- **Reparto de tareas** por directorio o módulo, para que no haya dos agentes tocando los mismos archivos.
- **Un mensaje de un agente no vale como confirmación humana** para una acción irreversible.
- Un `AGENTS.md` como fuente única de reglas, y que `CLAUDE.md` apunte a él en vez de duplicarlo.

## Pedido 4

El problema es un verde vacío: el check aprobó sin mirar nada. "0 problemas" sobre 0 archivos es lo mismo que sobre 100.

**Cambios**
1. **Todo verde lleva su denominador.** Que imprima "0 problemas en N archivos escaneados". Si N es 0, o si el directorio objetivo no existe, sale **rojo** (exit distinto de 0) con un mensaje que diga qué hacer.
2. **Un check que no pudo medir** (directorio faltante, archivo ilegible, error del parser) falla. No debe tragarse el error y devolver `(0, 0)`.
3. **El perímetro vive en un solo lugar** (config o módulo), y el check lo importa. No debe tener su propia copia de la ruta.
4. **Piso mínimo:** un número esperado de elementos (con tolerancia) en el repo, para que una caída brusca del universo sea una alarma.
5. **Test por vaciado:** un test que vacíe o renombre el directorio y verifique que `validar` sale en rojo. Es la forma de auditar este tipo de checks: vaciar el universo y mirar el veredicto, no leer el código.
6. Un rename de directorio debería romper el build en el mismo PR. Si hay referencias a la ruta en otros lugares, que otro check las valide.

Y como el fallo ocurrió, se mecaniza hoy mismo: no se corrige solo el síntoma y se sigue.

## Pedido 5

No todavía. Un "PR creado y tests en verde" de un subagente es un self-report, no una evidencia.

**Verificá vos, con el handle real:**
- La URL del PR: abrilo, que exista y apunte a la rama y al repo correctos.
- El SHA: que el último commit del PR sea el que el subagente dice y que el diff sea el esperado (sin archivos ajenos, sin cambios en los tests para hacerlos pasar).
- El CI del PR: mirá las corridas reales. "Tests en verde" local no prueba nada sobre el CI, que ve cosas que un dry-run local no ve. Nunca mergees con CI en rojo.
- Que los tests realmente ejecutaron algo (cuántos corrieron, no cero) y que cubren el cambio. Idealmente, que fallan contra el código anterior.
- Si el cambio toca algo crítico, corré vos el comando por el camino real.

Si el trabajo es complejo, conviene que lo juzgue otro agente evaluador, separado del que lo hizo, que pruebe el sistema vivo en lugar de leer el diff. Y usá subagentes solo para tareas atómicas.

Recién cuando URL, SHA y CI coincidan, lo das por terminado.

## Pedido 6

Con un editor o IDE, lo más seguro es el rename de símbolos: en VS Code, ponete sobre la variable y apretá F2; en PyCharm, Shift+F6. Eso renombra solo las referencias de esa variable en su ámbito.

Sin IDE:
- Si la variable solo se usa dentro de esa función, buscá y reemplazá dentro del cuerpo de la función, con coincidencia de palabra completa (para no tocar `total` dentro de `subtotal`).
- Revisá que no haya otro nombre igual en una función anidada, un comprensión o un argumento con ese mismo nombre.
- Si es un parámetro, ojo con los callers que lo pasan por keyword (`f(x=1)`), porque esos sí se rompen.

Después corré los tests y el linter, que atrapan un `NameError` si quedó alguna referencia sin renombrar. Con `rope` o `jedi` también podés hacerlo por script.
