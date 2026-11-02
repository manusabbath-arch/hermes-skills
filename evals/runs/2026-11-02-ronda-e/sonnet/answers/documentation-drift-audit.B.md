## Pedido 1

No puedo actualizar la wiki desde acá: no tengo su contenido ni puedo medir nada. Si te la inventara, pondría números nuevos igual de sin verificar que los viejos. Este es el plan para hacerlo bien:

1. Listá todos los `.md`, sin `.obsidian/` ni cachés de herramientas.
2. Corré el chequeo de links y huérfanos.
3. Por cada cifra (cantidad de checks, archivos, fuentes), buscá el comando o registro que la produce y medila. No la deduzcas leyendo la wiki.
4. Revisá las frases con dos o más cifras. Si no cierran entre sí, por ejemplo "6 de 41" y después "esos 22", las dos están viejas.
5. Corregí en la misma línea, tachando el número viejo y poniendo el nuevo con fecha y motivo. Donde se pueda, escribí el comando que da la cifra en lugar del número.
6. Los documentos que son foto de una fecha llevan un bloque fechado arriba. No reescribas su historia.
7. Volvé a correr el chequeo al final.

Pasame los archivos o los resultados de los comandos y lo hago. Si alguna cifra resulta estar bien, lo voy a informar así y no voy a inventar correcciones.

## Pedido 2

No, todavía no se puede decir que está todo bien. "0 rotos y 0 huérfanos" también es lo que imprime un validador que no escaneó nada, por ejemplo con una ruta equivocada, un árbol vacío o una exclusión demasiado amplia. Antes de aceptar el cero necesito ver el denominador: cuántas notas escaneó y cuántos links resolvió. Si dice algo como "212 notas, 480 links resueltos", el cero vale. Si el chequeo no imprime esos totales, o imprime 0 de 0, el cero no prueba nada.

Además, ese chequeo no cubre las cifras viejas ni los TODO desactualizados, y tampoco los archivos de instrucciones que se cargan antes del árbol. Un resultado limpio en links no dice nada sobre eso.

## Pedido 3

Con el 16 estoy de acuerdo, pero con una condición: antes de escribirlo hay que volver a medirlo en el registry. Mejor todavía es que el documento diga qué comando lista los checks y no repita el número, así no vuelve a quedar viejo.

Lo que no haría es borrar el README. Si es el punto de entrada, borrarlo deja huérfanas todas las notas que enlazaba. Primero hay que ver si alguna otra nota apunta a él o si es la entrada de la wiki. Si el README es solo un duplicado, se corrige la línea en el lugar. Si está superado, se le pone arriba un bloque fechado que apunte al índice vigente. El "8" viejo queda como evidencia de lo que se decía antes.

## Pedido 4

No puedo confirmarlo sin ver el repo, pero lo dejaría solo si se cumplen estas tres cosas:

- El OCR no se hizo ya. Buscá en el repo si hay salidas de OCR o notas que lo mencionen como hecho.
- Los PDFs escaneados siguen existiendo y alguien o algo los consume. Si nada los lee, el ítem no es trabajo pendiente: es latente y conviene sacarlo de la lista, aclarando qué lo volvería activo.
- Correr OCR no pisa ni deshace algo ya arreglado, como texto corregido a mano.

Si las tres se cumplen, queda como está. Si falla alguna, te muestro qué falló y lo ajustamos.

## Pedido 5

Para enlazar una nota de otra carpeta con un wikilink de Obsidian:

- `[[Nota]]` funciona sin importar la carpeta, mientras el nombre sea único en la bóveda.
- `[[carpeta/subcarpeta/Nota]]` lleva la ruta desde la raíz de la bóveda. Hace falta cuando hay dos notas con el mismo nombre.
- `[[carpeta/Nota|texto a mostrar]]` agrega un alias.
- `[[carpeta/Nota#Sección]]` apunta a un encabezado.
- `[[carpeta/Nota#^id]]` apunta a un bloque.

La ruta no lleva la extensión `.md`.
