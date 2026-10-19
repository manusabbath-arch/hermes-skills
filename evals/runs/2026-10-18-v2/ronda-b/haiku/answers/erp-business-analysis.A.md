## Pedido 1

No llegó ningún archivo, así que describo el método y los supuestos.

**Supuestos:** rotación anual = costo de ventas del período / stock promedio (promedio del stock inicial y final por producto). Uso costo y no venta para que sea comparable con el stock valuado al costo.

**Pasos:**
1. Tomo el período del preámbulo del export, no del nombre del archivo. Si dice 1 de enero al 18 de octubre, son 291 días; 2025 completo son 365.
2. Leo las columnas por nombre en cada export, no por posición.
3. Cruzo por código de producto. Sumo antes de dividir: rotación total = suma de costo / suma de stock promedio. Nunca promedio ratios.
4. Normalizo por días antes de comparar: muestro la rotación anualizada del YTD 2026 contra la de 2025, y también la bruta con su período declarado.
5. Excluyo ítems de gasto (fletes) antes de rankear.
6. Canario: el costo de ventas 2026 contra el informe del ERP con el mismo período y hora de corte (tolerancia 0,15%).

**Para correrlo necesito:** export de ventas 2025 completo, stock valuado al 31/12/2024, al 31/12/2025 y a la fecha de corte 2026. Si el stock inicial no viene, no lo infiero.

## Pedido 2

No concluiría que el ERP está desactualizado. Es la atribución más cómoda y la más costosa de retractar después.

Antes de culpar a la fuente:
1. Comparo el export contra sí mismo: detalle contra total del mismo archivo. Si no cierra, el error está en nuestro cálculo o en el parseo.
2. Reviso nuestro total: filas de subtotal o "TOTAL GENERAL", duplicados, filtro por razón social, moneda (pesos y dólares sumados como si fueran lo mismo) y separadores decimales.
3. Declaro entidad, período y hora de cada export. Si el ERP se consultó en otro momento, un comprobante cargado en el medio explica la diferencia.
4. Repito la consulta del ERP a la misma hora y con los mismos filtros, y lo contrasto con una fuente independiente (cuentas a cobrar por cliente, extracto bancario).

Solo si la diferencia persiste con filtros iguales y el archivo cierra consigo mismo, la reporto como hipótesis de desactualización, no como hecho. Hasta entonces no publico ninguna cifra que lo afirme.

## Pedido 3

Pedido de export para el cliente:

- **Informe:** "Margen por producto". Si no existe en el menú, "Ventas por producto" con columnas de costo. Confirmar el nombre exacto.
- **Período:** 01/01/2025 al 31/12/2025.
- **Entidad:** una por razón social, por separado. No pedir "todas".
- **Columnas:** código de producto, descripción, cantidad, venta neta, costo y moneda.
- **Formato:** .csv o .xlsx (no .xls).
- **Cifra de control:** el total de ventas 2025 del informe de Estadística del ERP, mismo período y entidad.

Al recibirlo verifico: que el archivo cierre consigo mismo; que el costo no sea cero donde hay ventas (cero guardado contra campo vacío); que el ranking no tenga ítems de gasto como flete; y que el total cruce con la cifra de control dentro de 0,15%. Si el costo no viene en el export, no lo calculo: lo pido por separado.

## Pedido 4

Un resultado exactamente al doble casi siempre es una fila de total sumada junto con el detalle, o un duplicado. Lo reviso en este orden:

1. Fila "TOTAL GENERAL" o subtotales dentro del archivo. Si un reexport cambió la cantidad de columnas, la fila sobrevive al filtro y todo da el doble.
2. Cruzo por nombre de columna, no por posición, e imprimo los encabezados de ambos lados.
3. Filas duplicadas: el mismo comprobante dos veces. Cuento filas contra comprobantes únicos.
4. Universo: confirmo que el informe de Estadística sea de la misma entidad y período. Si uno consolida y el otro no, la diferencia sale de ahí.
5. El archivo contra sí mismo: detalle contra total del mismo export.

Si la diferencia es exactamente el total o un duplicado, el informe de Estadística no está mal: corrijo el lado que sumé. No publico ninguna cifra hasta alinear ambos lados.

## Pedido 5

Es la explicación más probable y es verificable. Supongo que la deuda del cliente aparece en ambas razones sociales.

1. Corto ambos exports a la hora de cada uno, usando la fecha de modificación de la fila y no la del documento. Un recibo cargado entre la mañana y la tarde cambia el saldo sin cambiar su fecha.
2. Separo por razón social en los dos exports. Si el cliente tiene filas en una entidad en la mañana y en las dos en la tarde, hay partición.
3. Comparo fila por fila qué comprobantes aparecen o desaparecen. Si los $290.000 son un único comprobante o pago, eso lo confirma.
4. Reviso el filtro por nombre: una variante con tilde no matchea, sus filas caen en "otros" y el total general cierra igual, pero el cliente queda partido.
5. Agrupo por código de cliente, no por nombre.

Si la diferencia es un comprobante de $290.000 cargado entre las dos horas, es el corte de hora. Si aparece en una razón social y no en la otra, es partición. Para distinguirlas pido los dos exports con código de cliente y fecha de modificación.

## Pedido 6

En la celda debajo de la columna:

=SUMA(A2:A100)

Para toda la columna: =SUMA(A:A). Si querés sumar solo las filas visibles con filtro: =SUBTOTALES(9;A2:A100).
