## Pedido 1

No tengo el archivo adjunto, así que te cuento qué haría y con qué supuestos.

**Supuestos:** el CSV trae ventas por producto (código, descripción, cantidad, importe, fecha). Para rotar stock necesito además stock, y las ventas YTD no lo traen. Asumo que usaré el stock actual (o el promedio inicial/final) de un export de inventario; si no lo hay, calculo una rotación aproximada solo con ventas y lo marco como tal.

**Qué haría:**
1. Rotación por producto = costo de ventas del período / stock promedio valorizado (o unidades vendidas / stock promedio en unidades).
2. Como 2026 es YTD (hasta hoy, 18/10), **no es comparable directo con 2025 completo**. Anualizo (YTD × 365/291 días) o, mejor, comparo contra 2025 en el mismo período (1/1 al 18/10). Declaro cuál usé.
3. Calculo días de stock (365 / rotación) por producto.
4. Comparo 2025 vs 2026: variación absoluta y porcentual, y destaco productos con rotación que cae más de X% o con más de N días de stock.
5. Excluyo productos sin movimiento, devoluciones y notas de crédito, y verifico que no haya códigos duplicados o renombrados entre años.

**Salida:** tabla por producto (ventas, stock promedio, rotación 2026, rotación 2025, variación, días de stock) y un resumen de top y bottom 10. Para 2025 necesito el mismo export de ese año.

## Pedido 2

Que los totales no coincidan no prueba que el ERP esté desactualizado. Hay otras causas más probables que conviene descartar antes de culpar al ERP:

1. **Fecha de corte distinta:** el export se sacó en un momento y el ERP muestra otro. Es la causa más común.
2. **Criterio de deuda:** el ERP puede mostrar saldo neto (con notas de crédito, anticipos y recibos sin imputar) y el export solo facturas pendientes.
3. **Filtros del export:** moneda, sucursales, razones sociales, clientes inactivos, comprobantes anulados.
4. **Duplicados o cuenta corriente vs. cartera:** son vistas distintas del mismo dato.
5. **Cache o proceso de actualización del informe:** si el informe del ERP se recalcula por lotes, ahí sí podría estar viejo.

**Cómo lo verificaría:** comparo cliente por cliente, ordeno por diferencia y miro si se concentra en pocos clientes o es pareja. Si es pareja, sospecho de criterio o fecha. Si se concentra, es un tema puntual (imputaciones, notas de crédito). Chequeo también la fecha y hora de generación de ambos.

Hasta tener esa conciliación, yo diría "no coincide, causa por determinar", no "ERP desactualizado".

## Pedido 3

Para el margen por producto de 2025 necesitás dos cosas: ventas netas y costo. Le pediría al cliente estos exports, todos de 2025 completo (1/1 al 31/12):

1. **Ventas por producto:** código, descripción, cantidad, importe neto (sin IVA), descuentos, y devoluciones o notas de crédito.
2. **Costo por producto:** costo de ventas (CMV) por producto o el costo unitario vigente en cada movimiento. Aclarar el método de costeo (promedio ponderado, último costo, FIFO).
3. **Maestro de productos:** para unir por código y traer rubro y marca.

**Supuestos y cuidados:**
- Todo en la misma moneda y sin IVA.
- Si el ERP solo guarda el costo actual y no el histórico, el margen de 2025 queda distorsionado por inflación. Lo advertiría y pediría el costo al momento de cada venta.
- Margen = (venta neta − costo) / venta neta; también muestro el margen en pesos.

Mensaje para el cliente: "Para calcular el margen 2025 por producto, ¿nos pasás tres exports del ERP de 1/1/2025 a 31/12/2025: ventas por producto, costo de ventas por producto y el maestro de productos? Indicanos además el método de costeo y si los importes incluyen IVA."

## Pedido 4

Que dé **exactamente el doble** casi nunca es casualidad. Suele ser una sola causa estructural, no un error de datos:

1. **Fila de total o subtotal en el export:** el archivo trae una línea de total por vendedor o por marca además del detalle, y al sumar toda la columna contás todo dos veces. Es mi primera hipótesis.
2. **Doble nivel de agrupación:** el informe muestra vendedor y, dentro, marca, con subtotales en cada nivel. Sumar todo duplica (o triplica).
3. **Export duplicado:** el mismo período exportado dos veces o filas repetidas.
4. **Unión con un maestro:** un join que repite filas.

**Cómo lo chequearía:**
- Filtro las filas con "Total" o "Subtotal" en vendedor o marca y las excluyo; si la suma baja a la mitad, está resuelto.
- Cuento filas duplicadas exactas.
- Comparo la suma de un solo vendedor contra el ERP.

Si al sacar los totales coincide con Estadística, el informe del ERP está bien y el error era al sumar. Para evitarlo, sumaría solo las filas de detalle.

## Pedido 5

Puede ser, pero no lo confirmaría sin mirar. Una diferencia de $290.000 entre dos exports del mismo día tiene varias explicaciones posibles:

1. **Movimientos durante el día:** una factura, un cobro o una nota de crédito cargados entre la mañana y la tarde. Es lo más probable.
2. **Partición entre razones sociales:** si el cliente tiene dos CUIT o razones sociales, uno de los exports pudo agrupar por cliente (ambas) y el otro por razón social (solo una). Hay una señal clara: si $290.000 coincide con el saldo total de la otra razón social, es esto.
3. **Filtros distintos:** sucursal, moneda, vencidos vs. totales.
4. **Imputación de pagos:** un recibo imputado después reduce la deuda.

**Cómo lo resolvería:**
- Comparo ambos exports por comprobante (número, fecha, importe) y miro cuáles aparecen en uno y no en el otro. La diferencia debería sumar $290.000.
- Si son comprobantes de la otra razón social, confirmado. Si son cobros o facturas del día, es movimiento normal.
- Verifico el código o CUIT de cliente en ambos archivos.

Supuesto: es el mismo cliente y ambos exports usan los mismos filtros.

## Pedido 6

Usá **SUMA** (en inglés, **SUM**):

`=SUMA(B2:B100)`

Cambiá el rango por el de tu columna. Para sumar la columna entera: `=SUMA(B:B)`. Si solo querés sumar los valores que cumplen una condición, usá `=SUMAR.SI(A:A;"criterio";B:B)`. Según la configuración regional, el separador puede ser coma o punto y coma.
