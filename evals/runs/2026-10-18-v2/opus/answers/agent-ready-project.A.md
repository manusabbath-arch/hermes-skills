## Pedido 1

Las dos líneas mienten sobre el resultado, y un agente que lea el CI va a creer que todo anda bien.

- `pytest | grep passed || exit 1`: el pipe se queda con el código de salida de `grep`, no el de pytest. Si hay "3 failed, 10 passed", `grep` encuentra "passed" y el CI pasa en verde. Tampoco hay `set -o pipefail`.
- `bandit ... || true`: bandit nunca puede hacer fallar el build. Es puro decorado.

Lo que cambiaría (supuesto: GitHub Actions o un shell script):

```bash
set -euo pipefail
pytest -q --junitxml=reports/pytest.xml
bandit -r src -c pyproject.toml --severity-level medium -f json -o reports/bandit.json
```

- pytest sin pipe: su código de salida es la verdad (sale distinto de 0 si falla, y también si no junta ningún test, el código 5).
- bandit bloqueante, con las excepciones aceptadas explícitas en la configuración (`skips` o `# nosec` con justificación), no con `|| true`. Si hoy tiene hallazgos, usá un baseline (`bandit -b baseline.json`) para que solo fallen los nuevos.
- Un único comando de entrada (`make check` o `scripts/check.sh`) que corra lo mismo en local y en CI, documentado en `AGENTS.md`/`CLAUDE.md`, para que el agente se valide antes de pushear.
- Salidas legibles por máquina (junit, json) para que el agente diagnostique sin adivinar.
- Para probarlo: rompé a propósito un test y meté un `eval()` en una rama; el CI tiene que ponerse en rojo en los dos casos.

## Pedido 2

Activalo ya, pero solo para lo nuevo: el ratchet (trinquete).

1. **Baseline**: registrá las 180 violaciones actuales en un archivo versionado. Según la herramienta: `ruff --add-noqa` (agrega `# noqa` en cada línea), baseline de flake8/pylint, o un script que guarde la lista (archivo + regla + hash de la línea, no el número de línea, que se mueve).
2. **CI bloqueante para lo nuevo**: el check falla si aparece una violación que no está en el baseline. No pongas `|| true` ni "solo warning": un aviso que no falla se ignora, sobre todo si quien lee es un agente.
3. **El baseline solo baja**: el CI también falla si el número crece; cuando alguien arregla algunas, se regenera y el nuevo número queda como techo. Un test que compare el conteo contra un valor fijado (`<= 180`) sirve.
4. **Arreglá lo automático hoy**: muchas reglas tienen autofix (`ruff --fix`). Corrélo en un PR separado, solo con ese cambio, para que la revisión sea fácil; seguramente bajás bastante de 180.
5. **El resto, por partes**: por directorio o por regla, en PRs chicos. Es una buena tarea para delegar a agentes, con la consigna "baja el baseline sin cambiar comportamiento, los tests tienen que seguir verdes".

Documentá en el README/AGENTS.md que existe el baseline y que no se debe agregar nada a mano para "pasar el CI".

## Pedido 3

La regla de base: cada agente en su propio espacio de trabajo, con tareas que no se superpongan, y la integración pasa solo por PRs.

- **Aislamiento**: un `git worktree` (o clon) y una rama por agente: `agent/claude/<tarea>`, `agent/hermes/<tarea>`, `agent/opencode/<tarea>`. Nunca dos en el mismo directorio de trabajo: se pisan archivos sin commitear, locks y caches.
- **Reparto por tareas, no por "lo que encuentren"**: un issue por tarea con dueño explícito (label o asignación). Repartí por zonas del código que no se toquen; si dos tareas tocan el mismo módulo, que vayan en serie.
- **Archivos calientes**: lockfiles, migraciones, configuración de CI y archivos de versión los toca un solo agente o un humano. Las migraciones numeradas son el clásico conflicto: asignalas.
- **Instrucciones compartidas**: un solo `AGENTS.md` como fuente de verdad (comandos de test, convenciones, qué no tocar); `CLAUDE.md` y lo que lea cada herramienta apuntan ahí, en vez de tres copias que divergen.
- **Recursos de runtime**: puertos, bases de datos de test y directorios temporales parametrizados por agente (variable de entorno), para que los tests no choquen.
- **Gate común**: el mismo `make check` en CI para todos, protección de rama en `main`, merge solo con CI verde y rebase sobre `main` antes de mergear. PRs chicos para que los conflictos sean baratos.
- **Coordinación**: un humano (o un agente orquestador) mergea; ningún agente pushea a `main` ni a la rama de otro.

