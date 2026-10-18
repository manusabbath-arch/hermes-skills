## Pedido 1

Un cambio en el repo no llega solo a los perfiles: el tap es la fuente canónica, pero lo que se carga es la copia instalada en cada perfil. Tu perfil sigue con la versión vieja porque nadie la re-instaló.

Para arreglarlo ahora:
1. Verificá que el cambio esté commiteado y pusheado (con paths explícitos, no `git add -A`).
2. Re-instalá en cada perfil: `hermes skills install <owner>/<repo>/skills/<name>`, o copiá a mano la carpeta de la skill sobre el `skills/` del perfil, preservando `templates/`.

Para que no vuelva a pasar, si el tap es tuyo y lo editás seguido, reemplazá la copia por un symlink:

```bash
ln -sfn /ruta/al/tap/skills/<name>/ ~/.hermes/skills/<name>
```

Con eso el cambio en el repo es el cambio en el perfil, sin re-instalar. Hermes y Claude Code resuelven symlinks. Dejá el install por copia solo para consumidores externos que quieran una versión congelada.

## Pedido 2

Pasos para publicar una skill nueva:

1. Creá `skills/<nombre>/SKILL.md`. El `name:` del frontmatter tiene que ser igual al nombre de la carpeta. La `description` dice qué hace y cuándo usarla.
2. Agregá `evals/evals.json` con al menos 3 escenarios (el validador lo exige). Opcionales: `templates/`, `references/`, `scripts/`.
3. Sumá la fila de la skill al README y subí el conteo del bloque `verify` `skills-count`.
4. Corré los checks del CI:
   ```bash
   python3 scripts/validate_skills.py
   python3 -m pytest skills -q
   python3 skills/agent-ready-project/scripts/doc_verify.py --root . --docs README.md
   ```
5. Commit y push con paths explícitos: `git add README.md skills/<nombre>/ && git commit -m "feat: add <nombre> skill" && git push`.
6. Verificá que el tap la resuelva: `hermes skills inspect <owner>/<repo>/skills/<nombre>`. No uses `search`, que no cubre taps.
7. Propagá a cada perfil con `hermes skills install <owner>/<repo>/skills/<nombre>` (o con symlink si el tap es tuyo). Si falta el tap en un perfil: `hermes --profile <p> skills tap add <owner>/<repo>`.

## Pedido 3

Ese error puede aparecer aunque `inspect` resuelva y la skill esté commiteada. El install resuelve vía skills.sh externo y es frágil a eso; el problema no está en el contenido del repo.

Workaround: propagación manual.

```bash
mkdir -p ~/.hermes/skills/<name>
cp -r <repo>/skills/<name>/SKILL.md <repo>/skills/<name>/templates ~/.hermes/skills/<name>/
```

Repetilo en `~/.hermes/profiles/<p>/skills/<name>` por cada perfil, y copiá también `evals/` y lo que tenga la skill si lo necesitás. Verificá con `ls` en el perfil. Si el tap es tuyo, un symlink a `skills/<name>/` también sirve. No reintentes el install en loop contra el mismo error.

## Pedido 4

`doc_verify` falla porque el bloque `verify` `skills-count` del README lleva el conteo de skills del repo, y vos agregaste una sin actualizarlo. El check compara ese número (y la tabla) contra el estado real, así que detecta el drift.

Arreglo:
1. En el README, agregá la fila de la skill nueva.
2. Subí el número del bloque `verify` `skills-count` en uno.
3. Corré localmente: `python3 skills/agent-ready-project/scripts/doc_verify.py --root . --docs README.md`.
4. Commit y push con paths explícitos.

Antes de pushear también corré `validate_skills.py` y `pytest skills -q`, porque son los mismos checks que bloquean el merge.

## Pedido 5

El `name:` del frontmatter tiene que ser igual al nombre del directorio. El loader indexa por directorio, y si difieren, la skill no se resuelve. Acá tenés `MiSkill` contra `mi-skill`.

Arreglo: renombrá la carpeta a `skills/mi-skill/` (o cambiá el `name:` para que coincida; lo más limpio es la carpeta en minúsculas con guiones). Después:
1. Corré `python3 scripts/validate_skills.py`.
2. Commit y push con paths explícitos.
3. Verificá con `hermes skills inspect <owner>/<repo>/skills/mi-skill`.
4. Re-instalá en el perfil.

Supuesto: la skill ya está pusheada. Si el nombre de carpeta empieza con `.` o `_`, se saltea, pero no es tu caso.

## Pedido 6

Con la CLI de GitHub:

```bash
gh repo create <owner>/<repo> --public --description "..."
```

Usá `--private` si no querés que sea público. Después clonalo con `gh repo clone <owner>/<repo>`.

Desde la web: botón "New" en github.com/new, elegís nombre, visibilidad y, si querés, README, y das "Create repository".

Supuesto: tenés `gh` instalado y autenticado (`gh auth login`).
