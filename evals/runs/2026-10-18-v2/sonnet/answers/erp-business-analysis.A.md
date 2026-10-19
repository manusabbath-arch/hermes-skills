## Pedido 1

Como no tengo el archivo, te cuento cómo lo haría y qué supuestos tomo.

- **Período:** lo leo del preámbulo del export, no del nombre. "2026 YTD" puede ser mucho menos (o más) de lo que dice el título. Declaro período real, razón social y grano (producto) en cada cifra.
- **Comparación con 2025:** los períodos tienen distinto largo, así que normalizo por días (ventas por día) antes de comparar. Si no, la "caída" o el "crecimiento" es solo calendario. Para 2025 uso el mismo corte de fechas (1/1 hasta la misma fecha) o declaro el desfasaje.
- **Rotación:** costo vendido del período ÷ stock promedio, calculado agregando (suma de costo / suma de stock), no promediando ratios por producto. Verifico la identidad rotación × cobertura = días del período; si no cierra, hay un error.
- **Ojo con los datos:** cruzo por nombre de columna, no por posición; descarto la fila `TOTAL GENERAL`; reviso el top del ranking por si aparece un flete u otro gasto como "producto"; y verifico si el stock en cero es cero guardado o NULL.
- **Control:** el total de ventas del export tiene que cerrar contra el detalle del mismo archivo y contra otra fuente (informe de Estadística) dentro de ~0,15%.

Supuesto: el export de ventas no trae stock. Necesito además el stock valorizado a inicio y fin de cada período, y la entidad (razón social) filtrada. Al pie va un sello de procedencia (archivo, hora, sha256, filas leídas y descartadas).

## Pedido 2

No concluiría todavía que el ERP está desactualizado. Esa es la explicación cómoda y suele ser falsa: en el proyecto de referencia, un "ERP desactualizado 1,4%" era un `abs()` nuestro.

Pasos, en orden:

1. **Comparar el export contra sí mismo:** detalle vs. total del mismo archivo. Si no cierra, el problema es nuestro.
2. **Hora del export:** si el ERP muestra datos más nuevos, un recibo cargado después explica la diferencia. Corto a la hora del export.
3. **Universo:** misma razón social, mismo período declarado y mismo grano en ambos lados.
4. **Moneda:** si hay dólares y pesos, no se suman juntos. Si el cociente del desvío es un número redondo, busco qué unidad representa.
5. **Parseo:** si todos los montos salen enteros, hay un `replace` roto.

Supuesto: hasta no descartar 1 a 5, el desvío es nuestro. Si algo se publicó con "el ERP está mal", lo retracto y corrijo todo documento que lo cite.

## Pedido 3

Por ahora no puedo darte el margen: no hay datos de costo y ventas de 2025. Le pediría al cliente esto, con el filtro exacto:

- **Informe 1:** ventas por producto 2025 (nombre del informe tal como aparece en el menú del ERP), del 01/01/2025 al 31/12/2025, con **código de producto**, cantidad e importe neto, de una razón social por vez.
- **Informe 2:** costo por producto (costo de la mercadería vendida, o costo de reposición/promedio), mismo período y misma entidad, con código de producto.
- **Formato:** `.csv` o `.xlsx`, nunca `.xls` (se corta en 65.536 filas).
- **Cifra de control:** el total de ventas 2025 de la entidad según el informe de Estadística, para verificar que el archivo llegó completo.
- **Moneda:** indicar en qué moneda vienen los importes.

Supuesto: el margen se calcula por código, no por nombre. Controlo que ningún producto tenga margen del 100% o negativo sin explicación (un distribuidor no vende a costo ni gratis), y que el precio implícito (importe ÷ cantidad) coincida entre los dos informes. Si el ítem número uno es un flete, lo excluyo.

## Pedido 4

Que dé **exactamente el doble** es la firma típica de una fila de total que quedó dentro de la suma. Lo más probable es que el export traiga `TOTAL GENERAL` (y quizás subtotales por vendedor o marca) y vos sumaste detalle + total. Con un reexport que cambió de 9 a 7 columnas ya pasó: la fila de total quedó viva y todo dio 2×.

Qué haría:

1. Mirar las últimas filas del archivo y buscar `TOTAL`, `Subtotal` o filas con la clave vacía.
2. Descartarlas y volver a sumar. Si ahora cierra contra Estadística, listo.
3. Verificar que el período declarado en el preámbulo y la razón social sean los mismos que los de Estadística.
4. Cruzar por nombre de columna (no por posición) e imprimir los encabezados de cada lado.
5. Confirmar que el detalle suma lo mismo que el total del propio archivo.

Supuesto: el desvío es nuestro, no del ERP. Cuando cierre, anoto la causa en el libro de errores con fecha.

## Pedido 5

Puede ser una partición entre razones sociales, pero no lo daría por hecho. Hay otras explicaciones que descartaría primero, empezando por la más barata:

1. **La hora.** Dos exports del mismo día con distinta hora suelen diferir por un recibo o factura cargados entre la mañana y la tarde. Mirá si hay un movimiento por $290.000 (o varios que sumen eso) con fecha de modificación entre ambas horas. En el proyecto de referencia, una "brecha" de +4,2% se cerró a 0,15% cortando a la hora del export.
2. **Entidad.** La deuda está particionada por razón social, mientras que clientes y stock son compartidos. Verificá que ambos exports sean de la misma entidad. Si uno es de la SAS y el otro de la otra razón social, la diferencia sería esa parte. Cruzá por código de cliente, no por nombre (una tilde puede dejar todo en "otros" y el total igual cierra).
3. **Cada export contra sí mismo:** detalle vs. total.
4. **Moneda:** que no se hayan sumado dólares como pesos.

Supuesto: pruebo primero la hora y la entidad; solo si ninguna explica los $290.000 completos hablo de partición. Para eso necesito la hora de cada export y la razón social declarada en cada preámbulo.

## Pedido 6

Para sumar una columna: `=SUMA(B2:B100)` en Excel en español, o `=SUM(B2:B100)` en inglés. Cambiá `B2:B100` por el rango de tu columna. Para una columna entera, `=SUMA(B:B)`.

Si querés sumar solo las filas que cumplen una condición, usá `=SUMAR.SI(A:A;"criterio";B:B)`. Si los números están guardados como texto, la suma da 0: convertilos primero.
