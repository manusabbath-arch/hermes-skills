## Pedido 1

No puedo confirmarlo esta noche: no tengo forma de mirar la máquina desde acá. Lo que sí sé es qué tiene que cumplirse para que el job de las 07:10 corra y deje el archivo:

- **Sesión abierta.** Si la tarea está configurada como "solo con el usuario logueado", no corre si la máquina se reinicia sola (por ejemplo, por una actualización de Windows) y nadie inicia sesión. Bloquear la pantalla no afecta.
- **Despertar y turno perdido.** Si la PC entra en suspensión, hace falta que "Despertar el equipo para ejecutar la tarea" esté activo. Si está apagada o dormida a la hora del turno, "Ejecutar la tarea lo antes posible si se perdió el inicio programado" tiene que estar activo para que se recupere.
- **Energía.** Revisá la suspensión con `powercfg /query SCHEME_CURRENT SUB_SLEEP`. Un valor de 0 significa que nunca suspende, pero solo en la fuente que estés usando (enchufada o con batería).
- **Tapa.** Si es notebook, cerrar la tapa puede suspender el equipo. Pedí que no la cierre.

La prueba real es mañana a la mañana: el archivo con fecha y hora posteriores a las 07:10 y un tamaño mayor que cero. Que la tarea figure como "próxima ejecución 07:10" no prueba nada por sí solo.

## Pedido 2

No está probado. "Exit 0" y "Impreso" solo dicen que SumatraPDF entregó el trabajo a la cola de impresión. Si la impresora está apagada, sin papel, o la cola apunta a una IP de otra red, el trabajo puede quedar retenido en la cola y el log igual dice "Impreso".

Para saber si salió papel hay que mirar la cola: el estado de la impresora, si está "sin conexión", si hay trabajos retenidos y si la subred de la PC coincide con la de la IP de la impresora. Hasta que eso esté verificado, lo que tenés es "entregado a la cola", no "impreso".

## Pedido 3

Que el proceso esté vivo no prueba que esté trabajando. Puede estar colgado antes de entrar al bucle de consulta, y mientras tanto los mensajes se acumulan sin respuesta.

La evidencia tiene que venir de la fuente:

- **Pendientes en Telegram.** Si el bot usa webhook, `getWebhookInfo` devuelve `pending_update_count`. Si ese número no baja, el worker no está consumiendo. Si usa `getUpdates`, no hay un contador directo, así que hay que apoyarse en el latido.
- **Latido del worker.** Si el worker no escribe cuándo fue su última consulta y cuántos mensajes trajo, no hay forma de distinguir "no hay mensajes" de "no pregunta". Con un umbral mayor que el tiempo de long poll, un latido viejo indica que está trabado.

Si el pendiente no baja, el arreglo es matar la cadena completa (lanzador incluido), no solo el proceso que aparece en la lista, y arrancar una sola instancia. Después, verificar que el pendiente baje a cero.

## Pedido 4

No lo tomaría como éxito. Si la corrida declaró fallo por timeout y el PDF apareció tres minutos después, lo más probable es que un proceso hijo sobreviviera al corte y terminó de escribir el archivo sin que nadie lo esperara. Es un entregable huérfano: la corrida dijo que falló, y el archivo llegó tarde por un proceso que se escapó.

Para confirmarlo:

- Compará la hora del archivo con la ventana de la corrida. Si es posterior al cierre, el archivo no reivindica la corrida.
- Revisá si quedan procesos del navegador o exportador vivos. Si siguen corriendo, están escribiendo algo que la corrida ya dio por perdido.

El problema de fondo es que al vencer el timeout se mató el lanzador y no el árbol de procesos. La corrección está en el productor: matar el árbol completo (`taskkill /F /T /PID` o `Stop-Process` sobre el árbol), borrar el destino antes de cada corrida y dar por bueno el archivo solo si tiene tamaño mayor que cero.

## Pedido 5

Con `crontab -l`. Lista las tareas del usuario que ejecuta el comando, sin necesidad de agregar otro parámetro.
