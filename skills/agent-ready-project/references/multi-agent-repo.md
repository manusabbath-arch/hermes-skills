# Varios agentes sobre el mismo repo — referencia

Detalle de la sección "Varios agentes sobre el mismo repo" de `agent-ready-project`.
**Origen:** proyecto NG (2026): seis consumidores (Claude Code, Hermes, OpenCode,
Qwen Code, Kimi Code, Antigravity) escribiendo el mismo repo, en Windows, con
`core.autocrlf=true` y un pre-commit que corre la suite. Cada punto tiene el
incidente medido que lo originó.

## 1. Aislamiento: un worktree y una rama por sesión

- `git worktree add -b <agente>/<tema> ../<repo>-<agente> main`. El prefijo es el
  agente; el tema dice qué se hace, no cuándo.
- **El árbol principal es de integración, no de trabajo.** Ahí viven el trabajo sin
  commitear y el índice de otra sesión: un `checkout`, `stash`, `reset` o `restore`
  destruye trabajo ajeno.
- **Integrar siempre igual:** en el worktree `git rebase main` (rama privada, sin
  empujar) → compuerta sin regresiones → desde integración `git merge --ff-only
  <rama>` → `git status --short` idéntico antes y después. Sin merge commits en el
  árbol de integración (se llevan el índice ajeno), sin `--no-verify`.
- **Archivos de alto conflicto se tocan al final**, ya rebasado (índice, línea base
  de checks, el CLI central). El sellado de la línea base lo hace una sola sesión.
- **Al integrar se limpia:** `git worktree remove` + `git branch -d`.
- **El push lo decide una persona** — es hacia afuera y no se deshace. Antes:
  `git log origin/main..main` y revisar qué archivos **agregó** cada commit del rango
  (también los que un commit posterior borró: viajan igual en el historial).

## 2. Worktree que crea la herramienta: HEAD detached

Algunas herramientas crean su propio worktree en **HEAD detached**. Ahí un commit
sale con exit 0 y **no queda en ninguna rama**: se pierde al desmontar el worktree
(salvo reflog), y `git status` se ve normal. Primer paso de una sesión cuyo
worktree no creó ella: `git switch -c <agente>/<tema>`.

Sostén mecánico: un chequeo que pone rojo el worktree detached **con commits que
ninguna rama alcanza** (lo único irreversible) y solo reporta los estados benignos
(detached contenido en una rama; rama integrada sin limpiar). La lista de prefijos
de agente y la de consumidores con guardas son **el mismo conjunto**, fijado por
test: una herramienta nueva no puede quedar afuera de una en silencio.

## 3. Commits con dos sesiones vivas

- **Siempre con pathspec:** `git add <rutas>` y `git commit -- <rutas>`. Nunca
  `add -A`, `add .` ni `commit -a`. Medido: un `commit -F msg` sin pathspec arrastró
  29 borrados que había dejado preparados otra sesión.
- **Nunca `--amend` sobre un commit que no hizo esta sesión**, ni sobre uno empujado.
  Antes de commitear, `git log --oneline -3` y `git status`: el HEAD puede no ser el
  que dejaste; `git reflog` muestra un `(amend)` ajeno.
- **Si un commit ajeno se llevó trabajo tuyo**, no rebasear para desenredarlo con la
  otra sesión activa: se declara en el mensaje del commit siguiente.
- **Un wrapper de commit atómico** (`add + commit` con pathspec, rechazo de stage
  ajeno, mensaje desde archivo con ruta nativa) cierra las ventanas de carrera mejor
  que la disciplina.
- **`git commit -- <paths>` exporta `GIT_INDEX_FILE` y `GIT_AUTHOR_*`** a los
  subprocesos del hook: los tests que arman un repo en `tmp_path` commitean contra
  el índice del repo real. Los tests (y el módulo bajo prueba) que corren `git` sobre
  otro repo limpian esas variables del entorno.

## 4. Locks, stat-cache y fin de línea

- **`.git/index.lock` no se borra sin verificar que no haya un `git` vivo.** Un
  pre-commit lento + un timeout corto del agente deja el lock huérfano con el índice
  escrito. Contar procesos `git` excluyendo los propios de la sesión.
- **` M` en `git status` con `git diff` vacío no es un cambio:** es el stat-cache
  desalineado por `autocrlf`. La prueba es `git hash-object --path=<f> <f>` contra
  `git rev-parse HEAD:<f>`, no el diff.
- **El fin de línea es por archivo y puede cambiar entre commits** (otra sesión lo
  reescribió). Detectarlo en el momento: `NL = "\r\n" if "\r\n" in s else "\n"`.
  Editar por script: leer con `newline=""` → `replace` con `assert s.count(ancla) == 1`
  **antes** de escribir → escribir con `newline=""`. Nunca "normalizar" un archivo.
