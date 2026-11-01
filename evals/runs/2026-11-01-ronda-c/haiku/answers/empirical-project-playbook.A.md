## Pedido 1

Sí se puede. Hay dos formas habituales:

- **Programador de tareas de Windows o cron:** una tarea nocturna ejecuta un script que llama a Claude Code en modo no interactivo (`claude -p "..."`) sobre tus evals, guarda la salida y después envía el resultado. Es lo más directo si las evals corren en esta máquina.
- **GitHub Actions con `schedule`:** un workflow con `cron` corre las evals en un runner y publica el resultado como comentario, issue o mensaje a Slack. Conviene si el repo está en GitHub y no querés depender de que la PC esté encendida.

En ambos casos hacen falta:

1. Una API key o credenciales guardadas como secreto (no en el script).
2. Un paso que compare el resultado con la corrida anterior, para avisar solo si algo empeoró.
3. Un canal de notificación: email, Slack o similar.

No puedo crear ni probar la tarea programada desde acá, así que tendrías que armarla y hacer una corrida manual antes de dejarla nocturna.

## Pedido 2

No, está mal. Un log de respaldo que no existe no es prueba de que no haya errores. Si falta el archivo de ayer, el tablero está ocultando justamente el problema que debería mostrar.

Lo que conviene hacer:

- Tratar la ausencia del log esperado como **fallo o alerta (rojo o amarillo)**, nunca como verde.
- Verificar que exista un respaldo con fecha de ayer y que tenga un tamaño mayor que cero.
- Mostrar "sin datos" como estado propio, distinto de "ok".
- Si el respaldo viene de un proceso programado, alertar también cuando ese proceso no dejó ninguna señal, no solo cuando reporta un error.

El verde debería significar "encontré el respaldo de ayer, está completo y no tiene errores", no "no encontré nada que marque error".

## Pedido 3

El 15% de 2.400 es **360**.
