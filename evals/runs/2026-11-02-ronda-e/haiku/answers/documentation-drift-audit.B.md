## Pedido 1

No puedo leer ni editar archivos en esta conversación, así que no puedo revisar la wiki ni actualizar los números viejos. Si me pegás el contenido de las páginas, marco los números que no coinciden con los datos actuales y te devuelvo el texto corregido.

## Pedido 2

No lo sé con certeza. No corrí el check, así que no puedo confirmar el resultado. Un 0 y 0 es plausible, pero conviene verificar que el check cubra estos casos:

- Links con alias (`[[nota|texto]]`) y con anclas (`[[nota#sección]]`).
- Links dentro de bloques de código, que a veces se cuentan y a veces no.
- Diferencias de mayúsculas o acentos en el nombre del archivo, que pueden fallar en Windows pero no detectarse.
- Cómo se define "huérfano": una nota sin links entrantes, o sin links entrantes ni salientes.

Si me pegás la salida completa del check o su código, reviso esos puntos.

## Pedido 3

No puedo borrar archivos ni verificar el registry desde acá. Mi recomendación es la que pedís: dejar 16 como cifra correcta y eliminar el documento viejo. Pero antes de borrarlo, conviene revisar que no tenga información que no esté en el otro lado, y que no haya links que apunten a él. Si me pegás el texto del documento viejo y la lista del registry, te digo qué falta y te preparo el texto actualizado.

## Pedido 4

Lo dejo como está. Es trabajo pendiente, así que no hay nada que cambiar.

## Pedido 5

En Obsidian se escribe con la ruta desde la raíz de la bóveda (vault):

- `[[carpeta/nota]]` apunta a una nota dentro de una carpeta.
- `[[carpeta/nota|texto a mostrar]]` usa un alias.
- `[[carpeta/nota#Encabezado]]` apunta a una sección.

Si el nombre de la nota es único en toda la bóveda, `[[nota]]` alcanza y Obsidian lo resuelve solo. Si hay dos notas con el mismo nombre en carpetas distintas, la ruta completa evita ambigüedad.
