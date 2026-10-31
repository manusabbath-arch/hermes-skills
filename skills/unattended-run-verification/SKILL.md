---
name: unattended-run-verification
description: "Use when verifying an unattended run, a scheduled task, a cron job, or a Windows Task Scheduler job: whether it actually fires alone, whether a log that says done proves the artifact exists, print spooler versus exit 0, orphaned headless processes, listeners that look alive, and health items that measure the wrong leg of the job."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [scheduled-tasks, cron, unattended, verification, windows, spooler, health]
    category: software-development
    related_skills: [designing-mechanical-guards, agent-ready-project]
---

# Verificar una corrida sin nadie y su salida real

USAR cuando la pregunta es si algo corre solo y su salida sale de verdad: "dejo la PC
prendida y no voy, ¿se ejecuta todo y se imprime?", una tarea programada que salió "en
verde" sin resultado, o un trabajo que quedó sin entregar.

## Cuándo NO aplicarla

Si el pedido es cómo escribir un cron o una tarea programada (sintaxis, un trigger), se
responde **solo eso**, sin agregar un procedimiento de verificación de salida que nadie
pidió. Esta skill aplica cuando hay que **probar** que la corrida sola produce el artefacto.

## La regla que manda

**Un log que dice "hecho" prueba que el proceso aceptó el trabajo, no que el resultado
exista.** La respuesta a "¿corre mañana solo?" se arma con cuatro condiciones leídas de
la máquina y una prueba de la salida; nunca con el estado de la tarea ni con su último
renglón del log.

## Procedimiento

### 1. Qué turnos hay y cuándo

```
powershell.exe -NoProfile -Command "Get-ScheduledTask -TaskPath '\<Project>\*' | ForEach-Object {
  \$i = Get-ScheduledTaskInfo -TaskName \$_.TaskName -TaskPath \$_.TaskPath
  '{0} | State={1} | Last={2} | Next={3} | Result={4}' -f \$_.TaskName,\$_.State,\$i.LastRunTime,\$i.NextRunTime,\$i.LastTaskResult
  \$_.Principal.LogonType; \$_.Settings.StartWhenAvailable
}"
```