## Pedido 4

El problema es que "0 problemas" no distingue entre "revisé todo y está limpio" y "no revisé nada". Hay que hacer que el check falle si no revisó nada.

1. **Fallar si no hay entrada**: si el directorio no existe o no hay archivos que coincidan, salir con un código distinto de 0 y con un mensaje claro ("directorio X no existe" o "0 archivos escaneados").
2. **Reportar cobertura, no solo resultado**: `escaneados 412 archivos en src/datos, 0 problemas`. Con eso cualquiera, humano o agente, ve el cambio de 412 a 0.
3. **Piso mínimo**: si es razonable, `--min-files N` o comparar contra la cantidad esperada; una caída brusca es un error.
4. **Ruta desde una única configuración** (pyproject o config del check), no hardcodeada en el script, y que el renombre de ese directorio rompa algo visible.
5. **Test del propio check**: un fixture con un problema conocido que el check tiene que detectar (canario). Si un día pasa en verde, el check está roto. También un test de que con un directorio vacío o inexistente falla.
6. **Sin `|| true` ni pipes** que escondan el código de salida en el CI.

Y revisá el historial: corré el check con la ruta correcta sobre el estado actual, porque en esas semanas pueden haber entrado problemas reales que nadie vio.

## Pedido 5

Todavía no. Es un reporte, no una evidencia. Antes de cerrarlo, verificá vos (dos minutos):

- **El PR existe y es el correcto**: abrí el link o `gh pr view <n>`. Fijate la rama base, que el diff contenga lo pedido y nada extra (archivos que no corresponden, tests borrados o marcados como `skip`, umbrales bajados, `|| true` agregados).
- **"Tests en verde", ¿dónde?**: lo que vale es el CI del PR (`gh pr checks <n>`), sobre el último commit. "Pasaron en local" o "corrí un subconjunto" no es lo mismo. Revisá que los checks hayan corrido de verdad (no "skipped" ni pendientes) y que la cantidad de tests se parezca a la habitual.
- **¿Cubre lo pedido?**: comparalo contra el criterio de aceptación original. Que haya tests que ejerciten el cambio, no solo que los viejos sigan pasando.
- **Pendientes**: comentarios de revisión, conflictos con `main`, cosas que el subagente haya dejado como TODO.

Si todo cierra, sí, está listo para revisión/merge. Si algo no cierra, devolvelo con el punto concreto. Para la próxima, pedile al subagente que el reporte incluya el link del PR, el link de la corrida del CI y el resumen de tests (X passed, 0 failed, 0 skipped) para que la verificación sea inmediata.

## Pedido 6

Cambiá el nombre en la asignación y en cada uso dentro de esa función. Como es local, no afecta nada afuera.

La forma más segura es usar el "rename" del editor, que entiende el código y no reemplaza texto a ciegas:
- VS Code (Pylance): cursor sobre la variable y **F2**.
- PyCharm: **Shift+F6**.

A mano también sirve, pero ojo con:
- No pisar otro nombre que ya exista en la función.
- Funciones anidadas o closures que la usen (`nonlocal`).
- Strings o f-strings que la mencionen (`f"{viejo}"`): el rename del IDE las detecta, buscar/reemplazar puede no hacerlo o tocar de más.

Después corré los tests o el linter para confirmar que no quedó ningún uso con el nombre viejo (aparece como `NameError` o `F821`).
