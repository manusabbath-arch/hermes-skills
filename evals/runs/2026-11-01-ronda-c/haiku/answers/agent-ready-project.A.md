## Pedido 1

No lo bajaría a warning. Un warning que el equipo ya ignora en rojo queda igual de ignorado, y el rojo permanente hace que el próximo defecto real pase sin que nadie lo note.

Lo que sí funciona es congelar los 5 o 6 rojos actuales como deuda conocida, con tres datos por cada uno: qué falta, por qué no se puede resolver hoy y cuál es la condición de salida con fecha (por ejemplo, "esperando el export de X, se resuelve antes del 2026-12-01"). La compuerta falla solo si aparece un rojo nuevo, y también si uno de los congelados se corrige y sigue figurando en la lista, porque así la lista solo puede achicarse.

Dos cosas más:

- **Datos faltantes no son lo mismo que chequeo sin datos.** Si el chequeo no pudo medir (archivo ausente, error al leerlo), tiene que salir en rojo y no en verde. Si nunca mira nada, el verde no significa nada.
- **Identificá cada chequeo congelado por su nombre y su objetivo, no por el número de línea**, para que editar otra cosa no haga aparecer rojos "nuevos".

## Pedido 2

No revertiría el commit todavía. El código 127 significa "comando no encontrado": el shell no encontró el ejecutable que corre la suite (el intérprete, el runner o una herramienta del entorno). Eso indica que la suite no llegó a ejecutar los tests, así que los 300 fallos no dicen nada sobre tu commit ni sobre los archivos que no tocaste.

Para confirmarlo:

1. Ejecutá el runner solo, por ejemplo `python -m pytest --version` (o el equivalente de tu proyecto). Si falla, el problema es el entorno: PATH, el entorno virtual o una herramienta no instalada.
2. Si el runner responde, mirá el primer error completo de la salida, no el resumen.
3. Para descartar el commit por completo, corré la suite sobre el commit anterior en un directorio aparte. Si ahí también aparecen los 300 con código 127, el commit es inocente y revertirlo solo deshace trabajo bueno.

Si el runner no está disponible, arreglá el entorno y volvé a correr la suite. Solo revisaría el commit si, después de eso, los fallos persisten y el diff toca algo que la suite usa, como configuración, rutas o dependencias.

## Pedido 3

`git worktree add` crea un directorio de trabajo nuevo, vinculado al mismo repositorio, en la ruta que indiques. Comparte historial, objetos y referencias con el repo original, pero tiene su propio índice y su propio estado de archivos, así que podés tener dos ramas abiertas a la vez sin clonar nada ni cambiar de rama en el directorio principal.

Formas comunes:

- `git worktree add ../rama-x feature/x`: crea el directorio y hace checkout de una rama existente.
- `git worktree add -b feature/y ../rama-y main`: crea una rama nueva a partir de `main` y la abre en ese directorio.
- `git worktree add --detach ../prueba <commit>`: abre un commit sin rama, útil para probar algo sin mover ninguna referencia.

Git no permite abrir la misma rama en dos worktrees a la vez. Para borrar un worktree usá `git worktree remove <ruta>`, y `git worktree list` muestra los que existen.
