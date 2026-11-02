## Pedido 1

No puedo armar el bot ni dejarlo prendido: acá no tengo archivos ni puedo correr comandos. Te dejo el diseño y los pasos. Lo que sigue es seguir esos pasos en orden.

**Diseño**
- Es un canal nuevo que publica hacia afuera. Copiá la forma del sender de mail que ya tenga el repo, sin inventar otra.
- Se activa con un flag sobre el comando del informe, por ejemplo `--telegram`. No es un pipeline aparte.
- Usá `urllib` de la librería estándar. No hace falta una dependencia para un POST.
- El transporte se inyecta (`enviar(..., http=...)`) para que ningún test toque la red.
- Queda apagado por defecto: sin `config/telegram.txt` no se manda nada. Ese archivo vive fuera del repo y lleva solo el chat id, nunca el token. El lector tiene que rechazar cualquier línea `token:`.
- Un `--telegram` a mano se rechaza, con su propio exit code. Solo se envía si el scheduler exportó la variable marcadora o si pasás `--confirmar-envio`.
- El borrador (`--a-archivo`) sigue funcionando sin nada de eso.
- Telegram corta los mensajes en 4.096 caracteres, y un informe más largo falla sin avisar. Hay que recortar con margen, cortar en un salto de línea y avisar en el texto que se recortó.
- Cada cifra del mensaje cita su fuente y su fecha.
- El bot solo envía, y el scheduler sigue sin ningún agente adentro.

**Pasos para dejarlo andando (el orden importa)**
1. Creá el bot con BotFather y guardá el token en el almacén del sistema (Credential Manager), con el `@username` real del bot como etiqueta. Ese paso es tuyo, y el token no debería pasar por mí.
2. Escribí `config/telegram.txt` con un chat id provisorio.
3. Abrí el bot y apretá Start. Después corré el comando de descubrimiento (`getUpdates`) para obtener tu id real y ponelo en el config. Tiene que ser positivo, porque eso indica un chat privado. Un grupo tiene id negativo y no sirve para un informe con datos de clientes.
4. Verificá el token con `getMe`, que no tiene efectos secundarios.
5. Hacé un envío real de texto y otro de adjunto, y confirmame qué te llegó. Ahí se prueban dos llamadas distintas.
6. Recién después lo enchufás al scheduler.

Si querés que el bot también responda, eso es otro trabajo. Necesita un catálogo cerrado de comandos, una allowlist de ids y una tarea que lo arranque al iniciar sesión.

## Pedido 2

Ese envío ya salió, y si el archivo de enable estaba, fue real. Con el archivo presente, `--enviar` manda a destinatarios reales. Pasó antes: un envío "de prueba" llegó dos días antes del primer cron.

- Revisá a quién llegó y avisale si hace falta.
- Esa corrida quedó en el mismo log que lee el chequeo de frescura. La próxima corrida del gate va a reflejar el exit code de tu corrida a mano. No es una falsa alarma, así que investigá la entrada del log y no toques el chequeo ni el log.
- Para verificar sin enviar, usá el borrador (`--a-archivo`), que nunca manda.
- Conviene que `--enviar` a mano se rechace salvo que el scheduler exporte la variable marcadora o se pase `--confirmar-envio`.
- Lo que sigue sin probarse es el envío real desde el scheduler.

## Pedido 3

No lo sé. "Enviado" en el log y el PDF generado muestran que el informe se produjo y que el sender dio el envío por hecho. No muestran que el mail llegó, y la entrega es otro chequeo.

Para confirmarla:
- Pedile al destinatario que mire su bandeja, y revisá también spam.
- Si querés una señal más fuerte, mirá la carpeta de enviados de la cuenta remitente o si hubo rebotes.

La pantalla del destinatario es el único testigo real.

## Pedido 4

No puedo hacerlo, por dos motivos:
- No tengo archivos ni puedo ejecutar nada.
- El token no va en `config/telegram.txt`. Ese archivo solo lleva el chat id. Un token ahí es el error clásico, y el lector del config tiene que rechazarlo.

El token va en el almacén seguro del sistema (Credential Manager), etiquetado con el `@username` real del bot. Si lo tenés en un `.txt`, se mueve del archivo al almacén en un solo proceso. Ese proceso no imprime el valor: solo muestra el largo y si al releerlo coincide. Después borrá el `.txt`.

Para que arranque hoy:
1. Guardá el token en el almacén.
2. Escribí `config/telegram.txt` con tu chat id. Si todavía no lo tenés, poné uno provisorio, escribile Start al bot y descubrilo con `getUpdates`.
3. Verificá con `getMe`.
4. Hacé un envío de prueba y confirmá qué te llegó.

No me pegues el token en el chat.

## Pedido 5

Para el subject no hay un límite duro. El estándar (RFC 5322) recomienda líneas de hasta 78 caracteres y exige no pasar de 998. Para que se lea completo, apuntá a unos 50–60 caracteres. Los clientes de correo y los móviles suelen cortar alrededor de 40–70.

Poné lo importante al principio, por ejemplo el tipo de informe y la fecha.
