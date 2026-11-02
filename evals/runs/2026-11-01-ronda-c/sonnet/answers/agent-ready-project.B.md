## Pedido 1

No los bajaría a warning en bloque. Tampoco dejaría el rojo como está. Un warning que nadie mira es la misma enfermedad con otro color: los 5 o 6 rojos fijos ya le enseñaron al equipo a ignorar la compuerta, y cuando aparezca un defecto real va a entrar a esa lista sin que nadie lo note.

Lo que haría:

1. **Separar los rojos por tipo.** "Faltan datos" no es lo mismo que "el chequeo encontró un defecto". Si el dato falta, el chequeo no pudo medir. Eso debe salir como `ERROR` o rojo explícito, nunca como `PASS` ni como un warning que se pierde. Y si lo que falta es algo que debería estar, el rojo es correcto, porque el chequeo pregunta "¿esto debería estar y no está?".
2. **Declarar cada rojo con motivo y condición de salida.** Por ejemplo: "falta el export X; sale cuando llegue el archivo del proveedor". Los declarados no bloquean y se imprimen en cada corrida, así quedan visibles sin frenar a todos. Un rojo declarado sin condición de salida se rechaza: eso es silenciarlo.
3. **Usar una línea base sellada.** La compuerta distingue tres casos:
   - Una regresión bloquea.
   - Un rojo nuevo, que no estaba en la base, bloquea.
   - Un rojo declarado se informa pero no bloquea.
   Así el equipo vuelve a ver rojo solo cuando algo cambió de verdad.
4. **Cuidado al sellar.** Sellá mezclando con la base existente, no reemplazándola. Una corrida filtrada o sin todas sus dependencias no se sella. Y que un chequeo desaparezca de la corrida también debe bloquear.
5. **Mostrar el estado de hoy junto al motivo.** El motivo declarado es una foto vieja. Imprimí el veredicto y el mensaje actuales encima, y avisá cuando el mensaje cambie.
6. **Revisar las condiciones de salida.** Cada rojo declarado necesita una fecha de revisión, y cuando el chequeo vuelva a verde hay que sacar la declaración.

Si algunos de los 5 o 6 son datos que realmente nunca van a llegar, el problema es el chequeo: o se elimina, o se redefine para que no dependa de ese dato. Bajarlo a warning solo esconde que está mal planteado.

## Pedido 2

No revertiría todavía. El patrón apunta a que no es tu commit: 300 fallos en archivos que no tocaste, todos con "no existe" y código 127. El 127 es "comando no encontrado" del shell. Eso suele indicar que algo del entorno no corrió (un intérprete, una herramienta o un PATH ausente), no que el código esté roto.

Un gate que no distingue "falló" de "no corrió" le echa la culpa a lo primero. Para separarlos:

1. **Verificá que la herramienta exista antes de leer los resultados.** Corré, como paso aparte, algo como `python -m pytest --version`, o el equivalente de tu runner. Mirá qué comando exacto devuelve 127 y si existe en tu PATH o en el venv activo.
2. **Comparalo contra el commit anterior en el mismo entorno.** Si ahí también salen los 300 fallos, tu commit es inocente. Podés hacerlo con un `git stash` o con un worktree separado en el commit previo. No hace falta revertir nada para probarlo.
3. **Mirá qué dice "no existe".** Si es un ejecutable, un script o una ruta, fijate si algún cambio de entorno lo movió: un venv desactivado, una dependencia que no se instaló, un cambio de shell o de directorio de trabajo.
4. **Revertí solo si el mismo entorno reproduce el fallo con tu commit y no sin él.**

Revertir ahora tiene un costo y, si la causa es el entorno, no arregla nada. Si me pegás el mensaje exacto de uno de esos fallos y el comando que corre la suite, te ayudo a ubicar la causa.

## Pedido 3

`git worktree add <ruta> [<rama>]` crea un directorio de trabajo adicional, vinculado al mismo repositorio. Cada worktree tiene su propia rama o HEAD, su propio índice y sus archivos, pero todos comparten el mismo historial y los mismos objetos de `.git`.

Sirve para tener dos ramas abiertas a la vez sin clonar ni hacer stash. Por ejemplo, podés arreglar un bug en una rama mientras tu trabajo en otra queda intacto.

Formas comunes:

- `git worktree add ../hotfix hotfix`: crea `../hotfix` con la rama existente `hotfix`.
- `git worktree add -b nueva-rama ../dir`: crea la rama `nueva-rama` desde HEAD y la saca en `../dir`.
- `git worktree add --detach ../dir <commit>`: lo crea en HEAD detached.

Dos cosas a tener en cuenta:

- Git no deja sacar la misma rama en dos worktrees a la vez.
- Si el worktree queda en HEAD detached, los commits ahí no pertenecen a ninguna rama. Conviene hacer `git switch -c <nombre>` antes de comitear.

Para listar los worktrees usá `git worktree list`, y para borrar uno, `git worktree remove <ruta>`.
