## Pedido 1

No tengo el archivo adjunto, así que describo lo que haría. Supuesto: el export 2026 trae por producto las unidades vendidas, el costo de venta y el stock.

- Rotación por producto = costo de ventas del período / inventario promedio, con inventario promedio = (stock inicial + stock final) / 2.
- Días de inventario = días del período / rotación.
- Como 2026 es YTD (parcial), comparo contra 2025 con el mismo corte de meses (enero a la fecha de corte), no contra el año completo. Si no, la rotación 2026 aparecería artificialmente baja.
- Si el export solo trae el stock actual, uso el promedio de los cierres mensuales como inventario promedio.
- Presento la variación contra 2025 en veces y en días, y marco los productos con stock pero sin ventas en el período.

Para la comparación necesito el mismo tipo de export de 2025 con el mismo corte.

## Pedido 2

No puedo confirmar que el ERP esté desactualizado con la información disponible. Es una hipótesis que tengo que verificar antes de aceptarla. Lo que haría:

- Comparar la fecha y hora de corte de ambos: el export y la consulta del ERP. Si son distintas, la diferencia puede ser de tiempo.
- Revisar qué incluye cada uno: notas de crédito, pagos parciales, anticipos, documentos anulados, moneda y filtros por estado.
- Conciliar cliente por cliente y ordenar las diferencias de mayor a menor. Si la diferencia se concentra en pocos clientes, es un tema de imputación o de cortes; si está repartida, es más probable un problema de cálculo en el export.
- Verificar que el export no tenga filas duplicadas ni un total incluido en el detalle.

Si después de eso las diferencias son documentos que el ERP no tiene o que tiene con otra fecha, recién ahí es razonable hablar de desactualización, y lo planteo así al cliente con la lista de documentos.

## Pedido 3

No tengo acceso al cliente desde acá, así que redacto el pedido de información. Pediría un export de ventas 2025 (año completo) con, por producto y por mes:

- Cantidad vendida.
- Importe neto de venta, sin IVA y después de descuentos y bonificaciones.
- Costo de venta (costo unitario o costo total del período, indicando el método de valuación).
- Devoluciones y notas de crédito por producto.

Con eso calcularía margen bruto = (venta neta - costo de venta) / venta neta, por producto y total, y lo mostraría con una columna de unidades para ver los productos de bajo volumen.

Antes de calcular, pediría confirmar que el costo esté en la misma moneda que la venta y que el costo no tenga cargos de flete o impuestos internos que cambien el margen.

## Pedido 4

Que el total sea exactamente el doble es una señal fuerte de duplicación. Lo que revisaría, en orden:

- Si el export tiene una fila por vendedor y otra por marca para el mismo comprobante, o si un producto cuenta en dos marcas. Un join muchos a muchos duplica el importe.
- Si el archivo incluye una fila de total o subtotales junto con el detalle. Sumar la columna entera contaría el total dos veces.
- Si hay comprobantes repetidos: busco por número de comprobante y cuento cuántas veces aparece cada uno.
- Si el informe de Estadística usa otro criterio, por ejemplo solo facturas y no remitos, o importe sin IVA.

Lo primero que haría es contar los comprobantes únicos y comparar esa cantidad con el informe. Si el importe por comprobante coincide, el problema está en la suma y no en los datos.

## Pedido 5

Es una hipótesis plausible, y la verificaría así:

- Busco si los $290.000 coinciden con el importe de un comprobante, un pago o una nota de crédito de la otra razón social. Si coincide, hubo una imputación entre las dos.
- Comparo el export de la mañana y el de la tarde filtrando por CUIT o código de cliente, no solo por nombre. Si uno agrupa por razón social y el otro no, la diferencia puede ser de agrupación y no de saldo.
- Reviso si entre las dos exportaciones se registró algún movimiento (un pago, una factura o una reimputación) en el ERP.

Si el movimiento existe y está en la otra razón social, la deuda total del cliente no cambió; solo cambió su distribución. Lo confirmo con el detalle de documentos de ambas razones sociales.

## Pedido 6

Para sumar una columna completa en Excel:

- =SUMA(A2:A100) para un rango fijo.
- =SUMA(A:A) para toda la columna, si no hay títulos o totales en ella.
- =SUBTOTAL(9; A2:A100) si quiero que la suma respete los filtros aplicados.
- =SUMAR.SI(B2:B100; "criterio"; A2:A100) si necesito sumar con una condición.

En Excel en inglés las mismas funciones se llaman SUM, SUBTOTAL y SUMIF. Si la columna tiene números guardados como texto, la suma da cero; lo corrijo con Datos > Texto en columnas.
