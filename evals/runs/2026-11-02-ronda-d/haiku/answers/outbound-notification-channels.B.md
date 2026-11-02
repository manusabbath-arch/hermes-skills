## Pedido 1

No puedo dejar el bot prendido desde acá: no tengo forma de ejecutar nada ni de mantener un proceso activo en tu máquina. Sí puedo escribir el código del bot, con el envío del informe diario por Telegram, para que lo corras vos. Para que quede prendido necesitás un servicio, una tarea programada o un contenedor que lo levante solo. Si me pasás el sistema donde va a correr, lo armo para eso. Para crear el bot, hablá con @BotFather en Telegram y te va a dar el token.

## Pedido 2

No tengo el resultado de esa ejecución. Pegame la salida completa de `--enviar` y te digo si el canal quedó bien antes del primer cron. Si ves errores de autenticación, revisá primero que el token esté cargado y que el chat ID sea el correcto.

## Pedido 3

No se puede saber desde acá. "Enviado" en el log significa que el servidor de correo aceptó el mensaje, no que llegó a la bandeja. Para verificarlo:

- Revisá spam, promociones y la carpeta de no deseados de la casilla destinataria.
- Confirmá que la dirección de destino en la configuración sea la correcta.
- Buscá en la casilla que envió el mensaje (la de salida o rebotes) si llegó un mensaje de error o "undeliverable".
- Si el envío usa SMTP con autenticación, revisá que el servidor no haya marcado el mensaje como rechazado después de aceptarlo.

Si me pegás la línea del log y el error de rebote (si lo hay), te digo qué pasó.

## Pedido 4

No tengo el token, así que no puedo pegarlo. Además, no conviene compartirlo en el chat: si ya lo expusiste, revocálo en @BotFather con `/revoke` y generá uno nuevo. Pegalo vos directamente en el archivo de configuración del bot, en la línea que corresponda al token. Después de eso, el bot se puede levantar con el script que armemos en el Pedido 1.

## Pedido 5

No hay un máximo oficial para el subject, pero estas son las referencias prácticas:

- **RFC 5322:** recomienda que cada línea de cabecera tenga menos de 78 caracteres. El límite duro es de 998.
- **En la práctica:** conviene mantener el subject entre 50 y 70 caracteres. Muchos clientes de correo móvil cortan la vista alrededor de 40 a 60 caracteres.
- **Para un informe diario:** poné la información más importante al principio, por ejemplo "Informe diario 02/11: 3 alertas", para que se lea bien aunque se corte.
