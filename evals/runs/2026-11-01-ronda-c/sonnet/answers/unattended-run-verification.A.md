## Pedido 1

Todavía no puedo asegurarlo. Que la PC quede prendida es una sola de las condiciones, y yo no pude leer la máquina desde acá. Para el job de las 07:10 hay que revisar cuatro cosas:

- **Sesión.** Si la tarea corre como "solo con el usuario logueado" (`LogonType = Interactive`), una pantalla bloqueada alcanza. Un reinicio de madrugada, por ejemplo por Windows Update, deja la máquina sin sesión y la tarea no corre.
- **Turno perdido.** Mirá si `StartWhenAvailable` está en `False`. En ese caso, si la PC está dormida o apagada a las 07:10, el turno no se recupera.
- **Energía y tapa.** Revisá que la suspensión esté en "nunca" también con batería, no solo enchufada. Si es una notebook, la acción de la tapa puede suspender el equipo. Si `LIDACTION` no devuelve nada, no tengo ese dato: no cierres la tapa.
- **Próxima ejecución.** `NextRunTime` tiene que mostrar mañana a las 07:10. Un `LastTaskResult` de `267011` significa que nunca corrió.

Tampoco alcanza con que la tarea se ejecute. Mañana hay que comprobar que el archivo existe, con su fecha y tamaño mayor que cero, y que es de esa corrida y no el de ayer. El log o el estado de la tarea no prueban eso. Si el job depende de otros servicios, como una base de datos o un servidor de archivos, también tienen que estar disponibles a esa hora.

## Pedido 2

No lo sé todavía. El exit 0 y el "Impreso" del log solo indican que el spooler aceptó el trabajo. No prueban que haya salido papel. Con la impresora apagada, sin papel o en otra red, el trabajo queda retenido y el log dice lo mismo.

Para confirmarlo:

- Corré `Get-PrintJob -PrinterName '<cola exacta>'`. Fijate que no haya un trabajo `Retained`, porque ese bloquea a los siguientes.
- Revisá con `Get-Printer` el estado de la cola: `WorkOffline` y `DetectedErrorState`.
- Verificá que la subred de la PC (`Get-NetIPAddress`) sea la misma que la IP de la cola.
- Controlá que el nombre de la cola sea el que usa la configuración. Es común tener la misma impresora instalada dos veces, por USB y por IP.

Mientras no tenga eso, lo que puedo decir es que el trabajo se encoló. No puedo decir que el papel salió. Lo más rápido es mirar la bandeja de la impresora.

## Pedido 3

Que el proceso exista no prueba que el worker esté trabajando. Puede estar colgado antes del bucle de consulta, y por eso el chequeo sigue en verde mientras nadie contesta. Ese chequeo mide si hay un proceso, no si el worker atiende mensajes.

Para saber qué pasa, mirá la fuente:

- Consultá el `pending_update_count` del bot. Si hay proceso y ese número no baja en unos minutos, el worker no está consultando.
- Si el log está vacío, no concluyas nada. Algunos lanzadores escriben la salida del hijo recién cuando el proceso termina. Con el proceso vivo y sin líneas nuevas, lo correcto es "no se sabe".
- No mates procesos por contarlos. Una cadena como `uv run`, `powershell` y `python` deja varios procesos con la misma línea de comando, y no son instancias duplicadas. Para saber cuántos consumidores hay, mirá el socket establecido o lo que declara la fuente.
- Si hace falta reiniciar, matá la cadena entera, lanzador incluido. Arrancá un solo worker y verificá que el pendiente baje a cero.

Como arreglo permanente, conviene que el worker escriba un latido en cada vuelta, también cuando no trajo nada. Ese latido debería ir en una carpeta de datos compartida, fuera del repo. La guarda lo lee con un umbral mayor que el long poll, por ejemplo 10 minutos, y deja de medir solo la existencia del proceso.

## Pedido 4

Ese PDF no reivindica la corrida. Que haya aparecido después del fallo indica que un proceso hijo sobrevivió al timeout y lo escribió tarde, sin que nadie lo recogiera. La corrida falló, y el trabajo igual se hizo.

Lo más probable es que al vencer el tope se haya matado el lanzador (por ejemplo `chrome.exe`) y no el árbol de procesos. La instancia que hacía el trabajo siguió viva. Para verificarlo, compará la hora del archivo con la ventana de la corrida. Si es posterior al cierre, es un huérfano.

Lo que corresponde reportar es esto: el PDF se generó, nadie lo tomó, y la causa fue que el timeout no mató el árbol completo. Para arreglarlo:

- Matá el árbol entero al vencer el tope. En Windows es `taskkill /F /T /PID`. Desde git-bash, usá `powershell -NoProfile -Command "Stop-Process -Id <pid> -Force"`.
- Borrá el destino antes de producir, para que un PDF viejo no pase por nuevo. Dalo por bueno solo si pesa más de cero.
- Usá un directorio de bloqueo temporal por intento, como `--user-data-dir`, para que el reintento no espere el candado del anterior.
- Hacé que el código de salida coincida con el artefacto. Si no se escribió el archivo, es fallo.

## Pedido 5

`crontab -l` lista las tareas del usuario actual.
