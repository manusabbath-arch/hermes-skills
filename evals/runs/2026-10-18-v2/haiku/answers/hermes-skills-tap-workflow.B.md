## Pedido 1

Lo más probable es que tu perfil de Hermes tenga una copia instalada de la skill, y esa copia no se actualiza sola cuando editás el repo tap. Editar el repo solo cambia el código fuente; hay que publicar el cambio y después traerlo al perfil.

Supuesto: no tengo el detalle exacto del CLI de tu versión, así que los comandos son orientativos.

Lo que haría:
1. Confirmar que el cambio está commiteado y mergeado en la rama que usa el tap (normalmente `main`). Si está en una rama o en un PR sin mergear, el tap no lo ve.
2. Ver de dónde viene la skill instalada en el perfil (un listado de skills del CLI o la ruta de instalación), para confirmar origen y versión.
3. Actualizar la skill: `hermes skills update <nombre>` si tu versión lo tiene; si no, desinstalarla y volver a instalarla desde el tap.
4. Verificar que el contenido del `SKILL.md` instalado ya es el nuevo.
5. Si el tap tiene caché local, refrescarlo antes de instalar.

Si sigue vieja, revisá que estás mirando el perfil correcto, porque Hermes puede tener varios perfiles.

## Pedido 2

Pasos que seguiría:
1. Crear la carpeta `skills/<nombre>/` con un `SKILL.md` que tenga frontmatter (`name`, `description`, etc.). El `name` es el identificador con el que se instala la skill.
2. Agregar dentro de la misma carpeta los archivos de apoyo que necesite.
3. Si el repo mantiene un índice, un README con listado o un contador de skills, agregar la nueva ahí.
4. Correr localmente las verificaciones del repo (validación o `doc_verify`) antes de pushear.
5. Crear una rama, commitear, pushear y abrir un PR.
6. Esperar CI en verde y mergear.
7. Probar desde un perfil limpio: refrescar el tap e instalar la skill.

Supuesto: no conozco una guía de contribución específica del repo. Si existe un `CONTRIBUTING`, esa guía manda sobre estos pasos.

## Pedido 3

Supuesto: el mensaje "Could not fetch from any source" indica que Hermes no pudo acceder al tap. Las causas típicas son red o proxy, falta de autenticación si el repo es privado, o una URL o rama incorrecta.

Opciones:
1. Verificar acceso con `git clone` directo al repo del tap. Si falla, el problema es de red o de acceso, no de Hermes. Revisar también las variables de proxy (`HTTPS_PROXY`) y el token de GitHub si el repo es privado.
2. Si el clone funciona, copiar manualmente la carpeta de la skill a la ubicación de skills locales del perfil de Hermes, respetando la estructura `skills/<nombre>/SKILL.md`, y recargar el CLI si hace falta.
3. Si tu versión soporta instalar desde una ruta local o una URL directa, usar esa opción.
4. Revisar que la URL del tap y la rama sean las correctas.

Aclaro que la copia manual funciona pero no se actualiza sola. Para mantenerla al día, hay que repetir el proceso o volver a resolver el acceso al tap.

## Pedido 4

Supuesto: el paso `doc_verify` compara la cantidad de skills declarada en la documentación (por ejemplo un contador en el README o un índice) con la cantidad real de skills del repo. Si agregás una skill sin actualizar ese conteo, los números no coinciden y el CI falla.

Lo que haría:
1. Leer el log del CI para ver el valor esperado y el encontrado.
2. Actualizar el contador o el listado de skills en la documentación que revisa el script.
3. Confirmar que la nueva skill tiene su carpeta y un `SKILL.md` válido, así el conteo real es el correcto.
4. Correr el script de verificación localmente antes de pushear.

La idea general es que la documentación refleje la cantidad real de skills del repo.

## Pedido 5

Probablemente hay una de estas dos causas, o ambas:
- Carpeta y `name` no coinciden. La carpeta es `MiSkill` pero el `name` es `mi-skill`. En Linux los nombres distinguen mayúsculas y minúsculas, y el tap puede buscar por `name` o por carpeta.
- La skill no está registrada en el índice o manifiesto del tap, si el repo tiene uno.

Lo que haría:
1. Revisar el frontmatter de `SKILL.md`. El `name` debe ser el identificador que usás para instalar.
2. Usar una convención consistente: carpeta en minúsculas con guiones igual al `name`, por ejemplo `skills/mi-skill/`.
3. Si hay un índice o manifiesto, agregar la entrada de la skill.
4. Verificar que el frontmatter es YAML válido. Si está mal formado, la skill puede ignorarse sin mostrar error.
5. Refrescar el tap, volver a listar las skills disponibles y reinstalar para confirmar que aparece.

## Pedido 6

Desde la web:
1. Entrar a github.com e iniciar sesión.
2. Click en el "+" arriba a la derecha y elegir "New repository".
3. Poner el nombre, una descripción opcional y elegir público o privado.
4. Opcionalmente, agregar README, `.gitignore` y licencia.
5. Click en "Create repository".

Desde la terminal con la CLI `gh`: `gh repo create <nombre> --private` (o `--public`). Si ya tenés un repo local, `gh repo create <nombre> --private --source . --push` lo crea y sube el código.

Supuesto: tenés cuenta de GitHub y `gh` autenticado si vas por terminal.