Sustituí `\<Project>\` por la carpeta real del planificador. Desde bash hay que escapar
`\$_`: la shell se come el `$` antes de que llegue a PowerShell. Se listan los turnos con
día y hora reales (`NextRunTime`), no con la intención del que los creó.

`LastTaskResult`: `0` corrió bien, `1` corrió y falló, `267011` (0x41303) **nunca
corrió**, `267014` (0x41306) la terminaron a la fuerza, `267009` (0x41301) corriendo
ahora. Un `LastRunTime` de `30/11/1999` es lo mismo que "nunca corrió".

En Linux/macOS el equivalente es `crontab -l` más el log del job, o `systemctl list-timers`
si vive en systemd. El mismo criterio: próxima ejecución real, último código, nunca el
nombre de la unidad.

### 1 bis. Si lo que se pide es contar turnos por cadencia

Cuando el número va a un informe ("¿cuántas diarias, cuántas semanales?"), la fuente es el
**tipo de programación**, nunca el nombre de la tarea: una llamada `...-diaria` puede estar
en "Semanal, lunes a viernes" y contarla por el nombre infla el diario. `schtasks /query /v
/fo LIST` trae `Tipo de programación` con el detalle (`Diariamente`, `Semanal, lunes a
viernes`, `Mensual, primer lunes`) y `Próxima ejecución` con el turno real.

Dos trampas al leerlo desde bash:

- La salida de `schtasks` viene en la página de códigos del sistema (cp1252 en un Windows en
  español) y los acentos del encabezado llegan rotos: se busca por subcadena sin acento
  (`rogramaci`) o se parsea en Python con `encoding="cp1252"`, no se grepea la palabra
  acentuada. Un grep que no encuentra nada parece "no hay tareas".
- La ruta del planificador no se arma por interpolación en la shell: `"\\Folder\\$n"` llega
  con la barra duplicada y el `$n` sin expandir, y la respuesta es "no existe la tarea". Se
  pasa el nombre exacto, o se arma en Python con `chr(92)`.

El conteo se declara con su comando y su fecha, y separa **nunca corrió** del total: una tarea
mensual con `LastTaskResult` `267011` es una intención, no una tarea mensual.

### 1 ter. Un trabajo que agendás desde el agente no corre hasta que el planificador está vivo

Crear el trabajo devuelve `next_run_at` con día y hora, y **eso es una intención, no un turno**:
si el servicio que dispara los trabajos del agente no está corriendo, el trabajo queda guardado
y no se dispara nunca. Antes de decirle a alguien "a las 12:35 lo corro solo", leé el estado
del planificador y decí las dos cosas que midió: la tarea está registrada, y no hay proceso —
o sea que no va a correr hasta que eso arranque. La alternativa que sí depende de dos personas
es la más honesta: que te escriba y lo corrés en el momento.

Para un trabajo determinista —correr un comando y resumir su salida— va el modo sin agente con
un script propio: no inventa nada, su salida se entrega tal cual y queda igual de auditable que
un turno a mano. Ahí la forma del script es parte del contrato: la salida vacía no manda nada
(sirve de vigilante) y un código distinto de cero sí avisa, así que se elige de antemano si el
script imprime siempre o solo cuando tiene algo que decir. Y probalo antes contra una salida
capturada de verdad: un resumen que se arma parseando la salida del CLI se valida con una
corrida real, no con un caso inventado.

### 2. Las condiciones que deciden si corre

| Condición | Dónde se lee | Cómo se rompe |
|---|---|---|
| Sesión abierta | `Principal.LogonType` | `Interactive` = necesita el usuario logueado: pantalla bloqueada alcanza, un reinicio (Windows Update) deja la máquina sin nadie y no corre nada |
| Turno perdido | `Settings.StartWhenAvailable` | en `False`, apagada o dormida a la hora del turno no se recupera |
| Despertar | `Settings.WakeToRun` | en `False`, dormida no despierta |
| Energía | `powercfg /query SCHEME_CURRENT SUB_SLEEP` | `STANDBYIDLE`/`HIBERNATEIDLE` en `0x00000000` es "nunca", pero **por corriente**: lo que vale en AC puede no valer con batería |
| Tapa | `powercfg /query SCHEME_CURRENT SUB_BUTTONS` (`LIDACTION`) | cerrar la tapa puede suspender y matar el turno |

`(Get-CimInstance Win32_Battery).BatteryStatus` = `2` es enchufada. Si `LIDACTION` no
devuelve nada, el dato no se tiene: se dice así y se pide no cerrar la tapa, en vez de
suponer que no hace nada.

### 3. Si la salida salió de verdad

Para papel, el spooler es la evidencia:

```
Get-Printer | Where-Object Name -like '*<modelo>*' | Select Name,PrinterStatus,WorkOffline,DetectedErrorState,PortName
Get-PrintJob -PrinterName '<cola exacta>'
Get-NetIPAddress -AddressFamily IPv4     # subred de la máquina AHORA
netsh wlan show interfaces               # SSID, para saber en qué red está
```

Para archivos, la evidencia es el archivo con su fecha y tamaño, no la línea del log.

### 3 ter. Cuando el artefacto lo produce un proceso externo (navegador headless, exportador, impresora virtual)

Cuatro reglas, y cada una tapa un modo de "el archivo está" que no es "esta corrida lo hizo":

- **Borrar el destino antes de producir.** Un archivo de la corrida anterior en la misma carpeta
  pasa por nuevo: un `return pdf.exists()` devuelve verdadero con el de ayer, y la guarda de arriba
  lo cuenta como entregado. Se borra antes de arrancar y se da por bueno solo con tamaño mayor que
  cero.
- **Al vencer el tope, matar el árbol, no el lanzador.** Un navegador headless arranca por un
  proceso que es un pasamanos (`chrome.exe`): matar ese deja viva la instancia que hace el trabajo,
  y el archivo aparece minutos después del corte —huérfano en la carpeta de entregables— mientras
  la corrida ya declaró el fallo. `taskkill /F /T /PID` en Windows (desde git-bash no va: MSYS se come las barras y `taskkill //PID` llega inválido — se mata con `powershell -NoProfile -Command "Stop-Process -Id <pid> -Force"`), `killpg` fuera.
- **Un directorio de bloqueo propio por intento.** Un `--user-data-dir` (o cualquier carpeta de
  lock) fijo y compartido hace que el reintento espere el candado del proceso anterior y se cuelgue
  igual que el primero: el reintento solo sirve con un temporal por intento, borrado al salir.
- **El código de salida tiene que decir lo mismo que el artefacto.** Terminó sin escribir el
  archivo es fallo, no éxito mudo; y el rojo que eso levanta es correcto: no se declara para
  destrabar commits, se arregla el productor.

La contracara, al verificar: **un artefacto que aparece DESPUÉS de que la corrida declaró el fallo
no la reivindica.** Su hora posterior al cierre prueba que un hijo sobrevivió y lo escribió tarde y
sin dueño; no que la corrida salió bien. Se compara la hora del archivo con la ventana de la
corrida antes de creerle a la guarda o al log —los dos pueden estar en lo cierto a la vez— y lo que
se reporta es que el trabajo se hizo, que nadie lo tomó, y qué lo impidió.

### 3 bis. Si lo que tiene que quedar vivo es un escucha (bot, long poll, consumidor de cola)

Un proceso que existe no es un proceso que trabaja. La guarda que pregunta "¿hay un
python/worker corriendo el comando?" queda en verde con el trabajador colgado antes del bucle,
y mientras tanto la cola de entrada se llena y nadie contesta.

La evidencia no es el proceso ni su log, es **la fuente**:

- **El pendiente que declara la fuente.** En un bot de mensajería es el pending-update count;
  en una cola, su profundidad. Si hay proceso y el pendiente no baja en minutos, el escucha no
  está consultando: está trabado antes del bucle, no ocupado.
