## Pedido 1

Yo no los bajaría a warning en bloque. El problema real no es la severidad de los chequeos. Es que la compuerta mezcla dos cosas distintas: "el código está mal" y "no tengo datos para evaluar". Mi sugerencia:

1. **Separá los estados.** Un chequeo sin datos no debería ser rojo (falla) ni verde (pasa). Tiene que ser un tercer estado, tipo "sin datos" o "omitido", visible pero que no bloquee. Así el rojo vuelve a significar algo real.
2. **Seguí los chequeos sin datos como deuda.** Poné un dueño y un plazo para cada uno, o un contador de cuántos llevan omitidos y desde cuándo. Si no, pasan de ignorados a olvidados.
3. **Bajá a warning solo lo que sea de verdad informativo.** Si un chequeo nunca va a tener datos o no te importa, sacalo. Si importa, arreglá el origen de los datos.
4. **Mantené el bloqueo para los chequeos críticos.** Si falta el dato de uno de esos, que siga fallando. No querés que un pipeline roto de datos deje pasar algo grave.

Bajar todo a warning resuelve el ruido de hoy, pero deja el mismo problema: dentro de unos meses el equipo va a ignorar también los warnings, y un rojo real se va a perder entre ellos.

## Pedido 2

Todavía no revertiría. Los síntomas apuntan a otra causa.

- **Código 127** en shell significa "comando no encontrado".
- **"No existe"** en 300 fallos, en archivos que no tocaste, sugiere que falta algo común a todos: un binario, una herramienta en el `PATH`, un script auxiliar o una variable de entorno.
- Un cambio tuyo que rompa 300 archivos sin tocarlos es posible, pero menos probable que un problema del entorno.

Para distinguirlo:

1. **Mirá el mensaje exacto** de un par de fallos. Fijate qué comando o archivo dice que no existe. Probablemente sea el mismo en todos.
2. **Corré ese comando a mano** en la misma terminal. Si tampoco lo encuentra, es del entorno: `PATH`, una dependencia sin instalar o una terminal distinta de la habitual.
3. **Probá sin tu commit.** Hacé `git stash` si tenés cambios sin commitear, y después `git checkout <commit anterior>` en un worktree o rama aparte. Corré la suite ahí. Si falla igual, tu commit no es el culpable. Si pasa, mirá qué agregó o borró tu commit: un archivo, un permiso ejecutable, o finales de línea CRLF en un script de shell. Este último es un clásico en Windows y da exactamente 127.
4. **Revisá si cambió algo del entorno:** una actualización, otra versión de la herramienta o un entorno virtual desactivado.

Si el paso 3 confirma que es tu commit, revertilo con `git revert`, que es seguro porque no reescribe la historia. Pero antes conviene saber qué lo rompió, para no repetirlo.

## Pedido 3

`git worktree add <ruta> [<rama>]` crea un **directorio de trabajo adicional** vinculado al mismo repositorio. Con eso podés tener varias ramas con el código desplegado al mismo tiempo, cada una en su carpeta, sin clonar de nuevo.

- Todos los worktrees comparten la misma base de objetos (`.git`), así que ocupa poco espacio y los commits se ven de inmediato en todos.
- Cada worktree tiene su propio `HEAD`, índice y archivos. Podés trabajar en uno sin tocar los demás.
- Una rama solo puede estar activa en un worktree a la vez.

Formas comunes:

```
git worktree add ../hotfix hotfix-rama       # usa una rama existente
git worktree add -b nueva-rama ../feature    # crea la rama y el worktree
git worktree add --detach ../prueba <commit> # HEAD suelto, sin rama
```

Sirve para atender un hotfix sin interrumpir lo que tenés a medias, para correr tests en otra rama mientras seguís trabajando, o para revisar un PR sin hacer stash.

Para limpiar: `git worktree list` los muestra, `git worktree remove <ruta>` elimina uno, y `git worktree prune` borra los registros de worktrees cuyas carpetas ya no existen.
