## Pedido 1

No puedo asegurarlo, y no lo daría por hecho. Que la PC esté prendida es necesario, pero no alcanza. Esto puede hacer que no corra o que no deje el archivo:

- **Suspensión o hibernación:** si Windows entra en suspensión por inactividad, el job no se dispara, salvo que la tarea tenga activado "Reactivar el equipo para ejecutar esta tarea" y el equipo lo permita.
- **Sesión de usuario:** si la tarea está configurada como "Ejecutar solo cuando el usuario haya iniciado sesión" y la sesión se cerró o está bloqueada, puede no correr o no tener acceso a lo que necesita.
- **Actualizaciones:** Windows Update puede reiniciar la PC durante la noche.
- **Cuenta y permisos:** si cambió la contraseña de la cuenta, o si la ruta de destino es de red o está en una unidad que no está montada, puede fallar.
- **Que se ejecute no es que deje el archivo:** el código de salida y el archivo generado son cosas distintas.

Para quedarte tranquilo, antes de dormir:
1. Desactivá la suspensión (Configuración, Energía).
2. Revisá en el Programador de tareas que la próxima ejecución diga 07:10.
3. Probá la tarea manualmente con "Ejecutar".

Mañana confirmá con el archivo mismo: que exista, que tenga fecha y hora de hoy, y que su tamaño no sea cero. El historial de la tarea solo te dice si arrancó.

## Pedido 2

No necesariamente. El exit 0 y el log "Impreso" indican que SumatraPDF terminó sin error y que el trabajo se entregó a la cola de impresión. No confirman que salió papel. Que esté en el papel depende de lo que pase después, en el spooler y en la impresora.

Puede haber fallado así:
- La impresora está offline, sin papel, sin tóner o con el papel atascado.
- El trabajo quedó retenido o con error en la cola.
- La impresora predeterminada no era la que esperabas, o se imprimió en un PDF virtual.
- Los ajustes de impresión (por ejemplo, el rango de páginas) dejaron el trabajo vacío.

Fijate en la cola de impresión (Configuración, Impresoras, "Abrir cola") si hay trabajos pendientes o con error. Y mirá la bandeja de la impresora. Si querés automatizar la verificación, consultá la cola con `Get-PrintJob -PrinterName <nombre>`. Aun así, solo el papel en la bandeja lo confirma del todo.

## Pedido 3

Ese chequeo en verde solo dice que el proceso existe. No dice que el worker haga su trabajo. Un proceso puede estar vivo y no responder, por ejemplo:

- **Bloqueado o colgado:** está esperando algo (una llamada de red sin timeout, un lock) y no atiende mensajes.
- **Token inválido o revocado:** el proceso sigue, pero la API de Telegram rechaza sus llamadas.
- **Conflicto de polling:** hay otra instancia usando el mismo token. Telegram devuelve el error 409 y ninguna instancia recibe bien los mensajes.
- **Red, proxy o DNS caídos:** el worker no llega a `api.telegram.org`.
- **Webhook activo:** si hay un webhook configurado, `getUpdates` no entrega nada.
- **Error en el handler:** las excepciones se tragan en silencio y el loop sigue sin responder.

Qué hacer, en orden:
1. Mirá los logs del worker en busca de errores 401, 409 o timeouts, y fijate si el último log reciente es de hace mucho.
2. Llamá a `getMe` y a `getWebhookInfo` con el token. Así ves si el token sirve y si hay un webhook o errores pendientes.
3. Revisá que haya una sola instancia.
4. Mandá un mensaje de prueba y mirá si el worker lo recibe.

A largo plazo, cambiá el chequeo para que mida lo que importa: un heartbeat que el loop escriba al procesar, o un ping de punta a punta que espere una respuesta real. Así el verde significa que contesta, no solo que existe.

## Pedido 4

Entonces el fallo declarado era falso, o al menos prematuro. El trabajo no falló: tardó más que el timeout. Lo que tenés ahora es un resultado que existe pero que la corrida registró como fallido. Son dos cosas distintas que hay que reconciliar.

Primero verificá que el PDF sirva, antes de usarlo:
- Que esté completo (tamaño razonable, abre sin error, páginas esperadas).
- Que su fecha y hora correspondan a esa corrida y no a una anterior.
- Que el proceso que lo generó haya terminado. Si sigue escribiendo, el archivo puede estar incompleto.

Después revisá las consecuencias del fallo declarado. Puede haber disparado un reintento, una alerta, una limpieza o una segunda corrida que ahora compite o duplica el archivo. Si hay otra corrida en curso, podría pisarlo.

La causa de fondo es el timeout, que está mal calibrado o ignora que el proceso sigue vivo. Algunas opciones:
- Subir el timeout según la duración real observada.
- Al vencer, matar el proceso explícitamente, en vez de declarar fallo y dejarlo corriendo.
- Escribir el archivo con un nombre temporal y renombrarlo al terminar, para que su presencia indique que está completo.

Si el archivo es válido, podés usarlo. Dejá anotado en el registro que la corrida fue un falso fallo.

## Pedido 5

`crontab -l`

Lista las tareas del usuario actual. Con `-u <usuario>` (como root) ves las de otro usuario. Para editarlas es `crontab -e`.