- **Un latido que escribe el propio trabajador en cada vuelta** (cuándo, cuántos ítems trajo,
  cuál fue el último) y que la guarda lee con un umbral mayor que el intervalo de consulta (un
  long poll tarda hasta 50 s; 10 minutos son diez vueltas perdidas, no un bache). La vuelta sin
  novedades **también** deja latido: "pregunté y no había nada" no es lo mismo que "no
  pregunté".
- **Escribilo fuera de los árboles de trabajo** (un archivo compartido en la carpeta de datos,
  no en `logs/` del repo): el canal es uno solo y la guarda puede correr desde cualquier worktree.

### 4. Cerrar diciendo qué no se pudo probar

"El trabajo se encoló y no salió" y "el papel salió" son afirmaciones distintas. Si
solo hay exit code, se dice: el log dice impreso, la cola no lo confirma.

## Pitfalls

- **`exit 0` de un `-print-to` (u otro spooler) es cola, no papel.** Con la
  impresora apagada, sin papel o en otra red, el trabajo queda retenido y el log
  escribe "Impreso … exit 0". El chequeo honesto es `Get-PrintJob` más la subred de la
  máquina contra la IP de la cola.
- **Un trabajo `Retained` tapa a los siguientes.** Hay que sacarlo antes de esperar
  papel; si no, aun volviendo a la red buena no sale nada.
- **El ping solo no prueba que no llega.** Windows filtra ICMP y devuelve "tiempo de
  espera agotado" con el equipo prendido. Lo que sí prueba que no llega es estar en
  otra subred que la IP de la cola.
- **La misma impresora suele estar instalada dos veces** (USB y por IP) con nombres
  casi iguales; la config nombra una sola. Se compara el nombre exacto de la cola.
- **La cola por IP es la que se muere en silencio** cuando la impresora cambia de
  dirección o la máquina cambia de red.
- **Dentro de `-Command` desde bash no van backticks**: son el escape de bash y el
  comando muere con `unexpected EOF while looking for matching`. Para filtrar o cortar
  se usa `Select-String -Pattern` o `-match`, y el texto se construye con `-f`.
- **El log de un trabajador vivo puede estar vacío aunque esté trabajando.** Si el lanzador
  captura la salida del hijo y la escribe recién cuando el proceso termina, el archivo sólo
  se llena al morir el proceso, y de golpe. La ausencia de renglones no prueba que no corrió;
  un log sin líneas nuevas con el proceso vivo es "no se sabe", y la respuesta sale del
  latido o de la fuente.
- **Contar procesos con el mismo renglón sobre-cuenta una cadena de lanzamiento.** Un `uv run`
  sobre `powershell` sobre `python` deja dos o tres procesos con la misma línea de comando;
  leídos como "varias instancias" hacen matar un escucha sano. La prueba de cuántos
  consumidores hay de verdad es el socket establecido contra el endpoint o el estado que
  declara la fuente, nunca la lista de procesos. Para dejar uno solo: matar la cadena
  entera —lanzador incluido—, arrancar **un** turno y verificar por la fuente que el pendiente
  baja a cero; un `schtasks /End` mata el `wscript` y deja el `python` huérfano.
- **Una corrida sin supervisión depende de servicios que no son la tarea**: la base
  productiva apagada fuera de horario, el servidor de archivos caído. Chequearlos es parte
  de la respuesta, no un extra.
- **El log de la corrida que hacés para verificar queda donde la corriste, no donde la corre el
  programador.** Repetir el comando desde un worktree de git escribe el log en ese árbol, que
  después se borra al cerrar la rama, así que el árbol de integración no ve nunca la corrida
  buena. Verificar desde el árbol que usa el programador, y si ya verificaste en otro lado,
  repetirlo ahí antes de declarar el arreglo.
- **Un envoltorio que traduce cualquier código distinto de 0 a "falló la tarea" convierte un
  archivo ilegible en un fallo nocturno falso.** La herramienta de respaldo/exportación sale
  distinto de 0 por un único origen que no puede abrir — el caso típico es el archivo de
  bloqueo que deja un Excel abierto (`~$*.xlsx`) — y el envoltorio informa la tarea entera en
  rojo mientras todos los demás archivos están bien. Se encuentra con un `--dry-run` más
  verboso; se arregla excluyendo el patrón de bloqueo, no borrando el archivo. **La lista de
  exclusión tiene que nombrar cada clase de candado**, no solo la que ya falló una vez. Y el
  arreglo no se da por probado leyendo la config: se prueba corriendo la operación real **con
  el proceso que toma el candado vivo**.
- **Un ítem de salud en verde puede estar midiendo otra pata de la tarea, no la que falló.**
  Un "respaldo: OK, hace 0 h" que lee el paquete local sigue en verde mientras la copia fuera
  de la máquina lleva días sin renovarse. Antes de tomarlo como cobertura, leé qué artefacto
  mide y con qué fecha. La forma del arreglo está en
  `designing-mechanical-guards/references/guards-over-machine-state.md`.

## Fuente canónica

Repo-tap `manusabbath-arch/hermes-skills` (`skills/unattended-run-verification`). Editar
acá, nunca la copia instalada.
