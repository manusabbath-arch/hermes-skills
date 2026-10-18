## Pedido 1

Supuestos: la skill ya está instalada desde el tap y editaste el repo del tap, pero no hiciste push, o Hermes no refrescó su copia. No tengo acceso a tu máquina, así que te digo qué verificaría, en orden.

1. Confirmar que el cambio llegó al remoto: `git status` y `git log origin/main..HEAD` en el repo del tap. Si hay commits sin pushear, `git push`. Hermes lee del remoto (GitHub), no de tu working copy local.
2. Revisar que la edición esté en la rama que usa el tap (normalmente la default) y que el `SKILL.md` conserve su frontmatter válido (nombre, descripción). Un frontmatter roto puede hacer que se ignore el cambio.
3. En Hermes, la skill instalada es una copia en tu perfil (típicamente bajo `~/.hermes/skills/`). No se sincroniza sola. Actualizá con `hermes skills update` (o `hermes skills check` primero para ver qué cambió). Si tu versión no lo soporta, reinstalá: `hermes skills uninstall <nombre>` y luego `hermes skills install <tap>/<nombre>`.
4. Si usás varios perfiles, asegurate de estar en el correcto (`hermes -p <perfil> skills ...`).
5. Comprobar con `hermes skills list` y abriendo el `SKILL.md` instalado que la versión nueva esté. Si no cambia, puede haber caché del índice del tap: volvé a correr el update o `hermes skills tap` para refrescar.

Aviso: si habías modificado la copia instalada a mano, un update puede pisarla o marcar conflicto; hacé backup antes.

## Pedido 2

Supuestos: el tap es un repo de GitHub que ya agregaste con `hermes skills tap add <owner>/<repo>`, y cada skill vive en su propia carpeta con un `SKILL.md`. Verificá los nombres exactos de comandos con `hermes skills --help`, porque pueden variar según versión.

1. Crear la carpeta de la skill en el repo del tap, con el layout que use el tap (por ejemplo `skills/<nombre-skill>/`). Nombre en minúsculas con guiones.
2. Escribir `SKILL.md` con frontmatter YAML (`name`, `description` clara de cuándo usarla, y metadatos que pida el formato) y debajo las instrucciones: cuándo aplica, pasos, ejemplos. Agregar scripts o referencias en subcarpetas si hacen falta, con rutas relativas.
3. Revisar que no haya secretos, rutas personales ni dependencias no declaradas.
4. Si el tap tiene un índice o manifiesto (README o lista de skills), registrar la nueva skill ahí.
5. Commit y push a la rama que consume el tap: `git add skills/<nombre> && git commit -m "Add <nombre> skill" && git push`.
6. Probar desde Hermes como si fueras un usuario nuevo: `hermes skills search <nombre>` o `hermes skills browse`, y luego `hermes skills install <tap>/<nombre>`. Probar que el agente la dispare con un pedido real.
7. Si algo falla, corregí, pusheá y actualizá con `hermes skills update`.

## Pedido 3

Supuestos: el error significa que Hermes no pudo resolver la skill en ningún origen configurado (tap mal escrito, repo privado sin credenciales, rate limit de GitHub, red/proxy, o ruta de la skill distinta a la esperada). No puedo ver tu entorno, así que va primero el diagnóstico rápido y después la instalación manual, que funciona igual.

Diagnóstico (1 minuto):
- `hermes skills tap list` para confirmar que el tap está agregado y con el `owner/repo` correcto.
- Si el repo es privado, necesitás un token de GitHub (`GITHUB_TOKEN`) exportado; sin eso GitHub devuelve 404 y Hermes lo reporta como "no se pudo traer".
- Si ves rate limit, también ayuda el token.
- Revisá que el identificador sea exactamente el que aparece en `hermes skills search`.

Instalación manual (siempre funciona):
1. `git clone https://github.com/<owner>/<tap-repo>.git /tmp/tap` (con credenciales si es privado).
2. Copiar la carpeta de la skill (la que contiene `SKILL.md`) al directorio de skills de tu perfil, normalmente `~/.hermes/skills/<nombre>/`: `cp -r /tmp/tap/skills/<nombre> ~/.hermes/skills/`. Para un perfil distinto, usá el directorio de ese perfil.
3. Verificar con `hermes skills list` que aparezca; si no, reiniciá la sesión de Hermes para que la recargue.

Contra: instalada así no queda registrada por el gestor, por lo que `hermes skills update` quizá no la actualice; repetí la copia cuando cambie.
