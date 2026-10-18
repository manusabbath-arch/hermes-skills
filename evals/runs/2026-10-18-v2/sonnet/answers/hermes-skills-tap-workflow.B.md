## Pedido 1

Supuesto: el repo tap es un repo de GitHub y tu perfil de Hermes instaló la skill desde ahí. Editar el repo no actualiza el perfil automáticamente: la instalación es una copia local.

Qué haría:
1. Confirmar que el cambio esté commiteado y pusheado a la rama que usa el tap (normalmente `main`). Si quedó solo en local, el perfil nunca lo va a ver.
2. Actualizar la skill instalada. Primero probaría `hermes skills update` (o `hermes skills list` para ver el estado). Si no detecta el cambio, reinstalar forzando: `hermes skills install <nombre> --force`.
3. Si el tap se cachea, refrescarlo (`hermes skills tap update` o quitar y volver a agregar el tap) y reintentar.
4. Verificar que el perfil correcto sea el que está activo, porque cada perfil tiene su propio directorio de skills.
5. Reiniciar la sesión de Hermes: las skills se cargan al iniciar.

Los nombres exactos de los subcomandos pueden variar según tu versión; `hermes skills --help` te los confirma.

## Pedido 2

Supuesto: el tap es un repo Git con las skills en `skills/<Carpeta>/SKILL.md`.

Pasos:
1. Crear la carpeta `skills/<NombreSkill>/` con un `SKILL.md` que tenga frontmatter YAML (`name`, `description`, y lo que pida el formato) y el cuerpo con las instrucciones.
2. Hacer que `name` sea en minúsculas con guiones y que coincida con la carpeta o con la convención del repo.
3. Agregar archivos auxiliares (scripts, referencias) dentro de la misma carpeta si hacen falta.
4. Actualizar la documentación que lleva la cuenta de skills (README, índice, contador de skills). Si el CI verifica que esos números coincidan, hay que actualizarlos a mano.
5. Correr localmente las validaciones del repo, si existen.
6. Crear una rama, commit, push y abrir un PR. Esperar a que el CI pase y mergear a `main`.
7. En Hermes: `hermes skills tap add <owner>/<repo>` (si todavía no lo agregaste) y `hermes skills install <nombre>`.

## Pedido 3

"Could not fetch from any source" significa que Hermes no pudo bajar la skill de ninguno de los orígenes configurados. Causas típicas: el tap no está agregado, hay un problema de red o proxy, el repo es privado y falta autenticación, o el nombre no coincide.

Cómo instalarla igual, a mano:
1. Clonar el repo del tap: `git clone https://github.com/<owner>/<repo>.git`. Si es privado, usar un token o SSH.
2. Copiar la carpeta de la skill (`skills/<Carpeta>/`) al directorio de skills de tu perfil de Hermes. Suele estar bajo `~/.hermes/skills/` o en el directorio del perfil activo. Lo confirmaría con `hermes skills list` o la documentación.
3. Verificar que `SKILL.md` quede en la raíz de esa carpeta copiada.
4. Reiniciar Hermes y comprobar con `hermes skills list`.

En paralelo, diagnosticaría la causa: `hermes skills tap list`, probar `git ls-remote` contra el repo, revisar el proxy y el token.

## Pedido 4

Supuesto: el repo tiene un paso de CI (`doc_verify`) que compara la cantidad real de skills con la cantidad declarada en la documentación.

El error `skills-count` aparece porque agregaste una skill y el número escrito en los docs (README, índice o badge) ya no coincide con la cantidad real de skills en `skills/`. El verificador cuenta las carpetas con `SKILL.md` y compara con el valor documentado.

Solución:
1. Contar las skills reales (por ejemplo `ls skills | wc -l`, o los `SKILL.md` que haya).
2. Actualizar el contador en cada lugar donde aparece. Busco el número viejo con grep en README y docs.
3. Agregar la skill nueva a las listas o tablas de la documentación si existen.
4. Volver a correr `doc_verify` localmente, si hay script, y pushear.

Si ya actualizaste el número y sigue fallando, revisaría que la skill nueva tenga un `SKILL.md` válido y que no haya otra carpeta que se cuente de más.

## Pedido 5

Lo más probable es que el problema sea el desajuste entre el nombre de la carpeta (`MiSkill`) y el `name` del frontmatter (`mi-skill`). Muchos instaladores buscan la skill por el nombre de la carpeta o exigen que coincidan, y por eso no la encuentran al instalar.

Qué haría:
1. Alinear ambos: renombrar la carpeta a `skills/mi-skill/`, que es la convención en minúsculas con guiones, y dejar `name: mi-skill`.
2. Comprobar que `SKILL.md` esté directamente dentro de la carpeta y que el frontmatter sea YAML válido, con `---` al inicio y al final.
3. Commit y push, refrescar el tap y reintentar `hermes skills install mi-skill`.

Otras causas posibles: la rama no se mergeó, o el tap está cacheado. Tendría que verlo en tu repo para confirmarlo, así que asumo que es el desajuste de nombres.

## Pedido 6

Hay dos caminos.

Desde la web:
1. Entrá a github.com e iniciá sesión.
2. Hacé clic en el botón "+" arriba a la derecha y elegí "New repository".
3. Ponele un nombre, una descripción opcional y elegí si es público o privado.
4. Opcional: marcá "Add a README", `.gitignore` y licencia.
5. Hacé clic en "Create repository".

Desde la terminal con GitHub CLI:
```
gh repo create mi-repo --public --clone
```
Usá `--private` si querés que sea privado. Para subir un proyecto local ya existente, desde su carpeta: `gh repo create mi-repo --source=. --public --push`.

Con Git a mano: creá el repo vacío en la web y después `git remote add origin <url>`, `git push -u origin main`.
