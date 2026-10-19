## Pedido 1

Lo más probable es que tu perfil tenga una copia instalada de la skill y no un enlace al repo. El repo es la fuente canónica, pero un push no actualiza los perfiles solo. Supuesto: la skill está instalada por copia.

Pasos:

1. Confirmá que el commit llegó a `origin` (con `git push`, paths explícitos).
2. Re-instalá en cada perfil: `hermes skills install <owner>/<repo>/skills/<name>` (y `hermes --profile <nombre> skills install ...` para los perfiles adicionales).
3. Si el install falla con "Could not fetch from any source", hacé la propagación manual: copiá `SKILL.md` y `templates/` del repo a `~/.hermes/skills/<name>/` y a `~/.hermes/profiles/<nombre>/skills/<name>/`. Verificá con `ls`.

Para un tap propio que editás seguido, conviene un symlink en vez de copias. Así el cambio del repo es el cambio del perfil y no hace falta re-instalar:

```bash
ln -sfn /ruta/al/tap/skills/<name> ~/.hermes/skills/<name>
ln -sfn /ruta/al/tap/skills/<name> ~/.claude/skills/<name>
```

Reservá la copia para consumidores externos que quieran una versión congelada.

## Pedido 2

Pasos para publicar una skill nueva en el tap:

1. Creá `skills/<name>/SKILL.md`. El `name:` del frontmatter tiene que ser igual al nombre del directorio, y la `description` tiene que decir qué hace y cuándo usarla.
2. Escribí `evals/evals.json` con al menos 3 escenarios: pedidos reales con el comportamiento esperado. Escribilos antes que la prosa.
3. Agregá `templates/` (y `references/` o `scripts/` si hacen falta).
4. Sumá una fila para la skill en `README.md` y subí el conteo del bloque `verify` (`skills-count`).
5. Corré los checks antes del push:
   - `python3 scripts/validate_skills.py`
   - `python3 -m pytest skills -q`
   - `python3 skills/agent-ready-project/scripts/doc_verify.py --root . --docs README.md`
6. Commiteá con paths explícitos (no `git add -A`) y hacé push.
7. Agregá el tap en cada perfil (`hermes skills tap add <owner>/<repo>`), verificá con `hermes skills inspect <owner>/<repo>/skills/<name>` y después instalala o enlazala.

Supuesto: el repo ya existe y los skills viven en el path default `skills/`.

## Pedido 3

`install` resuelve la skill a través de un origen externo (skills.sh) y es frágil a esa resolución. El problema no está en el contenido del repo: si `inspect` ya resuelve la skill, el layout es correcto. No reintentes el install en loop.

Instalala a mano:

1. `mkdir -p ~/.hermes/skills/<name>`
2. Copiá `SKILL.md` y `templates/` desde `<repo>/skills/<name>/` a esa carpeta.
3. Repetí en cada perfil: `~/.hermes/profiles/<perfil>/skills/<name>/`.
4. Verificá con `ls` en cada perfil.

Si después querés que las actualizaciones lleguen solas, usá el symlink del Pedido 1.

## Pedido 4

El CI falla con `skills-count` porque agregaste la skill pero no actualizaste el conteo que verifica `doc_verify`. Supuesto: el bloque `verify` del README tiene el número de skills.

Para arreglarlo:

1. Agregá la fila de la skill nueva en `README.md`.
2. Actualizá `skills-count` al número real de skills en `skills/`.
3. Corré `python3 skills/agent-ready-project/scripts/doc_verify.py --root . --docs README.md` localmente antes de hacer push.

## Pedido 5

El problema es el nombre. El loader indexa las skills por directorio, y el `name:` tiene que coincidir con él. Hoy el directorio es `MiSkill` y el `name` es `mi-skill`, así que la skill no se resuelve y no aparece al instalar.

Para arreglarlo, elegí una de estas opciones:

- Renombrá el directorio a `skills/mi-skill/` (la opción recomendada, porque el nombre queda en minúsculas y con guiones).
- O cambiá `name:` para que sea `MiSkill`. Esta opción no es recomendable.

Después, revisá lo demás de la skill nueva:

- `evals/evals.json` con al menos 3 escenarios.
- Fila en el `README.md` y conteo `skills-count` actualizado.
- Los checks de validación y `doc_verify`.
- `hermes skills inspect <owner>/<repo>/skills/mi-skill`, que tiene que mostrar Name y Description.

Recordá que `hermes skills search` no busca en taps, así que no sirve para verificar la skill.

## Pedido 6

Con la CLI de GitHub:

```bash
gh repo create <owner>/<repo> --public --description "Mi descripción"
```

Usá `--private` si no querés que sea público. Si además querés clonarlo en tu máquina, agregá `--clone`.

También podés crearlo desde la web, en github.com/new.
