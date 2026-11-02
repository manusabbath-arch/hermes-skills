## Pedido 1

No lo bajaría a warning en bloque. Si el equipo ya ignora el rojo, un warning va a correr la misma suerte: el problema es que la compuerta muestra "falló" por algo que no es un fallo del código.

Yo separaría los 5 o 6 casos en tres grupos:

- **Dato faltante que hace imposible el chequeo:** que no sea rojo ni warning. Ponelo como "omitido" o "no aplicable", con el motivo escrito. Así la compuerta no mezcla "no pudimos medirlo" con "está mal".
- **Dato faltante que sí se puede conseguir:** arreglá la fuente o el pipeline de datos. Es lo que de verdad saca el ruido.
- **Chequeo que falla por algo real:** mantenelo bloqueante, aunque sea uno solo.

Después, revisá los 120 y bajá a warning solo los que son advertencias por naturaleza (de calidad o de estilo). Los de seguridad, integridad o regresiones tienen que seguir bloqueando.

## Pedido 2

No revertiría todavía. Un código de salida 127 en la shell significa "comando no encontrado". Eso apunta a un problema del entorno (una herramienta que no está en el PATH, un intérprete que falta, un script que llama a un ejecutable inexistente), no a un error en el código de los archivos que no tocaste. Y 300 fallos iguales en archivos que no modificaste suelen venir de una sola causa común.

Antes de revertir, verificá:

1. Leé el mensaje completo de uno de los fallos y anotá qué comando aparece como "no existe".
2. Corré ese comando a mano y fijate si está instalado y en el PATH (en PowerShell: `Get-Command <nombre>`, o `where.exe <nombre>`).
3. Mirá si tu último commit cambió algo que esa suite invoca: un script, una ruta, un shebang, un archivo de configuración. Si no lo toca, revertirlo no arregla nada.
4. Si querés confirmar que el commit es la causa, probá la suite en el commit anterior sin tocar tu rama, con un worktree aparte (ver Pedido 3), o usá `git bisect`.

Si el comando faltante es algo que tu commit agregó (por ejemplo, una dependencia nueva que no se instaló), lo correcto es instalarla o documentarla, no revertir.

Un detalle: en el entorno que tengo, este directorio no aparece como repositorio git. Si el commit está en otro lado, los comandos de arriba tenés que correrlos desde la carpeta correcta.

## Pedido 3

`git worktree add` crea un directorio de trabajo adicional, vinculado al mismo repositorio. Cada worktree tiene su propia carpeta, su propio índice y su propio HEAD, pero comparte los objetos, las ramas y el historial con el repo principal.

Usos típicos:

```
git worktree add ../prueba v1.2                 # checkout de un commit/tag/rama en otra carpeta
git worktree add -b hotfix ../hotfix origin/main # crea una rama nueva desde origin/main
git worktree add --detach ../revision abc1234    # checkout en HEAD separado
```

Sirve para probar una versión vieja o revisar otra rama sin hacer `stash` ni cambiar tu working tree actual. Git no te deja tener la misma rama checkouteada en dos worktrees a la vez, salvo que uses `--force`.

Para administrarlos:

- `git worktree list`: muestra los worktrees existentes.
- `git worktree remove <ruta>`: lo elimina (si no tiene cambios sin commitear).
- `git worktree prune`: limpia referencias a carpetas que ya no existen.
