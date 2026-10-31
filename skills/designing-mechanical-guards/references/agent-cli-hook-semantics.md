# Hooks de agente como guardas: qué evento puede hacer qué

Cuando una guarda se implementa como *hook* de un CLI de agente (Claude Code, Hermes,
Qwen, Kimi, OpenCode, Antigravity), la misma intención tiene mecanismos distintos en cada
uno. Elegir el evento equivocado produce el fallo más caro de esta clase: **la guarda queda
instalada, registrada y en verde, y no puede hacer lo que promete**.

Antes de portar o escribir un hook, decidí por intención y después buscá el evento que la
sostiene en ESA herramienta. No copies el nombre del evento de la otra.

## Tabla de decisión (por intención)

| Querés… | Necesitás un evento que… | En Claude Code | En Hermes |
|---|---|---|---|
| impedir una acción (escribir en el ERP, `rm`, `git push`) | pueda **bloquear** y devolver el motivo al agente | `PreToolUse` (exit 2) | `pre_tool_call` (exit 2, o `{"action":"block"}`) |
| avisar después de una escritura, sin bloquear | pueda **reescribir lo que el modelo lee** | `PostToolUse` (exit 2 llega por stderr) | **no existe como hook de shell**: hay que usar `transform_tool_result` de plugin |
| inyectar contexto al empezar | pueda **agregar** texto al prompt | `SessionStart` | `pre_llm_call` (dispara por turno) o sección de system prompt |
| frenar el cierre del turno con trabajo suelto | corra **antes de aceptar la respuesta final** | `Stop` | `pre_verify` (acepta `{"decision":"block"}` como "seguí") |

Regla dura: **si el evento no es de bloqueo, su `stderr` no llega al agente.** En Hermes
solo `pre_tool_call` está en el conjunto de bloqueo; en `post_tool_call` el `stderr` va al
log. Un hook de `post_tool_call` que "avisa" con exit 2 es una guarda apagada que se ve
encendida.

## El payload no viaja igual entre herramientas

No alcanza con que el evento exista: los campos cambian de nombre y de lugar.

- Hermes manda `hook_event_name`, `tool_name`, `tool_input`, `session_id`, `cwd`, `profile`
  y **todo lo demás bajo `extra`**: `final_response`, `changed_paths`, `attempt`, `coding`.
  Las herramientas de archivo reciben el destino en `path` (no en `file_path`).
- Claude Code manda `file_path`, `last_assistant_message`, `stop_hook_active` arriba.

Portar un hook entre herramientas sin traducir el payload deja el script corriendo sobre
cadenas vacías: mira y no ve nada. La traducción va en **una función del módulo que tiene la
lógica** (con su test), nunca duplicada en el wrapper `.sh`.

## Los interruptores que fallan en silencio

Cada herramienta tiene puertas propias entre "escribí el hook" y "el hook corre". Todas
fallan sin ruido:

- **Hermes**: consentimiento de primer uso por `(evento, comando)` en
  `shell-hooks-allowlist.json`. Sin él, el hook **se saltea en silencio**. Se aprueba con
  `hermes hooks test <evento>`, `HERMES_ACCEPT_HOOKS=1` o `hooks_auto_accept: true`, y se
  verifica con `hermes hooks list` (columna de allowlist) y `hermes hooks doctor`
  (exec bit, mtime, JSON, corrida sintética).
- **Hermes, plugins de proyecto**: `./.hermes/plugins/` solo se descubre con
  `HERMES_ENABLE_PROJECT_PLUGINS=1`, **y además** el plugin tiene que estar en
  `plugins.enabled`. Dos puertas, las dos silenciosas. Alternativa con una sola puerta: el
  directorio de plugins del usuario + un enlace al directorio del repo, así la fuente sigue
  versionada en un solo lugar.
- **Config de máquina**: el registro del hook vive en la config del usuario, no en el repo.
  Eso hace que un `git clone` nuevo no lo tenga. La guarda del repo tiene que poder decir
  "está registrado" leyendo esa config (mismo patrón que cualquier guarda sobre estado de
  máquina).

## Cómo se verifica un hook (no se lee, se corre)

Un hook versionado + registrado + reportado en verde **no prueba que el comando resuelva**.
El test tiene que:

1. Arrancar el wrapper real con un intérprete real (`sh <ruta>`) y un payload **de la forma
   que manda esa herramienta**, no de la otra.
2. Mirar código de salida y `stdout` esperados (vacío cuando no hay nada que decir).
3. Dejar una línea en el log del hook por corrida, para tener el **denominador**: prueba que
   corrió aunque no tuviera nada que avisar.

Y cuando la guarda tiene un modo de medición (sombra: registra y no bloquea), el test cubre
el modo sombra y la promesa de "no frena"; el mapeo de campos se cubre con un test puro de
la función que traduce. No hace falta un caso end-to-end que fuerce el bloqueo.

## Cuando la guarda te mira a vos

Si tu entregable es un archivo que el propio gate del repo parsea (un plan, una validación,
un índice), **corré ese chequeo sobre tu archivo antes de darlo por terminado** y mirá el
mensaje: los parsers de front matter suelen no ignorar comentarios en línea, así que un
valor con `# comentario` al lado se lee como valor inválido. Escribí el front matter limpio
y dejá el porqué en el cuerpo.
