## Pedido 1

No tengo el repo adjunto, así que declaro el supuesto de que el CI es un workflow de GitHub Actions con un paso `pytest | grep passed || exit 1` y otro de bandit con `|| true`. Qué haría:

**Problemas**
- `pytest | grep passed`: sin `pipefail`, el código de salida es el de `grep`. Si hay tests fallidos pero aparece la palabra "passed" en el resumen ("3 failed, 40 passed"), el paso queda en verde. Además, si pytest no recolecta nada, o falla al importar, el resultado es ambiguo.
- `bandit || true`: el paso nunca falla, así que es decorativo. Un agente que introduce un hallazgo de seguridad no recibe ninguna señal.

**Cambios**
1. Correr `pytest -q --maxfail=20` directamente, sin pipe, y que el código de salida decida. Agregar `--strict-markers` y exigir un mínimo de tests recolectados (por ejemplo, fallar si recolecta 0).
2. Bandit sin `|| true`. Si hoy hay hallazgos, congelar una línea base (`bandit -r src -b baseline.json`) o usar `-ll` para fallar solo en severidad media o alta. Así lo nuevo bloquea y lo viejo queda registrado.
3. Si hace falta un pipe, `set -o pipefail`.
4. Un único comando local, por ejemplo `make check`, que corra lo mismo que el CI, para que los agentes verifiquen antes de pushear.
5. Un `AGENTS.md` corto con: cómo correr tests y lint, qué checks son obligatorios, qué no tocar (no editar el CI para volver un check más laxo sin aprobación humana) y cuál es la definición de "terminado".
6. Proteger la rama principal con checks requeridos y revisión humana sobre cambios en `.github/workflows`.

Con eso el CI dice la verdad y los agentes tienen reglas explícitas.

## Pedido 2

Lo que hay que evitar es apagar el check o ignorar todo. La estrategia es **bloquear lo nuevo y tolerar lo viejo, con deuda visible**.

1. **Baseline**: generar un archivo con las 180 violaciones actuales. Según la herramienta: `ruff --add-noqa`, `--baseline` en pylint/flake8-baseline, o un script que guarde las violaciones por archivo y regla.
2. **Prender el check en el CI** comparando contra la línea base: falla si aparece una violación que no está en ella. El código nuevo queda limpio desde hoy.
3. **Alternativa**: activar la regla solo sobre archivos modificados en el PR (`git diff --name-only origin/main`).
4. **Ratchet**: el número de violaciones solo puede bajar. El CI falla si el conteo sube y se actualiza la línea base cuando baja.
5. **Pagar la deuda de a poco**: un issue o tarea por módulo, o un lote automático con `--fix` revisado aparte. Un agente puede encargarse, en PRs chicos y separados de cambios funcionales.
6. **No usar `# noqa` masivo sin motivo**. Si se usa, que lleve el nombre de la regla y quede contado.

Supuesto: no sé qué linter es. El principio es el mismo con cualquiera. Lo importante es que el check falle de verdad ante lo nuevo, de lo contrario nadie lo toma en serio.

## Pedido 3

Para que tres agentes trabajen a la vez sin pisarse:

1. **Aislamiento físico**: cada agente en su propio `git worktree` (o clon) y su propia rama (`claude/…`, `hermes/…`, `opencode/…`). Nunca dos agentes en el mismo directorio de trabajo.
2. **Partición por área**: asignar propiedad de directorios o módulos. Los archivos compartidos (lockfiles, configuración, CI, migraciones, `__init__`) los toca un solo agente, o se coordinan por humano.
3. **Tareas chicas e independientes**: un issue por agente, con alcance y criterio de terminado explícitos. PRs cortos que se integran seguido, para limitar el conflicto.
4. **Un archivo común de reglas** (`AGENTS.md`, que los tres puedan leer; Claude Code puede tener un `CLAUDE.md` que apunte a él): comandos de test y lint, convenciones, qué está prohibido tocar, formato de commits y de reporte.
5. **Registro de trabajo en curso**: un `TASKS.md` o issues con asignado, para que cada agente declare qué archivos va a tocar antes de empezar.
6. **El CI como árbitro**: los checks obligatorios en cada PR, rama principal protegida, merge solo con CI en verde. Rebase sobre `main` antes de abrir el PR.
7. **Un humano (o un único agente integrador) hace los merges**, en orden, y resuelve conflictos.
8. Puertos, bases de datos y archivos temporales por agente, para que las pruebas no choquen entre sí.

