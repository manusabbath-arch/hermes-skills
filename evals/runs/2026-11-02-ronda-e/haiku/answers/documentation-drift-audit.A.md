## Pedido 1

No pude actualizar la wiki. En la carpeta de trabajo solo encontré la skill y sus referencias, no hay ningún archivo de la wiki. Para hacerlo necesito la ruta de la wiki o que la copies en esta carpeta. Con eso, el procedimiento es: inventariar todas las notas, correr el chequeo de integridad, verificar cada número contra el sistema que describe y corregir dejando constancia de qué cambió y cuándo.

## Pedido 2

No puedo decir que esté todo bien. Un 0 rotos y 0 huérfanos solo vale si el chequeo recorrió notas de verdad. Un chequeo sobre un árbol vacío o ilegible también da 0 y 0. Antes de tomarlo como limpio, hay que confirmar que el resultado imprime cuántas notas revisó y cuántos links resolvió. Además, si una nota nueva no está en el control de versiones, el chequeo puede reportarla como link roto aunque el archivo exista. Y este chequeo solo cubre wikilinks y alcanzabilidad desde la nota de entrada. No verifica cifras ni consejos desactualizados.

## Pedido 3

No lo borraría todavía, y tampoco pondría 16 a mano. Primero:

- Medir el registry ahora, porque el número pudo cambiar. Lo que corresponde es escribir en el README el comando que lista los checks, no la cifra.
- Revisar si el README viejo tiene contenido que no esté en otro lado (reglas, lecciones, decisiones). Si lo tiene, hay que moverlo antes de borrarlo.

Si me confirmás que el registry es la fuente de verdad y que el README viejo no aporta nada único, puedo proponer el texto final. El borrado lo dejaría para cuando lo confirmes.

## Pedido 4

Lo dejo como trabajo pendiente, como pediste, pero antes conviene comprobar que el pendiente sea alcanzable. Hay que verificar:

- que existan PDFs escaneados en el árbol,
- que algún proceso o persona consuma la salida del OCR.

Si no hay PDFs escaneados, o nada lee el resultado, el TODO es latente: no está muerto, pero hoy no lleva a ninguna parte. En ese caso lo movería fuera de la lista de pendientes y anotaría qué lo activaría. Sin acceso a los archivos no puedo confirmar ninguna de las dos cosas.

## Pedido 5

En Obsidian, el wikilink usa la ruta desde la raíz del vault, sin extensión `.md`:

- `[[carpeta/subcarpeta/nota]]` apunta a una nota en otra carpeta.
- `[[carpeta/nota|texto a mostrar]]` cambia el texto visible.
- `[[carpeta/nota#Encabezado]]` apunta a una sección.

Si el nombre de la nota es único en todo el vault, `[[nota]]` alcanza sin la carpeta. Si hay dos notas con el mismo nombre, conviene usar la ruta completa para evitar ambigüedad.
