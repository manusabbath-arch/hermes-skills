## Pedido 1

Supuestos: GitHub Actions, proyecto Python, bandit sobre `src/`. No tengo el archivo, así que describo qué cambiaría.

**Problemas del CI actual**

1. `pytest | grep passed || exit 1` es frágil. El pipe devuelve el código de salida de `grep`, no el de pytest. Si hay tests fallidos pero el resumen incluye "1 failed, 40 passed", grep encuentra "passed" y el CI pasa en verde. Además, si no se recolecta ningún test o hay un error de colección, el resultado depende del texto. Reemplazo por `pytest -q --maxfail=20` (sin pipe), y si se necesita el reporte, `--junitxml=report.xml`. Opcional: `set -o pipefail` en el shell de los steps.
2. `bandit ... || true` anula el check: nunca falla. Lo cambio a `bandit -r src -ll -ii` (solo severidad y confianza media o alta) y, si hoy hay hallazgos, uso un baseline (`bandit -r src -b .bandit-baseline.json`), de modo que falle solo con hallazgos nuevos. Los falsos positivos se marcan con `# nosec Bxxx` y una justificación.

**Dejarlo listo para agentes**

- Un único comando local que replica el CI: `make check` (o `just check`), que corre lint, bandit y pytest. El YAML del CI llama a ese mismo comando, así no hay divergencia entre lo que el agente corre y lo que corre el CI.
- `AGENTS.md` en la raíz (Claude Code, Hermes y OpenCode lo leen o se puede enlazar desde sus archivos propios): cómo correr los checks, qué no tocar (el workflow de CI, el baseline), y la regla "no debilitar un check para que pase: nada de `|| true`, `# nosec` sin motivo, `skip` o `xfail` sin issue".
- `CODEOWNERS` sobre `.github/workflows/` para exigir revisión humana en cambios de CI.
- Salida de errores clara y con códigos de salida reales, que un agente pueda interpretar.

## Pedido 2

Supuesto: Python con ruff (el enfoque aplica igual a eslint, flake8, etc.).

La idea es **bloquear regresiones sin exigir arreglar el pasado**: la deuda queda congelada y no puede crecer.

Opciones, de más a menos recomendable:

1. **Baseline de violaciones existentes.** Generás un archivo con las 180 actuales (en ruff: `ruff check --add-noqa` agrega `# noqa: CODIGO` en cada línea; con otras herramientas, un baseline file). El CI queda en verde hoy y cualquier violación nueva rompe el build. Commit aparte, con mensaje claro, para que sea fácil de revisar.
2. **Solo código nuevo o modificado.** Correr el linter sobre el diff contra `main` (por ejemplo `reviewdog` o `git diff --name-only origin/main | xargs ruff check`). Más permisivo, pero la deuda en archivos tocados se paga gradualmente.
3. **Por directorio.** Activás la regla con `per-file-ignores` para los paths viejos y estricta en el resto; vas achicando la lista de excepciones.

Complemento: abrí un issue "Pagar deuda de lint" con el conteo actual y una meta (ej. bajar 20 por semana). Si algunas de las 180 son autofixeables (`ruff check --fix` en un PR separado y mecánico), arreglá primero esas: suele ser buena parte del total.

Evitá desactivar la regla globalmente o poner el check como "advisory" sin fecha: nadie lo mira y vuelve a crecer.

## Pedido 3

Supuesto: los tres agentes trabajan en el mismo repo en paralelo, con un humano que integra.

**Aislamiento físico**
- Una rama y un `git worktree` por agente (`git worktree add ../repo-claude agent/claude/<tarea>`). Cada uno tiene su directorio de trabajo: nadie pisa archivos sin commitear de otro, ni comparte el índice de git.
- Nada de commits directos a `main`: todo por PR, con el CI como árbitro. Protección de rama en `main`.

**Aislamiento lógico**
- Dividir por **área de código**, no por tipo de tarea: por ejemplo, Claude Code toma `api/`, Hermes `jobs/`, OpenCode `docs/` y tests. Una tabla de propiedad en `AGENTS.md` (agente, directorios, rama).
- Archivos compartidos y conflictivos (lockfiles, `pyproject.toml`, migraciones, CI, `__init__`, configs): un solo dueño, o cambios solo por PR chico y propio, mergeado rápido.
- Tareas pequeñas y cortas; rebase frecuente sobre `main` para detectar conflictos temprano.

**Coordinación**
- Un `TASKS.md` (o issues de GitHub) con estados: quién tomó qué. Regla: reclamar la tarea antes de empezar.
- Mismo `AGENTS.md` leído por los tres, con comandos de verificación (`make check`) y convenciones.
- Puertos, bases de datos y caches de test separados por worktree (variables de entorno por agente) para evitar colisiones en runtime.

**Integración**
- Merge secuencial: un PR por vez, rebase y CI verde antes de mergear. Revisión humana o de otro agente cruzada.
