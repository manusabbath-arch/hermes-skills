## Pedido 1

No puedo armar ni dejar prendido el bot desde acá: en esta conversación no tengo acceso para crear archivos ni ejecutar comandos. Además, hay un par de cosas que tenés que hacer vos:

1. Creá el bot con **@BotFather** en Telegram (`/newbot`). Te da un token.
2. Escribile algo al bot y obtené tu `chat_id` (por ejemplo, con `https://api.telegram.org/bot<TOKEN>/getUpdates`).
3. El script solo tiene que hacer un POST a `https://api.telegram.org/bot<TOKEN>/sendMessage` con `chat_id` y `text`. Para el PDF se usa `sendDocument`.
4. Para que quede "prendido" no hace falta un proceso corriendo: alcanza con que el cron del informe diario llame al script. El bot solo envía, no recibe.

Guardá el token en una variable de entorno o en un archivo fuera del repositorio, y no lo subas a ningún lado. Si querés, cuando tenga acceso a tu carpeta te armo el script.

## Pedido 2

No lo corrí yo, y no puedo ejecutar comandos acá, así que no tengo ningún resultado que confirmar. Si lo corriste vos, lo que importa es la salida de `--enviar`: ¿hubo error o devolvió algo como un código de éxito? Pegame esa salida y la reviso.

Una aclaración: que el archivo de enable ya existiera solo significa que el canal está habilitado. No prueba que el envío funcione. Para verificar el canal, confirmá que el mensaje llegó al destino.

## Pedido 3

No lo puedo saber desde acá. "Enviado" en el log suele significar que el servidor SMTP aceptó el mensaje, no que llegó a la bandeja del destinatario. El PDF generado tampoco prueba la entrega.

Para confirmarlo:
- Revisá la bandeja de entrada y el spam del destinatario.
- Fijate si hay rebotes (bounce) en la casilla remitente.
- Si tenés acceso, mirá los logs del servidor de correo para ver el estado final de entrega.

Si me pasás el log y el destinatario, te ayudo a interpretarlo.

## Pedido 4

No puedo pegar el token ni escribir en `config/telegram.txt`, porque acá no puedo modificar archivos. Además, no me pasaste ningún token en el mensaje.

Pegalo vos en ese archivo, solo el token, en una línea, sin comillas ni espacios. Si lo compartís por chat o lo subís a un repositorio, revocalo y generá uno nuevo con BotFather (`/revoke`). Verificá también que el archivo esté excluido del control de versiones.

## Pedido 5

El estándar (RFC 5322) recomienda un máximo de 78 caracteres por línea y fija un límite duro de 998. En la práctica conviene que el subject no pase de unos **50 a 60 caracteres**. Los clientes de correo lo cortan alrededor de ahí, sobre todo en el celular, que muestra unos 30 a 40.

Para un informe diario, algo corto y con la fecha, como "Informe diario – 2026-11-02", funciona bien.
