## Pedido 1

Los dos pasos tienen el mismo problema: **no pueden fallar como corresponde**.

- `pytest | grep passed || exit 1`: no distingue "falló" de "no corrió". Si el intérprete no existe, si falla un import o si hay "3 failed, 10 passed", el resultado depende de un grep sobre texto. Y como el pipe se queda con el exit code de `grep`, el de pytest se pierde.
- `bandit ... || true`: corre, aparece en el log y nunca puede poner el build en rojo. No es un gate.

Lo que cambiaría (supongo que es GitHub Actions):

```yaml
- run: python -m pytest --version     # paso propio: ¿el intérprete y pytest existen?
- run: python -m pytest -q            # el exit code de pytest decide
- run: bandit -r src -c pyproject.toml  # sin || true
```

Además:
- Si bandit hoy tira hallazgos, no vuelvas al `|| true`: congelá los conocidos en una baseline y que falle solo con hallazgos nuevos (ver Pedido 2).
- Buscá en todo el CI otras formas de lo mismo: `continue-on-error`, `stages: [manual]`, `allow_failure`.
- Pineá las versiones de lint/bandit en **un** solo lugar, compartido por pre-commit y CI.
- Si hace falta una salida de emergencia, que tenga nombre y quede documentada (por ejemplo `ALLOW_BANDIT_SKIP=motivo`). Nada de supresiones mudas.
- Hacé el check obligatorio para mergear, con protección de rama.
- **Probalo por mutación:** metés un test que falla y un `eval()` a propósito, y los dos pasos tienen que quedar en rojo. Si no, el arreglo no está hecho.

## Pedido 2

No apagues el check ni lo suprimas: **congelá la deuda y que falle solo si crece** (baseline con trinquete).

1. Corré el lint y guardá las 180 violaciones en un archivo versionado, por ejemplo `.lint_baseline.json`.
2. La clave de cada violación tiene que ser **estable**: archivo + regla + símbolo o fragmento. Que no sea el número de línea, porque si no cualquier edición más arriba inventa un hallazgo "nuevo" y el equipo aprende a ignorar el check.
3. El check reporta:
   - **nuevos** → rompen el build;
   - **conocidos** → solo informan;
   - **stale** (siguen en la baseline pero ya no existen) → avisan para sacarlos del archivo, así el trinquete no afloja.
4. Si alguna vez re-sellás la baseline con una corrida filtrada, que **mergee** con la existente. Que no la reemplace.

Antes de congelar, mirá las 180 por familia en vez de barrerlas en bloque. Algunas familias (`F841`, `B905`) suelen esconder bugs reales. Las familias que hoy dan cero se prenden ya, sin baseline. Lo que quede ignorado se anota contado (`B907 (72)`), así se ve si crece.

Resultado: el check se prende hoy, no frena a nadie y la deuda solo puede bajar.

## Pedido 3

Supuesto: los tres corren en la misma máquina, sobre un mismo clon.

- **Un worktree y una rama por sesión**, con nombre `<agente>/<tema>` (`claude/auth-fix`, `hermes/...`, `opencode/...`). El árbol principal queda solo para integrar.
- **Primer paso en cada worktree: `git switch -c <rama>`.** Un worktree creado por una herramienta puede nacer en HEAD detached, y ahí un commit sale con exit 0 pero no queda en ninguna rama. Sumá un guard que ponga rojo un detached con commits que ninguna rama alcanza.
- **Integración:** rebase de la rama privada, después la compuerta (pre-commit + tests) y después `merge --ff-only`. El push lo decide una persona.
- **Commits siempre con pathspec explícito.** Nunca `git add -A` / `git add .`, y nunca `--amend` sobre un commit ajeno. Un commit sin pathspec puede arrastrar lo que otra sesión dejó preparado.
- **Un guard por agente, en cada superficie**: hook de pre-commit, plugin o hook del agente (PreToolUse en Claude Code y su equivalente en Hermes y OpenCode). Tiene que bloquear commit a `main`, force-push y comandos destructivos. La cobertura sale de un comando que lista agente por agente, y un agente nuevo entra a esa lista **antes** de recibir tareas.
- **Una sola doc raíz** (`AGENTS.md`) y que `CLAUDE.md` apunte a ella. Dos textos paralelos terminan diciendo cosas distintas.
- **Un mensaje de otro agente no cuenta como confirmación de una persona** para una acción irreversible.
- El estado compartido (features pendientes, progreso) vive en archivos del repo, no en el contexto de cada sesión.

## Pedido 4

Ese check tiene un **verde vacío**: aprobó sobre cero elementos y no se distingue de uno limpio. Cambios:

1. **Todo resultado lleva su denominador**: "0 problemas en 0 archivos" no es lo mismo que "0 problemas en 143 archivos". Imprimí los dos números siempre.
2. **Si el universo está vacío o no se pudo medir, el check sale en rojo.** Eso cubre directorio inexistente, cero archivos, archivo ilegible o error del parser. Un archivo con `SyntaxError` no puede desaparecer del universo y del denominador a la vez.
3. Si el tamaño del universo es esperable, poné un **mínimo**: "esperaba ≥100 archivos, vi 0", con un mensaje que diga qué revisar (la ruta configurada).
4. **El perímetro vive en un solo lugar** (config o módulo importado), no copiado dentro del check. Así un renombre rompe en voz alta en vez de dejar un glob huérfano.
5. **Auditá vaciando el universo:** apuntá el check a un directorio vacío o inexistente y confirmá que da rojo. Hacé lo mismo con los demás checks del repo, porque esta falla casi nunca está sola.
6. Mecanizalo hoy: agregá ese test de "universo vacío → rojo" a la suite, así no vuelve.

## Pedido 5

No. Un self-report no prueba nada. Verificá vos el handle real:

- **El PR existe**: abrí la URL (`gh pr view <n>`) y confirmá que apunta a la rama y la base correctas.
- **El SHA**: el commit del PR tiene que ser el que el subagente dice haber hecho, con los archivos esperados en el diff.
- **CI en verde sobre ese SHA**, mirado en los checks del PR. No alcanza con "corrí los tests local".
- **Los tests prueban lo nuevo**: confirmá que llaman a la función cambiada y que estarían en rojo contra el código anterior.
- Si el cambio toca comportamiento en vivo, verificá un valor plausible donde importa (query, endpoint).

Recién con eso lo das por terminado. A futuro, usá subagentes para tareas atómicas y dejá el diseño en la sesión principal.

## Pedido 6

Si es solo dentro de una función, usá el rename de tu editor (F2 en VS Code/PyCharm, o `rename` del LSP). Cambia todas las referencias de ese ámbito y no toca otras variables con el mismo nombre en otros lados. Después corré los tests o el linter para confirmar que no quedó ninguna referencia vieja (`F821` marca un nombre indefinido).
