## Pedido 1

No puedo actualizarla todavía. Acá no puedo abrir archivos ni correr comandos, así que no tengo el contenido de la wiki. Si me pegás el texto (o las páginas con números viejos), reviso cada cifra contra el origen que la produce y te devuelvo las correcciones.

Para cada número voy a hacer lo siguiente:
- Anotar la cifra tal como aparece y qué la produce (un comando, un registro, un conteo).
- Corregirla, o mejor, reemplazarla por el comando que la calcula, para que no vuelva a quedar vieja.
- Dejar constancia de lo que cambió y por qué, sin reescribir el historial de páginas fechadas.

## Pedido 2

No necesariamente. Un «0 rotos y 0 huérfanos» solo es confiable si el chequeo recorrió lo que tiene que recorrer. Antes de darlo por bueno, hay que confirmar:
- **Cuántos documentos y cuántos links revisó.** Si el número es 0 o muy bajo, el chequeo no miró nada y el 0 no significa nada.
- **Si la lista de archivos sale del disco o de Git.** Si sale de Git, una nota nueva que todavía no agregaste aparece como link roto aunque esté bien escrita. Esto puede dar falsos positivos, pero también puede ocultar cosas si el chequeo se hizo sobre un árbol vacío.
- **Si el punto de entrada (el índice) está bien leído.** Un huérfano es un documento que no es alcanzable desde el índice; si el índice no se leyó, todo parece alcanzable.

Pasame el resultado con esos números (documentos revisados, links resolvidos, y el origen de la lista) y te digo si el 0 es real.

## Pedido 3

Estoy de acuerdo en dejar 16, pero antes de borrar el documento viejo hay que cerrar dos cosas:

1. **Revisar si tiene contenido único.** Si el documento viejo tiene alguna lección o explicación que no está en otro lado, borrarlo la pierde. Hay que buscar sus frases clave en el resto de la documentación y en el registro; lo que no aparezca en ningún lado hay que rescatarlo antes.
2. **Revisar si alguien lo enlaza.** Si el índice o alguna nota lo referencia, al borrarlo quedan links rotos.

Y en vez de escribir «16» como número fijo en la documentación, conviene poner el comando que lista los checks. Así el número no vuelve a quedar viejo cuando alguien agregue otro check.

No lo borro hasta que me confirmes que revisaste lo anterior (o me pegues el contenido para que lo revise yo).

## Pedido 4

Lo dejo como pendiente, como pediste. Solo te pido que confirmes una cosa antes de contarlo como trabajo activo: que exista algún proceso o lector que consuma la salida del OCR. Si los PDFs escaneados no se leen en ningún lado, el trabajo es real pero latente: queda fuera del backlog activo y se anota qué lo volvería urgente. No cambia el TODO, solo cómo lo clasificamos.

## Pedido 5

Obsidian resuelve los links por nombre de archivo, así que hay tres formas:

- **Con la carpeta:** `[[carpeta/nota]]`. Es la más clara cuando hay notas con el mismo nombre en distintas carpetas.
- **Solo el nombre:** `[[nota]]`. Funciona si el nombre es único en la bóveda.
- **Con alias o sección:** `[[carpeta/nota|texto a mostrar]]` para cambiar el texto del link, y `[[carpeta/nota#Sección]]` para apuntar a un encabezado.

No hace falta poner la extensión `.md`. Si querés incrustar el contenido en vez de enlazarlo, usá `![[carpeta/nota]]`.
