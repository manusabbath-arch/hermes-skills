## Pedido 1

No puedo leer ni editar la wiki desde acá: no tengo archivos adjuntos ni puedo correr comandos. Si me pegás el contenido de las páginas (o las que tengan los números viejos), reviso cada número, te digo cuál está desactualizado y te devuelvo el texto corregido. Si me indicás qué fuente usar para cada cifra, la actualización va a ser más confiable.

## Pedido 2

No necesariamente. Un resultado de 0 rotos y 0 huérfanos solo vale para lo que el chequeo realmente recorrió. Antes de darlo por bueno, conviene confirmar:

- **Alcance:** que haya escaneado todas las carpetas de la wiki y no solo algunas.
- **Formatos de enlace:** que cuente wikilinks con alias (`[[nota|texto]]`), con sección (`[[nota#encabezado]]`) y embeds (`![[nota]]`). Si alguno de estos no se procesa, los enlaces rotos quedan ocultos.
- **Resolución de nombres:** que no dé por válido un enlace solo porque existe un archivo con ese nombre en otra carpeta, cuando Obsidian lo resolvería distinto.
- **Huérfanos:** que la definición sea "ninguna nota la enlaza" y no "ninguna nota la enlaza desde fuera de su propia carpeta", porque eso cambia el número.

Si me pegás la salida del chequeo o me decís qué script o herramienta lo hizo, te digo si esos puntos están cubiertos.

## Pedido 3

Mi recomendación es dejar 16 como cifra correcta, como indica el registry. Antes de borrar el README viejo, revisá si tiene contenido que no esté en otro lado (instrucciones de uso, decisiones, enlaces) y pasalo a la documentación vigente. No puedo borrar el archivo ni editar el README desde acá, así que la eliminación la tenés que hacer vos. Si me pegás el README, te digo qué contenido único tiene antes de que lo borres.

## Pedido 4

Listo, lo dejo como está: el TODO sobre correr OCR en los PDFs escaneados queda como trabajo pendiente y no lo toco.

## Pedido 5

En Obsidian se escribe con la ruta de carpetas separada por barras, sin el `.md`:

- **Enlace simple:** `[[nombre-de-la-nota]]`. Funciona si el nombre es único en el vault.
- **Con ruta (recomendado si hay nombres repetidos):** `[[Carpeta/Subcarpeta/nombre-de-la-nota]]`.
- **Con alias:** `[[Carpeta/nota|texto que se muestra]]`.
- **A un encabezado:** `[[Carpeta/nota#Encabezado]]`.
- **Embed (incrusta el contenido):** `![[Carpeta/nota]]`.

Usá siempre barras `/`, también en Windows.
