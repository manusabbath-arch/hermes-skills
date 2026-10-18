## Pedido 1

Supuesto: no tengo el archivo de CI a la vista, así que describo los cambios sobre las dos líneas que mencionás.

El problema con `pytest | grep passed || exit 1` es que el código de salida que cuenta es el de `grep`, no el de `pytest`. Si hay tests rojos con una salida tipo "1 failed, 5 passed", `grep` encuentra "passed" y el paso queda en verde. Además, si el intérprete o pytest no existen, `grep` no encuentra nada y el error se ve igual que un fallo de tests.

Lo que haría:

1. Verificar el intérprete como paso propio: `python -m pytest --version`. Si falla, el job falla con un mensaje claro de "no corrió".
2. Reemplazar el pipe por `python -m pytest` directo, sin `grep`. El exit code de pytest decide el resultado.
3. Quitar el `|| true` de bandit. Si hoy tiene hallazgos que no se pueden arreglar de golpe, usar una baseline con trinquete (ver Pedido 2) en lugar de dejar el paso incapaz de fallar.
4. Revisar que no haya `continue-on-error`, `stages: [manual]` ni `# noqa` sueltos en el mismo pipeline.
5. Pinear las versiones de black, ruff, bandit y pytest en un solo lugar (por ejemplo `requirements-dev.txt`), y que el pre-commit y el CI lean de ahí.

Para que los agentes lo modifiquen sin romperlo, dejaría una nota corta en el archivo de CI diciendo que un paso no puede tener `|| true` ni pipes que tapen el exit code.

## Pedido 2

No hace falta arreglar las 180 hoy, ni apagar el check. La salida es un **baseline con trinquete**:

1. Congelar las 180 violaciones actuales en un archivo versionado (por ejemplo `.lint_baseline.json`), indexadas por **archivo + regla**, no por número de línea. Si la clave incluye la línea, cualquier edición arriba genera "nuevos" falsos y el equipo aprende a ignorar el check.
2. El check falla solo si aparece una violación que no está en la baseline. Las conocidas se informan con su conteo.
3. Reportar también las entradas **stale** (en la baseline pero ya arregladas) para sacarlas del archivo; si no, el trinquete se afloja.
4. Clasificar antes de suprimir: las familias que dan cero hoy se prenden ya. Las que tienen ruido se cuentan y se ignoran **con el número al lado** (por ejemplo `B007 (19)`), no en bloque. Entre las violaciones puede haber bugs reales.
5. Cada supresión que quede lleva el motivo al lado.

Resultado: la deuda queda visible, cuantificada, y solo puede bajar.

## Pedido 3

Mi propuesta:

1. **Un worktree y una rama por sesión**, con nombre `<agente>/<tema>`. El árbol principal queda solo para integración.
2. **Integrar en tres pasos:** rebase de la rama privada sobre main, pasar la compuerta (lint, tests), y después `merge --ff-only`. El push lo decide una persona.
3. **Verificar que no quedó en HEAD detached.** Un worktree creado por la herramienta puede nacer así, y un commit ahí sale con exit 0 pero no queda en ninguna rama. Primer paso de cada sesión: `git switch -c <rama>`. Un guard tipo `worktree_guard.py` que ponga en rojo ese caso ayuda.
4. **Commits siempre con pathspec** (`git commit -- <archivos>`), y nunca `--amend` sobre un commit ajeno. Así no se arrastran cambios preparados por otra sesión.
5. **Guardas en cada superficie de cada agente.** Bloquear `git add -A`/`.`, commit directo a main y force-push en el hook de cada uno (Claude Code, Hermes y OpenCode). Hay que listar qué agente tiene qué guarda, y un agente nuevo entra a la lista antes de recibir tareas.
6. **Un prompt de otro agente no es confirmación humana** para una acción irreversible.
7. Sesiones sin shell dejan anotado lo que no pudieron commitear, y la sesión con shell lo procesa primero.

## Pedido 4

Lo que pasó es un **verde vacío**: el check no miró nada y aprobó igual. Cambiaría tres cosas:

1. **Todo verde lleva su denominador.** La salida tiene que decir "0 problemas sobre N archivos escaneados". Si N es 0, o el directorio no existe, el check sale **rojo**, no con código 0.
2. **El check pregunta "¿esto debería estar y no está?"**: que el directorio exista, que tenga un mínimo de archivos esperados, y que el conteo no caiga de golpe.
3. **El perímetro vive en un solo lugar.** La lista de directorios que escanea `validar` se define en una constante que el check importa, no en una copia dentro del script.

Para verificarlo: renombrar el directorio a propósito y confirmar que `validar` sale en rojo. Si sigue en verde, el check está apagado. Y agregaría un log incondicional con el conteo, para que un día sin datos no sea silencioso.

## Pedido 5

No. "PR creado y tests en verde" es un self-report sin verificar. Antes de darlo por terminado, yo:

1. Abro la URL del PR y confirmo que existe, que apunta a la rama correcta y que el SHA coincide con el que se pushó.
2. Miro el estado real del CI en el PR, no el resumen del subagente.
3. Corro los tests yo mismo, o al menos reviso su salida completa, y confirmo que se ejecutaron (un "0 passed" en verde no cuenta).
4. Verifico que el cambio hace lo que se pidió, con el comando real y no con un mock.

Los subagentes sirven para tareas atómicas. El diseño y el criterio de "terminado" quedan en la sesión principal.

## Pedido 6

Depende de la herramienta, pero la forma segura es:

- **En un editor** (VS Code, PyCharm): poner el cursor sobre la variable y usar "Rename Symbol" (F2 en VS Code). Renombra solo las referencias dentro de esa función y no toca otra variable con el mismo nombre en otro scope.
- **A mano:** renombrar la asignación, cada uso dentro de la función, y revisar que no haya un nombre igual en otro lugar que deba quedarse igual.
- **Con código:** `rope` o la búsqueda de referencias de un LSP (pyright, pylsp) hacen lo mismo de forma verificable.

Después de renombrar, corré los tests de esa función, o al menos `python -m pyflakes` o `ruff check` para confirmar que no quedó una referencia al nombre viejo.
