## Pedido 1

Es lo esperado: el repo tap es la fuente canónica, pero lo que Hermes carga es la **copia instalada en el perfil**. Un push al repo no llega solo a los perfiles.

Pasos:

1. Commit + push del cambio con paths explícitos (`git add skills/<name>/`, nunca `git add -A`).
2. Re-instalá en cada perfil que use la skill:
   ```bash
   hermes skills install <owner>/<repo>/skills/<name>
   hermes --profile <p> skills install <owner>/<repo>/skills/<name>
   ```
   Si el install falla, copiá a mano la carpeta (con `templates/`) sobre `~/.hermes/skills/<name>` o `~/.hermes/profiles/<p>/skills/<name>`.

**Fix de fondo:** si el tap es tuyo y lo editás seguido, reemplazá la copia por un symlink, así el cambio en el repo *es* el cambio en el perfil:
```bash
ln -sfn /ruta/al/tap/skills/<name>/ ~/.hermes/skills/<name>
```
Hermes (y Claude Code, en `~/.claude/skills/`) resuelven symlinks. Dejá el install por copia para consumidores externos que quieren una versión congelada.

Verificá después con `ls ~/.hermes/skills/<name>` que el contenido es el nuevo.

## Pedido 2

1. Creá `skills/<nombre>/SKILL.md` en el repo tap. El `name:` del frontmatter tiene que ser **idéntico al nombre del directorio**, y la `description` tiene que decir qué hace y cuándo usarla.
2. Escribí primero `skills/<nombre>/evals/evals.json` con al menos 3 escenarios (pedidos reales + comportamiento esperado); después la prosa. `templates/`, `references/` y `scripts/` son opcionales.
3. Sumá la fila de la skill al README y subí el conteo del bloque `verify` `skills-count`.
4. Corré los checks (los mismos del CI):
   ```bash
   python3 scripts/validate_skills.py
   python3 -m pytest skills -q
   python3 skills/agent-ready-project/scripts/doc_verify.py --root . --docs README.md
   ```
5. Commit + push con paths explícitos:
   ```bash
   git add README.md skills/<nombre>/ && git commit -m "feat: add <nombre> skill" && git push
   ```
6. Verificá que el tap la resuelve: `hermes skills inspect <owner>/<repo>/skills/<nombre>` (no uses `search`, no cubre taps).
7. Propagala a cada perfil: `hermes skills install <owner>/<repo>/skills/<nombre>` (o symlink si es tu tap y la vas a editar seguido). Si el perfil todavía no tiene el tap: `hermes [--profile <p>] skills tap add <owner>/<repo>`.

## Pedido 3

Ese error suele no tener que ver con tu repo: el install resuelve vía skills.sh externo y es frágil a eso. Si `hermes skills inspect <owner>/<repo>/skills/<name>` la resuelve y está commiteada, el contenido está bien. No reintentes el install en loop.

Propagación manual:

```bash
mkdir -p ~/.hermes/skills/<name>
cp -r <repo>/skills/<name>/SKILL.md <repo>/skills/<name>/templates ~/.hermes/skills/<name>/
```

Repetilo por cada perfil adicional en `~/.hermes/profiles/<p>/skills/<name>/`, preservando `templates/` (y `references/`/`scripts/` si los tiene). Verificá con:

```bash
ls ~/.hermes/skills/<name>
```

Alternativa si el tap es tuyo: en vez de copiar, symlink (`ln -sfn <repo>/skills/<name>/ ~/.hermes/skills/<name>`), así los próximos cambios llegan solos sin depender del install.

## Pedido 4

Porque el README tiene un bloque `verify` con id `skills-count` que declara cuántas skills hay en `skills/`, y `doc_verify` compara ese número contra el estado real del repo. Al agregar una skill, el conteo real subió pero el README sigue con el número viejo → la doc drifta y el check falla.

Fix:

1. Agregá la fila de la skill nueva a la tabla del README.
2. Subí en uno el conteo del bloque `skills-count`.
3. Verificá localmente antes del push:
   ```bash
   python3 skills/agent-ready-project/scripts/doc_verify.py --root . --docs README.md
   ```
4. Commit + push de `README.md` (path explícito).

Ya que estás, corré también `python3 scripts/validate_skills.py` y `python3 -m pytest skills -q`, que son los otros checks del CI.

## Pedido 5

El `name:` del frontmatter tiene que ser **exactamente igual al nombre del directorio**. El loader indexa por directorio: `MiSkill` ≠ `mi-skill`, así que la skill no se resuelve.

Fix: renombrá el directorio a `skills/mi-skill/` (la convención es kebab-case en minúscula, coincidiendo con el `name:`):

```bash
git mv skills/MiSkill skills/mi-skill
python3 scripts/validate_skills.py
git commit -m "fix: rename MiSkill dir to match name" && git push
```

Después verificá con `hermes skills inspect <owner>/<repo>/skills/mi-skill` y reinstalá con `hermes skills install <owner>/<repo>/skills/mi-skill`. Si quedó una copia vieja en el perfil bajo `MiSkill`, borrala.

(Recordá también que carpetas que arrancan con `.` o `_` se saltan.)

## Pedido 6

Con la CLI de GitHub (`gh`), autenticada con `gh auth login`:

```bash
gh repo create <owner>/<repo> --public --description "Descripción"
```

Usá `--private` en lugar de `--public` si no querés que sea visible. Después lo clonás con `gh repo clone <owner>/<repo>`.

Si ya tenés una carpeta local con código:

```bash
gh repo create <owner>/<repo> --private --source . --push
```

Sin CLI: en github.com, botón **New repository**, elegís nombre y visibilidad, y **Create repository**.
