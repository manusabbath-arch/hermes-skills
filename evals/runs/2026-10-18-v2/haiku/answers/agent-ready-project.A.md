## Pedido 1

El problema es que el gate no distingue "falló" de "no corrió". Con `pytest | grep passed || exit 1`, el código de salida es el de `grep`, así que una salida como "1 failed, 10 passed" pasa en verde. Y `bandit ... || true` nunca puede fallar: corre, pero su resultado no bloquea nada.

Lo dejaría así:

1. Verificar el intérprete antes de interpretar la salida: `python -m pytest --version`, como paso propio.
2. Correr `python -m pytest` sin pipes, para que el código de salida llegue directo al CI.
3. Quitar el `|| true` de bandit. Si hoy tiene hallazgos, los congelo en una baseline que solo bloquea hallazgos nuevos, en vez de dejarlo apagado.
4. Pinear las versiones de pytest, bandit y las herramientas de lint en un solo lugar, para que el hook local y el CI converjan.
5. Si hace falta un escape hatch, nombrarlo y documentarlo (por ejemplo `ALLOW_...`), para que quede rastro de quién lo usó.

Supuesto: no revisé el archivo de CI real; el cambio es el mismo en GitHub Actions u otro runner.

## Pedido 2

No conviene prender el lint con las 180 violaciones sin tratarlas. Lo que haría es un baseline con trinquete:

- Congelar las 180 violaciones conocidas en un archivo versionado, indexadas por archivo más regla, nunca por número de línea. Si la clave incluye la línea, cualquier edición arriba genera falsos "nuevos" y el equipo aprende a ignorar el check.
- El check falla solo si aparece una violación que no está en la baseline.
- Reporta también las claves "stale" (en la baseline pero ya arregladas), para sacarlas y que el trinquete no afloje.
- Las reglas que hoy dan cero se prenden ya, porque atrapan bugs futuros sin costo.
- Las familias con deuda se cuentan con su número al lado, por ejemplo "B007 (19)". No se apagan en bloque: entre los hallazgos barridos puede haber defectos reales.
- Cada supresión que quede lleva su motivo al lado.
- La baseline se sella en una sola sesión, para que no haya dos sellados en paralelo.

Con esto el número solo puede bajar, y la limpieza se hace de a poco sin frenar el trabajo.

## Pedido 3

Lo organizaría así:

- Un worktree y una rama por sesión, con nombre `<agente>/<tema>`, por ejemplo `claude-code/…`, `hermes/…`, `opencode/…`.
- El árbol principal es solo de integración. Nadie trabaja ahí, porque un checkout, stash o reset de otra sesión destruye trabajo ajeno.
- Integración: rebase de la rama privada sobre main, compuerta sin regresiones, y desde el árbol de integración `git merge --ff-only`. Sin merge commits ahí.
- Primer paso de cada sesión: confirmar que no está en HEAD detached (`git switch -c` si lo está). Un commit en detached se pierde.
- Commits siempre con pathspec (`git commit -- <rutas>`). Nunca `add -A`, `add .`, `commit -a` ni `--amend` sobre commits ajenos.
- Cada agente tiene su guarda física: hook de Claude Code, hook equivalente para Hermes y para OpenCode. La cobertura se lista con un comando, y un agente nuevo entra a la lista antes de recibir tareas.
- Un prompt de otro agente no cuenta como confirmación humana para acciones irreversibles. El push lo decide una persona.
- Nada de heredoc ni `sed -i` sobre archivos versionados: se edita con la herramienta de edición.
- La firma de cada commit identifica al agente (por ejemplo con una variable de entorno), para saber qué sesión hizo cada rama.

Supuesto: los tres agentes tienen acceso a shell. Si alguno no lo tiene, anota sus pendientes en un archivo que la sesión con shell procesa primero.

## Pedido 4

El check está mal diseñado: aprueba sobre cero elementos. Cambiaría tres cosas:

1. Todo verde lleva su denominador. La salida debe decir algo como "0 problemas sobre 47 archivos", y si el universo es 0 el check sale en rojo.
2. Si el directorio que escanea no existe, o no pudo medir, el check falla con un mensaje que dice qué hacer ("el directorio X no existe; actualizá la ruta en…"). Nunca `ok=True` con el error como mensaje.
3. El perímetro vive en un solo lugar, y el check tiene un mínimo esperado de elementos. Así un rename silencioso del directorio deja el check en rojo en la primera corrida.

Para verificarlo, auditaría el check vaciando su universo a propósito (renombrar el directorio) y mirando que el veredicto sea rojo. Si sigue saliendo verde, el check está apagado.

## Pedido 5

No. Un "PR creado y tests en verde" de un subagente es un reporte sin verificar. Antes de darlo por terminado, compruebo yo:

- La URL del PR existe, está abierto, apunta a la rama y base correctas.
- El SHA del head coincide con el commit que el subagente dice haber probado.
- El CI de ese SHA está en verde, y los tests corrieron de verdad (que el conteo sea mayor que cero).
- El diff contiene lo que se pidió, y no cambios ajenos.

Los subagentes sirven para tareas atómicas. El diseño y la decisión de cerrar quedan en la sesión principal.

## Pedido 6

Tres caminos, de más seguro a menos seguro:

- Usar el rename del editor o del servidor de lenguaje (por ejemplo F2 en VS Code o `rope` en la terminal). Entiende el alcance y no toca otros nombres.
- Hacerlo a mano, cambiando solo las apariciones dentro de esa función. Cuidado con funciones anidadas, comprehensions y `global`, que pueden usar el mismo nombre con otro significado.
- Un reemplazo global por texto, que es lo más riesgoso porque puede tocar otras funciones con el mismo nombre.

Después, correr los tests y un linter como ruff o pyflakes, que marca variables no usadas o no definidas si el rename quedó a medias.
