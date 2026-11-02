## Pedido 1

No tengo acceso a la wiki en esta conversación, así que no puedo leerla ni editarla. Para actualizarla bien necesito dos cosas:

- El texto de las páginas, o al menos los pasajes con números.
- La fuente de verdad de cada número, por ejemplo el registry, un conteo real o un dashboard.

Con eso te devuelvo cada cifra vieja, el valor nuevo y la página donde va. No conviene "actualizar a ojo". Cada número debería salir de la fuente y no de otra página de la wiki, porque así se propagan los errores.

## Pedido 2

No necesariamente. Ese check solo dice que los links resuelven y que ninguna página quedó sin enlazar. No dice nada sobre si el contenido es correcto. Una página puede estar bien enlazada y tener números viejos, descripciones de cosas que ya no existen o instrucciones desactualizadas.

Además, "0 huérfanos" puede ser engañoso si hay un índice que enlaza todo automáticamente. Y según cómo esté hecho, el check puede no mirar anclas a encabezados, links externos ni referencias en texto plano que no son links.

Tu pedido 1 ya muestra que hay drift de contenido. El check de links no lo detecta, así que no alcanza como señal de que todo está bien.

## Pedido 3

Quedarse con 16 es razonable si el registry es la fuente de verdad. Pero contalo en vez de confiar en el número: si el README dice 8, puede que el registry haya crecido o que el README describa otra cosa.

Antes de borrar el README, revisá que no tenga contenido que no esté en otro lado, como instrucciones de uso, contexto o convenciones. Si es solo un número viejo, corregilo y listo. Si es un documento entero desactualizado, borrarlo está bien, pero hacelo con un backup o con control de versiones. Esta carpeta no es un repo git, así que el borrado no se podría deshacer. Yo no puedo borrar nada desde acá. Si querés, decime qué contiene y te ayudo a decidir qué rescatar.

## Pedido 4

Dale, lo dejamos. Un TODO de trabajo pendiente real no se toca. Solo te sugiero agregarle fecha o responsable, para que en una próxima auditoría se pueda distinguir de un TODO olvidado. Y si el OCR ya se hizo en parte, conviene aclararlo ahí mismo.

## Pedido 5

Se escribe con la ruta desde la raíz del vault:

```
[[Carpeta/Subcarpeta/Nota]]
```

Variantes útiles:

- Con texto alternativo: `[[Carpeta/Nota|texto que se muestra]]`
- A un encabezado: `[[Carpeta/Nota#Encabezado]]`
- A un bloque: `[[Carpeta/Nota#^id-bloque]]`

Si el nombre de la nota es único en todo el vault, alcanza con `[[Nota]]`. La ruta completa solo hace falta para desambiguar cuando hay dos notas con el mismo nombre en carpetas distintas. No hace falta poner la extensión `.md`.