## Pedido 4

El problema es que "0 problemas" puede significar "no escaneé nada". El check no distingue entre "limpio" y "vacío". Cambios:

1. **Fallar si el objetivo no existe o está vacío**: si el directorio no existe, error y salida distinta de cero. No tratar la ausencia como éxito.
2. **Exigir un mínimo de elementos escaneados** e imprimir el conteo: "Escaneados 214 archivos, 0 problemas". Si el conteo es 0 o cae por debajo de un piso configurado, falla.
3. **Declarar el objetivo en un solo lugar** (config o constante) y que tanto el check como el código que renombra ese directorio dependan de eso. Un test que verifique que la ruta existe.
4. **Probar el propio check con un caso conocido malo**: un fixture con una violación deliberada que el check tiene que detectar. Si el check deja de encontrarla, el check está roto. Así se detectan los falsos verdes.
5. **Salidas distintas**: 0 = limpio, 1 = hay problemas, 2 = error de uso o configuración (ruta no encontrada).
6. **Alertar sobre la deriva**: en el CI, comparar el conteo escaneado con el de la corrida anterior y avisar si cambia mucho.
7. Añadir la regla al `AGENTS.md`: renombrar rutas obliga a actualizar los checks que las usan.

Supuesto: `validar` es un script propio, por lo que se puede modificar directamente.

## Pedido 5

No todavía. "PR creado y tests en verde" es una afirmación del subagente, no una evidencia. Antes de darlo por terminado, verificaría:

1. **Que el PR exista de verdad**: abrir el enlace, revisar que apunte a la rama y al repo correctos y que tenga los commits esperados.
2. **Que el CI en verde sea el del PR**, no un run local. Mirar los checks en GitHub, que incluyan todos los obligatorios y que ninguno esté omitido o saltado.
3. **Qué corrieron los tests**: cuántos, y si hubo tests nuevos para el cambio. Un verde con cero tests recolectados no vale.
4. **Leer el diff**. Confirmar que hace lo pedido y nada más, y que el agente no debilitó tests, no agregó `skip`/`xfail`, ni relajó el CI para ponerlo en verde.
5. **Probar el comportamiento si es posible**: correr el cambio, no solo los tests.
6. **Revisión humana** antes del merge si el cambio es relevante.

Si el subagente mostró el comando exacto y su salida, o el enlace al run de CI, la verificación es rápida. Si solo dijo la frase, trataría el reporte como una hipótesis. Mi regla: "terminado" significa que yo (o el CI) lo comprobé, no que alguien lo afirmó.

## Pedido 6

Depende de cómo lo hagas, pero en general:

- **En un editor/IDE** (VS Code, PyCharm): poner el cursor sobre la variable y usar "Rename Symbol" (F2 en VS Code, Shift+F6 en PyCharm). Cambia todas las referencias dentro del alcance y no toca otras variables con el mismo nombre en otras funciones.
- **A mano**: reemplazar el nombre solo dentro de esa función. Con buscar y reemplazar global te arriesgás a cambiar otras variables de igual nombre, así que limitá la búsqueda a las líneas de la función y activá "palabra completa".
- **Con herramienta**: la librería `rope` o `jedi` permiten renombrar con seguridad desde código.

Después, correr los tests para confirmar que nada se rompió. Si la variable aparece en strings, f-strings o `locals()`, revisá esos casos aparte.
