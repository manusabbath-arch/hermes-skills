## Pedido 1

Probablemente sí, pero no puedo verificarlo desde acá: no tengo acceso a la configuración del job ni a sus logs. Si la PC queda encendida y no entra en suspensión, el job debería correr a las 07:10. Conviene revisar tres cosas en el programador de tareas:

- Que la PC no esté configurada para suspenderse a esa hora, o que la tarea tenga activada la opción de despertar el equipo.
- Si la tarea está configurada para "ejecutar solo cuando el usuario haya iniciado sesión", que la sesión siga abierta (con la pantalla bloqueada también funciona, pero cerrar sesión no).
- Que la carpeta de salida sea escribible con esa cuenta.

Después de la corrida, el archivo y el registro de ejecución te dirán si se generó.

## Pedido 2

No necesariamente. Exit 0 y "Impreso" significan que el proceso terminó sin error y que el comando de impresión se entregó a la cola de Windows. No confirman que el papel haya salido. La cola puede estar detenida, la impresora sin papel o sin tinta, o el trabajo puede quedar esperando en la cola.

Para confirmar, mirá la cola de la impresora en Windows (Configuración → Impresoras → Abrir cola) y después revisá la hoja física.

## Pedido 3

Que el proceso esté vivo no quiere decir que el worker esté funcionando. El chequeo de proceso solo confirma que existe, no que esté procesando mensajes. Algunas causas posibles:

- Está atascado en un bucle o esperando algo que nunca llega.
- El token del bot es inválido o expiró, y el worker sigue corriendo sin recibir actualizaciones.
- Recibe mensajes pero no los responde por un error silencioso.
- Está apuntando a un chat ID o un webhook equivocado.

Lo más útil es mirar la fecha y hora del último log de actividad real (no de arranque) y probar la API de Telegram directamente con el token para ver si responde. Si la API responde y el worker no, el problema está en el worker. Si la API no responde, el problema está en el token o en la configuración.

## Pedido 4

Eso indica que el timeout detuvo la espera, pero no la operación. La corrida se declaró fallida, pero el proceso de generación siguió y terminó tres minutos después.

Consecuencias:

- No trates el fallo por timeout como "no se generó nada". El archivo sí existe.
- Si hay reintentos automáticos, podrían generar un segundo PDF o pisar el primero.
- Revisá si la limpieza posterior al fallo se ejecutó antes o después de que apareciera el archivo, porque podría haber dejado residuos.

Lo recomendable es que el timeout cancele el proceso hijo de verdad (no solo deje de esperarlo), o que la corrida verifique la existencia del archivo antes de declarar el fallo.

## Pedido 5

`-l`. Se usa `crontab -l`, que lista las tareas del usuario actual.

Ojo: `crontab` es de sistemas tipo Unix. Como estás en Windows, ese comando no existe. Acá la equivalente es `schtasks /query`, o `Get-ScheduledTask` en PowerShell.
