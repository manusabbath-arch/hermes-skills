## Pedido 1

No tengo la wiki a la vista, así que no puedo decirte qué números cambiaron. Para actualizarla sin que los números vuelvan a quedar viejos, haría esto:

1. Listaría todas las notas, sin contar carpetas de herramientas como `.obsidian/`.
2. Correría el chequeo de links y huérfanos, y miraría cuántos documentos y links revisó.
3. Buscaría cada cifra que la wiki cita (cantidad de checks, fuentes, scripts, tests) y la mediría con el comando que la produce, sin recalcularla a mano.
4. Donde se pueda, escribiría el comando en vez del número, por ejemplo «corré X para listar los checks».
5. Corregiría en el lugar y dejaría registro: el texto viejo tachado con fecha y motivo. Los documentos superados llevarían un bloque fechado arriba y el cuerpo quedaría intacto.
6. Volvería a correr el chequeo al final y te daría la lista de correcciones.

Si me pasás el contenido de las notas y la salida de los comandos que producen las cifras, te devuelvo las correcciones concretas.

## Pedido 2

Todavía no te lo puedo confirmar. Un «0 rotos, 0 huérfanos» es la misma salida que da un chequeo que no revisó nada, por ejemplo con la ruta mal o el árbol vacío.

Para que cuente como limpio, la salida tiene que mostrar cuántos documentos escaneó y cuántos links resolvió. Si dice 0 documentos, el chequeo está roto.

Pasame esos dos números. Si el chequeo no los imprime, conviene agregarlos.

Aun con denominador razonable, el chequeo solo cubre links y huérfanos. No dice nada sobre cifras viejas ni sobre consejos desactualizados.

## Pedido 3

Dejaría 16, pero no borraría el README.

- **Número:** antes de escribirlo, volvé a medir el registry, porque el valor puede cambiar durante el trabajo. Mejor todavía es escribir en el README el comando que lista los checks. Así no vuelve a quedar viejo.
- **Borrado:** el README suele ser el punto de entrada. Si lo borrás, cualquier nota que solo se alcance desde ahí queda huérfana. Corregilo en el lugar y, si querés conservar el 8, tachalo con fecha y motivo.
- **Si hay otro README:** si ese README «viejo» es otro documento distinto del índice, avisame. Antes de borrarlo habría que comprobar que nada lo enlaza y que su contenido tiene otro lugar donde vivir.

## Pedido 4

Lo dejaría como está solo después de revisar tres cosas:

1. **Premisa:** ¿sigue siendo cierta? Un TODO es una instrucción y alguien la va a seguir. Si ya se corrió OCR, si se probó y no sirvió, o si pisaría algo que ya se arregló, hay que marcarlo como «no hacer esto» y explicar por qué.
2. **Alcance:** contá cuántos PDFs escaneados hay realmente y si algo los consume hoy. Si nada los lee, el ítem es verdadero pero latente. En ese caso lo movería a una sección de latentes y diría qué lo activaría.
3. **Cierre previo:** buscá si otra nota ya lo registra como hecho o descartado.

Si las tres revisiones dan que sigue vigente y alcanzable, queda en la lista.

## Pedido 5

Con la ruta desde la raíz del vault:

```
[[Carpeta/Subcarpeta/Nota]]
```

- Si el nombre de la nota es único en todo el vault, alcanza con `[[Nota]]`.
- Con texto alternativo: `[[Carpeta/Nota|texto a mostrar]]`.
- A una sección: `[[Carpeta/Nota#Encabezado]]`.
- A un bloque: `[[Carpeta/Nota#^id-del-bloque]]`.

No lleva la extensión `.md`. Si dos notas tienen el mismo nombre en carpetas distintas, usá la ruta para evitar ambigüedad.
