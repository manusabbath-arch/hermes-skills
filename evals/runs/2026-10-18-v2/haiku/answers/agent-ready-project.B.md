## Pedido 1

El problema principal es `pytest | grep passed || exit 1`. El código de salida del pipeline es el de `grep`, no el de `pytest`. Si un test falla pero la salida contiene la palabra "passed" (por ejemplo "1 failed, 40 passed"), `grep` devuelve 0 y el CI queda en verde. Además, `bandit ... || true` hace que el paso nunca falle, aunque haya hallazgos.

Lo que dejaría listo para agentes:

- Reemplazar el paso de tests por `pytest` a secas. Su código de salida ya sirve. Si hace falta un resumen, usar `pytest --junitxml=reports/junit.xml` como artefacto.
- Quitar `|| true` de bandit. Para no bloquear por deuda existente, usar `bandit -r src -ll` (solo severidad media y alta) y un archivo de baseline con los hallazgos actuales, de modo que falle solo ante hallazgos nuevos.
- Mover los pasos a un script único, por ejemplo `scripts/ci.sh` con `set -euo pipefail`, que el CI invoque. Así un agente puede correr exactamente lo mismo que el CI con un solo comando.
- Agregar un comentario corto en el YAML del CI explicando por qué cada paso falla o no, para que un agente no lo "arregle" quitando una validación.

Supuesto: no tengo el archivo de CI a mano, así que describo el cambio en general. Lo aplicaría sobre el archivo real antes de tocarlo.

## Pedido 2

No hace falta arreglar las 180 violaciones para activar el check. Lo haría así:

1. Generar un baseline con las violaciones actuales y commitearlo.
2. Configurar el check para que falle solo ante violaciones nuevas. Si la herramienta no trae baseline nativo, se compara el conteo o la lista de violaciones contra el snapshot.
3. Excluir de momento los archivos o reglas más ruidosas con `per-file-ignores` o una lista explícita, y documentar la deuda.
4. Aplicar primero el autofix de las reglas seguras (por ejemplo imports sin usar o formato) en un PR aparte, que es fácil de revisar.
5. Subir el umbral por etapas: cada PR que toque un archivo debe dejarlo más limpio (regla de "boy scout"), y el baseline solo puede achicarse, nunca crecer.

Así el check queda activo hoy y la deuda baja sin frenar el trabajo.

## Pedido 3

Lo organizaría con tres reglas:

- Una rama y un worktree por agente (`git worktree add ../repo-hermes hermes/tarea-x`). Nadie edita el mismo checkout a la vez.
- Ownership de tareas: cada tarea se asigna en un issue o en un tablero con un único responsable, y cada agente declara los paths que toca. Si dos tareas tocan el mismo archivo, se secuencian.
- Un solo archivo de instrucciones compartido, por ejemplo `AGENTS.md`, con las reglas del repo (no pushear a main, no tocar la configuración de CI sin aprobación, correr `scripts/ci.sh` antes de abrir un PR). `CLAUDE.md` puede simplemente apuntar a ese archivo, y lo mismo para Hermes y OpenCode si leen otro nombre.

Además: PRs chicos, rebase sobre main antes de mergear, y el CI como única puerta de merge. Nadie mergea su propio PR sin revisión humana.

## Pedido 4

El fallo es que el validador acepta un directorio inexistente o vacío y lo reporta como éxito. Cambiaría tres cosas:

- Que falle si el path no existe o si escanea 0 archivos. Es el cambio más importante.
- Que imprima cuántos archivos revisó ("0 problemas en 0 archivos" debería verse como alarma, no como éxito). Se puede agregar un mínimo esperado de archivos.
- Que la ruta esté en un solo lugar (una constante o un archivo de configuración) y que un test verifique que el validador detecta un fixture con errores conocidos. Así un "pasa siempre" se rompe en el CI.

Opcionalmente, agregar un check en CI que falle si cambia el número de archivos escaneados de forma abrupta.

## Pedido 5

No. "PR creado y tests en verde" es una afirmación del subagente, no evidencia. Antes de darlo por terminado verificaría:

- Que el PR existe, apunta a la rama correcta y su diff hace solo lo pedido.
- Que los checks de CI están en verde en el PR, mirando la página de checks, no el texto del reporte.
- Que los tests corridos son los correctos: que no haya tests salteados (`skip`, `xfail`) nuevos que escondan el problema, y que el comando del CI sea el que realmente valida (ver pedidos 1 y 4).
- Que no haya cambios fuera del alcance, sobre todo en CI, configuración o archivos de otros agentes.

Recién con eso lo daría por terminado. Si algo no cierra, le pediría al subagente la salida exacta del comando que corrió.

## Pedido 6

La forma más segura es usar una herramienta de refactor en lugar de buscar y reemplazar:

- En VS Code o PyCharm, posicionarse sobre la variable y usar "Rename Symbol" (F2) o "Refactor > Rename". Entiende el alcance y no toca strings ni atributos con el mismo nombre.
- Sin IDE, `rope` o `libcst` hacen el renombre por scope.

Si lo hacés a mano, con `sed` o buscar y reemplazar hay riesgos: puede cambiar otra variable con el mismo nombre en otra función, strings, o atributos como `obj.nombre`. Si usás `sed`, limitalo al rango de líneas de la función y usá `\b` para los límites de palabra, y revisá el diff.

Después del cambio, correr `pytest` y `pyflakes` o `ruff check` para confirmar que no quedó ninguna referencia al nombre viejo.
