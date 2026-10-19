## Pedido 1

Lo que pasa es que el tap es la fuente canónica, pero las copias instaladas en cada perfil no se actualizan solas. Cada push al repo tiene que propagarse a mano a cada perfil.

Tenés dos opciones:

1. **Re-instalar** desde el tap:
   `hermes skills install <owner>/<repo>/skills/<name>`
   Hacelo en cada perfil donde la skill esté cargada (`hermes --profile <nombre> skills install ...`).

2. **Usar symlinks** (lo que recomiendo si es un tap propio que editás seguido). Así el cambio en el repo es el cambio en el perfil, sin re-instalar:

```bash
for s in /ruta/al/tap/skills/*/; do
  n=$(basename "$s")
  ln -sfn "$s" ~/.claude/skills/$n     # Claude Code
  ln -sfn "$s" ~/.hermes/skills/$n     # Hermes (perfil default)
done
```

Reservá la copia instalada para consumidores externos que quieran una versión congelada.

Si ya tenés una copia vieja, reemplazala por el symlink (o re-instalá) y verificá con `ls` en el perfil.

## Pedido 2

Supongo que el repo tap ya existe. Si no, creálo con `gh repo create <owner>/<repo> --public --description "..."`.

Pasos:

1. Crear `skills/<name>/` con:
   - `SKILL.md`. El `name:` del frontmatter tiene que ser igual al nombre del directorio.
   - `evals/evals.json` con al menos 3 escenarios. El validador lo exige.
   - `templates/` (opcional, para `references/` y `scripts/`).
2. Agregar una fila para la skill en el `README.md`.
3. Subir el conteo del bloque `verify` `skills-count` del README. Si no, `doc_verify` falla.
4. Correr los checks antes del push, igual que el CI:
   - `python3 scripts/validate_skills.py`
   - `python3 -m pytest skills -q`
   - `python3 skills/agent-ready-project/scripts/doc_verify.py --root . --docs README.md`
5. Commitear con paths explícitos, nunca con `git add -A`:
   `git add README.md skills/<name>/ && git commit -m "feat: add <name> skill tap" && git push -u origin main`
6. Verificar que el tap resuelve la skill con `hermes skills inspect <owner>/<repo>/skills/<name>`. Tiene que mostrar Name, Description y Repo.
7. Agregar el tap en cada perfil (`hermes skills tap add <owner>/<repo>`) e instalar la skill.

Decidí si el repo es público o privado. Público sirve para compartir; privado si es conocimiento propietario.

## Pedido 3

`inspect` resuelve la skill, así que el problema no está en el contenido del repo. El `install` resuelve vía skills.sh externo y es frágil a eso.

Propagación manual:

```bash
mkdir -p ~/.hermes/skills/<name>
cp -r <repo>/skills/<name>/SKILL.md ~/.hermes/skills/<name>/
cp -r <repo>/skills/<name>/templates ~/.hermes/skills/<name>/
```

Repetilo en cada `~/.hermes/profiles/<perfil>/skills/` que la necesite. Preservá `templates/`. Verificá con `ls` en cada perfil.

No reintentes el install en loop contra el mismo error. Si querés que quede sincronizada con el repo, el symlink del Pedido 1 evita este paso.

## Pedido 4

El CI falla porque una skill nueva tiene que tener su fila en el `README.md` y el conteo del bloque `verify` `skills-count` tiene que subir. Si no lo hacés, `doc_verify` detecta que el README no coincide con el estado real del repo.

Para arreglarlo:

1. Agregar la fila de la skill en el README.
2. Subir `skills-count` en el bloque `verify`.
3. Correr localmente `python3 skills/agent-ready-project/scripts/doc_verify.py --root . --docs README.md` y confirmar que pasa antes de pushear.

Si el bloque tiene otra forma de la que supongo, el mensaje de error de `doc_verify` te va a indicar qué valor no coincide.

## Pedido 5

El loader indexa las skills por nombre de directorio, no por el `name:` del frontmatter. Como `MiSkill` y `mi-skill` no coinciden, la skill no se resuelve y no aparece al instalar.

Hay dos formas de arreglarlo, y tienen que quedar iguales:

- Renombrar el directorio a `skills/mi-skill/` (mi recomendación, en minúsculas con guiones, como el resto de las skills).
- O cambiar el `name:` a `MiSkill`.

Después de renombrar, corré `validate_skills.py`, verificá con `hermes skills inspect <owner>/<repo>/skills/mi-skill` y re-propagá a cada perfil.

## Pedido 6

Con la CLI de GitHub:

```bash
gh repo create <owner>/<repo> --public --description "..."
```

Usá `--private` si la skill es conocimiento propietario. Después clonalo con `gh repo clone <owner>/<repo>` y seguí con la estructura `skills/<name>/`.