- **Nunca `cat >>`/heredoc ni `sed -i` sobre un archivo versionado:** en una sesión,
  tres veces: LF en un `.py` CRLF (dos) y un `"\x00"` en un heredoc que llegó al
  fuente como byte NUL. Herramienta de edición, o script escrito en un archivo que
  preserve el fin de línea. Un chequeo `sin_fin_de_linea_mezclado` lo frena.
- **Hashes de archivos extraídos con `autocrlf`:** un `SHA256SUMS` que coincide con
  el blob de git puede no verificar **en disco**. Marcar datos crudos `-text` en
  `.gitattributes` y testear el sha en disco.

## 5. Guardas por consumidor, cobertura medida

- La regla es del repo, no de la herramienta: **cada** consumidor que pueda ejecutar
  la acción peligrosa necesita su guarda física (hook de Claude Code, hook envuelto
  para forks, plugin, wrapper que **traduce** el contrato de otro agente).
- **La cobertura sale de un comando, nunca de la prosa:** `guardas` lista cada
  consumidor con su denominador, y un chequeo pone rojo si alguno queda sin hook.
- **Un agente nuevo entra a la lista con su guarda antes de recibir tareas**, no
  después.
- **Una capacidad del agente que el repo no usa es una que nadie declaró:** una
  skill instalada en el directorio de usuario (`AppData`, `~/.x/skills`) es una copia
  que ninguna guarda ve. Si el agente soporta skills a nivel proyecto, van al repo.
- Hay condiciones que decide la máquina y no el repo (trust de directorio,
  allowlist del hook) y fallan en silencio devolviendo `[]`. Se escriben como paso
  de instalación que el usuario aprueba.
- **El escaneo de secretos recorre el disco, no `git ls-files`:** un `node_modules`
  que dejó otra herramienta (3.437 archivos) produjo 70 hallazgos ajenos y bloqueó
  todos los commits. Excluir por nombre de directorio y testear que el denominador
  siga siendo el repo.

## 6. Agentes que se hablan entre sí

- **Un prompt entre agentes no es la confirmación de una persona.** Si A le pide a B
  una escritura en producción, el hook de B corta igual; si no corta, es un hueco del
  hook, no un permiso.
- Quien recibe la orden trabaja en su propio worktree y rama.
- Lo que se delega viaja con su fuente y fecha; los datos de terceros no se pegan en
  un prompt entre agentes.
- **Un consejo de otra sesión se mide antes de repetirlo:** un procedimiento correcto
  puede traer un paso de más (un shim, un cambio de política) que después hay que
  desaprender.

## 7. Sesiones sin shell y el punto de recogida

Un agente con solo acceso a archivos (sin terminal) escribe en el árbol pero no puede
commitear ni correr la compuerta. Dos reglas:

- **Del lado sin shell:** cada archivo pendiente se anota en `pendientes-de-commit.md`
  con ruta, fecha y **el requisito que le falta** ("falta el enlace en el índice",
  "falta el sello") — nunca un veredicto propio de "completo", porque quien escribe
  no puede correr los chequeos.
- **Del lado con shell:** antes de tocar nada, leer ese archivo y procesar primero.
  **La entrada vence:** si sobrevive a una segunda sesión con shell, se procesa o se
  descarta con motivo; una lista sin vencimiento se pudre.

## 8. Identidad de quién commitea

Medido: 596 de 807 commits firmaban `Test` (un `user.name` en el `.git/config` del
árbol). "¿Qué agente hizo esta rama?" no tenía respuesta. Resolver la firma en orden:
variable declarada en la config versionada del consumidor → variable que el agente ya
exporta (`AI_AGENT`, `OPENCODE_CLIENT`) → `user.name`. Mostrar la firma antes de
commitear. El modelo, si no está en el entorno, no se completa a mano.

## 9. Tests bajo contención

- **Un test no puede medir la máquina.** Uno que suponía que un proceso arrancaba en
  <1 s tardó 4–8 s bajo `-n auto` en el pre-push y bloqueó el push entero. Medir el
  plazo desde que el proceso **ya arrancó**, no desde el `Popen`.
- **Antes de reportar un rojo de un test que lanza un shell**, correr ese archivo
  solo en el mismo clon. Si pasa, es contención: se declara; subir el timeout a
  ciegas solo mueve el umbral.
- **Pre-commit por niveles:** los tests que el commit puede haber roto (~60 s) en el
  commit; la suite entera (~8 min) en pre-push. Con varias sesiones, la suite lee
  también los archivos sin trackear de otra: el worktree propio aísla ese rojo.
- **`subprocess` con `text=True` en Windows:** un binario nativo escribe en la página
  de códigos de la consola; el `UnicodeDecodeError` ocurre en el hilo lector, `stdout`
  queda `None` y el test muere **antes de su aserción**, apuntando al lugar
  equivocado. Leer bytes y decodificar explícito con `errors="replace"`.
