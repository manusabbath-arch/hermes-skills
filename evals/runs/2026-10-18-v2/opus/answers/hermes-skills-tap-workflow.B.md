## Pedido 1

Es normal: cuando instalás una skill desde un tap, Hermes copia los archivos a tu perfil (por ejemplo `~/.hermes/skills/<nombre>/`). No queda un link al repo, así que editar el repo no cambia lo instalado.

Para traer la versión nueva:

1. Asegurate de que el cambio esté commiteado **y pusheado** a la rama que usa el tap (normalmente `main`). Si quedó solo en local, el tap no lo ve.
2. Actualizá la skill en tu perfil:
   ```bash
   hermes skills update <nombre>
   ```
   Si tu versión de Hermes no tiene `update` o no detecta el cambio, reinstalá forzando:
   ```bash
   hermes skills uninstall <nombre>
   hermes skills install <tap>/<nombre>
   ```
3. Si hay caché del índice del tap, refrescalo (por ejemplo `hermes skills tap update` o volviendo a agregar el tap) antes de reinstalar.
4. Abrí una sesión nueva de Hermes: las skills se cargan al iniciar, una sesión abierta sigue usando la vieja.

Para verificar, compará el `SKILL.md` en `~/.hermes/skills/<nombre>/` con el del repo (`diff`).

Supuesto: usás el directorio de skills por defecto; si tenés un perfil o `HERMES_HOME` distinto, mirá ahí.

## Pedido 2

Pasos típicos para publicar una skill nueva en el tap:

1. **Rama nueva** en el repo del tap: `git checkout -b add-mi-skill`.
2. **Crear la carpeta** `skills/<nombre>/` con el nombre en kebab-case, igual al `name` del frontmatter.
3. **Escribir `SKILL.md`** con frontmatter válido:
   ```yaml
   ---
   name: mi-skill
   description: Qué hace y cuándo usarla, en una o dos frases.
   ---
   ```
   Después, el cuerpo con las instrucciones. Si necesitás scripts o referencias, ponelos en subcarpetas (`scripts/`, `references/`).
4. **Actualizar el índice o la documentación** del tap si existe (README con la lista de skills, el conteo de skills, un `index.json` o similar). Muchos taps validan esto en CI.
5. **Correr las validaciones locales** que tenga el repo (lint, verificación de docs) antes de pushear.
6. **Probar la instalación** desde tu rama o en local: instalala en tu perfil y abrí una sesión nueva para confirmar que Hermes la detecta y la dispara bien.
7. **Commit, push y PR**. Esperá a que el CI pase y mergeá a `main`.
8. Una vez mergeada, cualquiera puede instalarla con `hermes skills install <tap>/mi-skill`.

## Pedido 3

Ese error significa que el instalador no pudo bajar la skill de ninguna fuente configurada (red, proxy, rate limit de GitHub, tap mal registrado o nombre/ruta incorrectos). Podés instalarla a mano:

1. **Cloná el repo del tap** (o bajá el ZIP):
   ```bash
   git clone https://github.com/<owner>/<tap>.git /tmp/tap
   ```
2. **Copiá la carpeta de la skill** a tu directorio de skills:
   ```bash
   cp -r /tmp/tap/skills/<nombre> ~/.hermes/skills/<nombre>
   ```
3. Verificá que `~/.hermes/skills/<nombre>/SKILL.md` exista y que el `name` del frontmatter coincida con la carpeta.
4. Abrí una sesión nueva de Hermes y confirmá que aparece (`hermes skills list`).

Antes de eso conviene revisar la causa: que el tap esté bien agregado (`hermes skills tap list`), que el nombre de la skill sea exacto, que tengas salida a GitHub, y si hay rate limit, exportar `GITHUB_TOKEN`. Si el repo es privado, el instalador necesita credenciales; clonar con tu acceso de git lo evita.

Ojo: instalada a mano, `hermes skills update` puede no reconocerla como del tap. Para actualizarla, repetí la copia.

## Pedido 4

El chequeo `skills-count` de `doc_verify` compara la cantidad de skills que hay realmente en `skills/` con el número que declara la documentación (típicamente el README, algo como "N skills" o una tabla o lista de skills). Agregaste una carpeta nueva, así que el conteo real subió en uno, pero el número documentado quedó igual, y por eso falla.

Cómo arreglarlo:

1. Abrí el README (o el archivo de docs que valide el script) y actualizá el número total de skills.
2. Si hay una tabla o lista de skills, agregá la fila de la nueva con su nombre y descripción.
3. Corré el verificador en local antes de pushear (por ejemplo `python scripts/doc_verify.py` o el comando que use el workflow) y confirmá que pasa.
4. Commit y push; el CI debería quedar verde.

Si el número ya está bien y sigue fallando, revisá que no haya carpetas extra en `skills/` (una vacía, una sin `SKILL.md`, o una de prueba) que el script esté contando o ignorando de forma distinta a la que esperás.

## Pedido 5

El problema es la discrepancia entre el nombre de la carpeta y el `name` del frontmatter. Hermes (y la mayoría de los validadores de skills) espera que sean **idénticos**: carpeta `skills/mi-skill/` con `name: mi-skill`. Con `MiSkill/` vs `mi-skill`, el instalador busca `skills/mi-skill/`, no la encuentra (en Linux las rutas distinguen mayúsculas) o la descarta por inválida.

Solución:

```bash
git mv skills/MiSkill skills/mi-skill
```

En macOS o Windows, con filesystem que no distingue mayúsculas, hacelo en dos pasos:

```bash
git mv skills/MiSkill skills/tmp && git mv skills/tmp skills/mi-skill
```

Además:

- Usá kebab-case en minúsculas (letras, números y guiones) tanto en la carpeta como en `name`.
- Actualizá cualquier referencia en el README o índice.
- Commit, push, y reinstalá: `hermes skills install <tap>/mi-skill`.
- Abrí una sesión nueva para que la cargue.

## Pedido 6

Tenés dos caminos:

**Desde la web:** entrá a https://github.com/new, elegí el dueño y el nombre, poné si es público o privado, opcionalmente un README, `.gitignore` y licencia, y tocá "Create repository".

**Desde la terminal con GitHub CLI** (`gh`, logueado con `gh auth login`):

```bash
gh repo create mi-repo --public --clone
```

Si ya tenés un proyecto local con git:

```bash
cd mi-proyecto
gh repo create mi-repo --private --source=. --push
```

Eso crea el repo en GitHub, agrega el remote `origin` y pushea tu rama.
