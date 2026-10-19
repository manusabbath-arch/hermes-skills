## Pedido 1

Esto es esperable: el repo tap es la fuente canónica, pero lo que Hermes carga es la copia instalada en tu perfil. Un push al repo no llega solo a los perfiles, y la copia queda desactualizada sin avisar.

Supuesto: ya hiciste commit y push de la edición (con paths explícitos, no `git add -A`).

Qué hacer ahora:
1. Re-instalá en cada perfil que use la skill: `hermes skills install <owner>/<repo>/skills/<nombre>`. Para perfiles adicionales, `hermes --profile <perfil> skills install ...`.
2. Si el install falla, copiá a mano la carpeta de la skill (SKILL.md y templates/) sobre el `skills/` del perfil, y verificá con `ls`.

Para que no te vuelva a pasar, y si el tap es tuyo y lo editás seguido, reemplazá la copia por un symlink:

```bash
ln -sfn /ruta/al/tap/skills/<nombre>/ ~/.hermes/skills/<nombre>
```

Con el symlink, el cambio en el repo es el cambio en el perfil, sin reinstalar. Hermes y Claude Code resuelven symlinks. Dejá el install por copia solo para consumidores externos que quieren una versión congelada. Hacelo también en `~/.hermes/profiles/<p>/skills/` si tenés otros perfiles.

## Pedido 2

Supuesto: el tap ya existe y está agregado a tus perfiles.

1. Creá `skills/<nombre>/SKILL.md`. El `name:` del frontmatter tiene que ser idéntico al nombre del directorio, o la skill no se resuelve. La `description` debe decir qué hace y cuándo usarla, porque es lo único que el agente lee para decidir si la carga.
2. Escribí `skills/<nombre>/evals/evals.json` con al menos 3 escenarios reales y el comportamiento esperado. Conviene escribirlos antes que la prosa. Templates, references y scripts son opcionales.
3. Sumá la fila de la skill al README y subí el conteo del bloque `verify` `skills-count`. Si no, `doc_verify` falla.
4. Corré los checks del repo, que son los mismos del CI:
   - `python3 scripts/validate_skills.py`
   - `python3 -m pytest skills -q`
   - `python3 skills/agent-ready-project/scripts/doc_verify.py --root . --docs README.md`
5. Hacé commit y push con paths explícitos, por ejemplo `git add README.md skills/<nombre>/`. `git add -A` está bloqueado por los guards.
6. Verificá con `hermes skills inspect <owner>/<repo>/skills/<nombre>`. Debe mostrar Name, Description y Repo. No uses `search`, que no cubre taps.
7. Propagá a cada perfil: install, o symlink si el tap es tuyo.

## Pedido 3

Ese error ("Could not fetch from any source") suele venir de la resolución vía skills.sh externo, que es frágil. No indica un problema con el contenido de tu repo. Si `hermes skills inspect <owner>/<repo>/skills/<nombre>` resuelve, la skill está bien.

No reintentes el install en loop contra el mismo error. Hacé la propagación manual:

```bash
mkdir -p ~/.hermes/skills/<nombre>
cp -r <repo>/skills/<nombre>/SKILL.md <repo>/skills/<nombre>/templates ~/.hermes/skills/<nombre>/
```

Repetilo para cada perfil con `mkdir -p ~/.hermes/profiles/<p>/skills/<nombre>` y la misma copia. Preservá `templates/` (y `evals/`, `references/` o `scripts/` si los tiene). Después verificá con `ls` en el perfil.

Si el tap es tuyo, un symlink sirve igual y evita futuros desfases:

```bash
ln -sfn <repo>/skills/<nombre>/ ~/.hermes/skills/<nombre>
```
