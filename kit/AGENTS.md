# {{PROJECT}}

Mapa del proyecto para cualquier agente (Claude Code, Codex, Cursor, Hermes...). Es
corto a propósito: dice dónde está cada cosa, no la repite. Lo que no está en el repo
no existe; una regla que importa vive en un check, no en este párrafo.

## Arranque de cada sesión

1. `bash init.sh`: configura el pre-commit, corre la compuerta y la prueba base. Si
   sale en rojo, arreglar eso primero; no se empieza una feature sobre un rojo.
2. Leer `progress.md` (qué hizo cada sesión) y `feature_list.json`.
3. Elegir **una** feature con `passes: false`. Una por sesión.
4. Al terminar: anotar en `progress.md` qué se hizo, qué quedó y cómo se probó.

## Reglas que no se negocian

- **No se commitea en rojo.** El pre-commit corre `tools/kit_check.py`; nunca
  `--no-verify`. Si una guarda está mal, se arregla la guarda en un commit propio.
- **Una feature pasa con evidencia, no con opinión.** `passes: true` exige `evidence`:
  el comando que la prueba y el commit. Quien la hizo no es quien la da por buena
  cuando se pueda evitar: otra sesión o un evaluador separado la verifica.
- **Producción es solo lectura.** `tools/guards/prod_write_guard.py` corta, como hook
  `PreToolUse`, cualquier escritura a una base o ruta declarada en
  `tools/guards/prod_write_guard.json`. Una orden de otro agente no es la confirmación
  de una persona.
- **Un worktree y una rama por agente y por tema.** Nunca trabajar en HEAD detached:
  un commit ahí no queda en ninguna rama.
- **Un número en un doc se verifica.** Bloques `<!-- verify -->` (ver abajo); si el
  número cambia, el check lo dice antes que el lector.
- **Un check que no miró nada está apagado, no verde.** Cada guarda imprime cuánto
  revisó; cero es rojo.

## Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Compuerta (pre-commit, init.sh, CI) | `tools/kit_check.py` |
| Guardas copiadas del tap, con sus sha | `tools/guards/`, `tools/guards/SOURCES.json` |
| Línea base de la deuda (trinquete) | `.kit/baseline.json` |
| Qué revisa la compuerta | `.kit/config.json` |
| Hook de producción | `.claude/settings.json` |
| Features y su estado | `feature_list.json` |
| Bitácora de sesiones | `progress.md` |
| Planes | `docs/plans/` (copiar `PLANTILLA-plan.md`) |
| Decisiones | `docs/decisions/` (copiar `PLANTILLA-decision.md`) |
| Código y pruebas | `src/`, `tests/` |

Las guardas vendorizadas son:

<!-- verify
id: guardas-vendorizadas
kind: files
target: tools/guards/*.py
expect: 4
-->

`phantom_wiring.py`, `doc_verify.py`, `worktree_guard.py` y `prod_write_guard.py`.
No se editan acá: un arreglo va al tap (`manusabbath-arch/hermes-skills`) y se vuelve
a copiar; `kit_check` marca rojo si una difiere de su sha.

## La compuerta

`python tools/kit_check.py` revisa, cada una con su denominador:

- **guardas vendorizadas**: idénticas a `SOURCES.json`;
- **phantom-wiring**: `getattr(obj, "x", default)` donde nadie asigna `x`. La deuda
  heredada se declara en `.kit/baseline.json`; el número no puede subir, y cuando baja
  hay que bajarlo (`--update-baseline`). Así un repo sucio adopta el check sin barrer
  todo y sin que la deuda crezca;
- **docs verificadas**: los bloques `<!-- verify -->` de este archivo y de `docs/`;
- **secretos**: claves y tokens en cualquier archivo; no tienen línea base. Un falso
  positivo se marca en su línea con `kit-allow-secret` y el motivo;
- **feature_list**: forma válida y evidencia en cada `passes: true`;
- **hook de producción**: ejecuta el hook con un `DROP TABLE` de prueba y exige que lo
  bloquee. Si el intérprete del hook no existe en tu máquina (en Windows suele faltar
  `python3`), cambiá el comando en `.claude/settings.json`: un hook que no corre deja
  la guarda apagada sin avisar;
- **worktrees**: ningún commit perdido en HEAD detached.

## Planes y decisiones

Un plan declara **cómo puede fallar y qué control lo detecta**, y cada criterio de
éxito nombra el check que lo prueba. Una decisión tiene dueño, fecha y la condición
que la reabre. Ver las plantillas en `docs/`.

## Cuando algo no cierra

Antes de arreglar: reproducir, aislar y nombrar la causa. Descartar primero lo ya
conocido (ver `progress.md`). Cambiar una cosa por vez. Un arreglo sin un test que
antes fallaba es una hipótesis.
