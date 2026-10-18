## Pedido 1

Esto es esperable: el repo del tap es la fuente canónica, pero lo que Hermes carga es la copia instalada en tu perfil. Un push al repo no llega solo a los perfiles, así que la copia vieja queda ahí sin que nada falle.

Qué haría, en orden:

1. Verificar que el cambio esté commiteado y pusheado (con paths explícitos, no `git add -A`, que los guards bloquean).
2. Re-propagar al perfil con `hermes skills install <owner>/<repo>/skills/<name>`. Si hay más perfiles, repetirlo con `hermes --profile <nombre> skills install ...` en cada uno.
3. Si el install falla, copiar a mano la carpeta de la skill (`SKILL.md` y `templates/`) sobre el `skills/` del perfil.

Para que no vuelva a pasar, si el tap es tuyo y lo editás seguido, reemplazaría las copias por symlinks hacia el repo:

```bash
ln -sfn /ruta/al/tap/skills/<name> ~/.hermes/skills/<name>
```

Con eso el cambio en el repo es el cambio en el perfil, sin re-instalar. Hermes y Claude Code resuelven symlinks. El install por copia lo dejaría para consumidores externos que quieren una versión congelada.

Supuesto: es un tap propio y el perfil es el default (`~/.hermes/skills`).

## Pedido 2

Pasos para una skill nueva en el tap:

1. Crear `skills/<nombre>/SKILL.md` con frontmatter válido. Los nombres de carpeta que empiezan con `.` o `_` se ignoran.
2. Escribir `skills/<nombre>/evals/evals.json` con al menos 3 escenarios, que son pedidos reales con el comportamiento esperado. Conviene escribirlos antes que la prosa. El validador los exige. Si hace falta, agregá `templates/`, `references/` o `scripts/`.
3. Sumar la fila de la skill al README y subir el conteo del bloque `verify` `skills-count`. Si no, `doc_verify` falla.
4. Correr los checks, los mismos que el CI y que bloquean el merge:
   ```bash
   python3 scripts/validate_skills.py
   python3 -m pytest skills -q
   python3 skills/agent-ready-project/scripts/doc_verify.py --root . --docs README.md
   ```
5. Commit y push con paths explícitos: `git add README.md skills/<nombre>/ && git commit -m "feat: add <nombre> skill" && git push`.
6. Verificar que el tap la resuelve: `hermes skills inspect <owner>/<repo>/skills/<nombre>`. No uses `search`, que solo cubre el catálogo oficial y no los taps.
7. Propagar a los perfiles: `hermes skills install <owner>/<repo>/skills/<nombre>` o symlink. Para otros perfiles, agregá el tap con `hermes --profile <p> skills tap add <owner>/<repo>`.

Supuesto: el tap ya está creado y agregado a tu perfil.

## Pedido 3

Ese error es conocido: el install resuelve a través de skills.sh externo y es frágil a eso, no al contenido de tu repo. Si `inspect` resuelve y la skill está commiteada, el problema no es tuyo. No lo reintentaría en loop contra el mismo error.

Instalación manual:

```bash
mkdir -p ~/.hermes/skills/<name>
cp -r <repo>/skills/<name>/SKILL.md <repo>/skills/<name>/templates ~/.hermes/skills/<name>/
```

Hacelo igual en cada perfil adicional, en `~/.hermes/profiles/<p>/skills/<name>`. Copiá también `templates/` y cualquier otro subdirectorio que tenga la skill. Después verificá con `ls` en el perfil que quedó todo.

Alternativa mejor si el tap es tuyo: un symlink, que evita tanto el install como el drift:

```bash
ln -sfn <repo>/skills/<name> ~/.hermes/skills/<name>
```

Supuesto: el perfil destino es el default y la skill ya está pusheada al repo.
