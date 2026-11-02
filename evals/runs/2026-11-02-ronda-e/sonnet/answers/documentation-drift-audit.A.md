## Pedido 1

No puedo actualizar la wiki desde acá. No tengo acceso a los archivos en esta conversación, así que no sé cuáles son los números viejos ni cuáles son los vigentes. Para hacerlo bien necesito dos cosas:

- **El texto de la wiki**, o al menos las frases con cifras (cantidades, versiones, fechas, conteos).
- **La fuente de verdad de cada cifra**: el registry, la config, la salida de un comando, etc.

Con eso te armo una tabla de "dice X, debería decir Y". No conviene "refrescar" números a ojo, porque se corre el riesgo de reemplazar uno viejo por otro también desactualizado.

## Pedido 2

No necesariamente. 0 rotos y 0 huérfanos solo te dice que la estructura de enlaces es consistente: todo lo que se enlaza existe y todo está enlazado desde algún lado. Eso no cubre:

- **Contenido desactualizado**: números, nombres o pasos que ya no son ciertos, justo lo del pedido 1.
- **Anchors o encabezados**: según la herramienta, un `#sección` renombrado puede no detectarse.
- **Enlaces externos**: muchos checks solo miran los internos.
- **Enlaces que apuntan a la nota equivocada**: existen, pero no son lo que el texto promete.

Es una buena señal, pero no prueba que la documentación esté al día.

## Pedido 3

Entiendo que dejamos 16, como dice el registry, y borramos el README viejo. Tengo dos reparos antes de borrar:

1. **Verificar el 16**: confirmá que el registry sea la fuente de verdad y que ese conteo sea el actual. Que el README diga 8 solo prueba que está viejo, no que el 16 sea correcto.
2. **Revisar el README antes de borrarlo**: la carpeta no es un repo git, así que no hay forma de recuperarlo. Si tiene algo útil que no esté en otro lado (instrucciones de uso, contexto), movelo antes. Y buscá si otras notas lo enlazan, porque borrarlo dejaría enlaces rotos.

Si ya revisaste ambas cosas, borralo sin problema.

## Pedido 4

Perfecto, el TODO de «correr OCR sobre los PDFs escaneados» queda como está. Si querés que no se pierda, podés sumarle una fecha o un responsable. No hace falta tocar nada más.

## Pedido 5

Se escribe con el nombre de la nota entre dobles corchetes. Si hay que indicar la carpeta, se agrega la ruta:

- `[[Nota]]`: funciona si el nombre es único en toda la bóveda.
- `[[Carpeta/Nota]]`: con ruta, desde la raíz de la bóveda. Es lo que necesitás si hay dos notas con el mismo nombre.
- `[[Carpeta/Subcarpeta/Nota]]`: para más niveles.
- `[[Carpeta/Nota|texto a mostrar]]`: con alias.
- `[[Carpeta/Nota#Encabezado]]`: apunta a una sección.

Sin extensión `.md`. Por defecto Obsidian inserta la ruta más corta que no sea ambigua. Si escribís `[[` y empezás a tipear, el autocompletado te la sugiere.
