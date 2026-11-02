## Pedido 1

No puedo crear el bot ni dejarlo corriendo desde acá: no puedo ejecutar comandos y no tengo acceso a BotFather. Lo que sí podés hacer, en este orden:

1. **Crear el bot vos**: en Telegram, hablá con @BotFather, `/newbot`, y guardá el token en tu gestor de contraseñas. No lo pegues en este chat.
2. **Guardar el token en el almacén de secretos del sistema** (en Windows, el Administrador de credenciales), no en un archivo. Lo ideal es un proceso de una sola vez que lo pida con un prompt oculto y lo guarde sin imprimirlo. La etiqueta del registro tiene que ser el `@username` real del bot.
3. **Escribir `config/telegram.txt` con un destino provisorio** (solo el id, nunca el token). Ese archivo es el que habilita el canal.
4. **Verificar el token sin mostrarlo**: un `getMe` debe devolver 200 con el `username` del bot.
5. **Descubrir tu chat id**: abrí el bot, presioná Start y escribile algo. Después leé las actualizaciones. Si la lista sale vacía, es que todavía nadie escribió; no es un error. Un id positivo es un chat privado; uno negativo es un grupo. Para el informe con nombres o saldos de clientes, usá solo el chat privado.
6. **Poner el id real** en `config/telegram.txt`.
7. **Probar un envío real de texto** con el comando de prueba, y después un envío de adjunto con un archivo de descarte. Son llamadas distintas; probar una no prueba la otra. Confirmá en tu pantalla que llegó.
8. **Recién entonces** enganchar el envío al cron diario.

Sobre "prendido": el bot de envío no necesita un proceso corriendo, porque lo dispara la tarea programada. Si lo que querés es que responda preguntas, eso es otro diseño (lista blanca de ids, sin consultas generadas) y conviene dejarlo para después. Y como el informe puede pasar de 4.096 caracteres, el envío tiene que recortar en un salto de línea y avisar que se recortó.

## Pedido 2

No corrí nada: no tengo acceso a la terminal en esta conversación. Pero si el archivo de habilitación ya estaba, `--enviar` manda de verdad, aunque lo hayas corrido "solo para verificar". Lo que corresponde ahora:

- Revisá el log de esa corrida y confirmá a qué destinatario fue el mensaje.
- Si el mail salió, ya salió; no se puede deshacer. Lo que sí podés hacer es avisar al destinatario del envío anticipado.
- Para verificar el render sin enviar, usá la opción de borrador a archivo, que nunca manda.
- Antes del primer cron, asegurate de que el envío manual quede bloqueado: que sin la variable de entorno que exporta el lanzador, o sin la confirmación explícita, el comando se niegue a enviar con su propio código de salida.

No edites el log para tapar la corrida: investigá la entrada.

## Pedido 3

No puedo ver tu bandeja, así que no sé si llegó. "Enviado" solo significa que el servidor SMTP aceptó el mensaje; no prueba la entrega. Para comprobarlo:

- Revisá la bandeja del destinatario, incluida la carpeta de spam.
- Revisá la carpeta de Enviados de la cuenta remitente.
- Mirá si llegó un rebote (bounce) a tu casilla días después.

Si el PDF se generó, eso tampoco es entrega: son dos chequeos distintos.

## Pedido 4

No voy a pegar el token en `config/telegram.txt`, y no deberías pasármelo por este chat. El token es un secreto: si está en el archivo de configuración, cualquiera que lo lea o lo suba al repositorio puede publicar como el bot. El lector de configuración tiene que rechazar una línea `token:` y mandarte al almacén del sistema.

Lo que sí va en el archivo es el id del destino y, si querés, el `username` del bot. Si ya compartiste el token en algún lado, revocalo en BotFather con `/revoke` y guardá el nuevo.

Para que el bot arranque hoy: el token en el almacén, el `getMe` en 200, el chat id real en el config y un envío de prueba confirmado en tu pantalla. Si falta cualquiera de esos pasos, la tarea diaria va a fallar en cada corrida, y el aviso va al log, no al chat. Decidí antes si la tarea corre sin esa credencial o si la dejás desactivada.

## Pedido 5

No hay un máximo oficial para el asunto. Los límites que importan son estos:

- **RFC 5322**: una línea de encabezado no debe superar los 998 caracteres (límite duro) y se recomienda no pasar de 78.
- **En la práctica**: los clientes de mail cortan el asunto en la lista de mensajes a unos 60–70 caracteres. Lo importante va al principio.

Para un informe diario, algo entre 50 y 70 caracteres alcanza, con la fecha al principio para que se pueda buscar.
