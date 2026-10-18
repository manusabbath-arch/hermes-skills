## Pedido 1

No tengo el archivo 'Ventas 2026 YTD.csv' adjunto, así que te cuento qué haría y qué supuestos tomo.

Un punto clave: las ventas por sí solas no alcanzan para calcular rotación de stock. La rotación necesita el costo de lo vendido (COGS) y el inventario promedio (o unidades vendidas / stock promedio en unidades). El export de ventas me da cantidades e importes vendidos, pero no stock. Supuesto: trabajo en unidades, y voy a necesitar un export de stock (existencias por producto, idealmente mensual o al menos inicio y cierre de cada período).

Qué haría:
1. Perfilar el CSV: columnas, formato de fechas y decimales, duplicados, devoluciones/notas de crédito (restarlas), productos sin código.
2. Agrupar por producto (código, no descripción) las unidades vendidas 2026 YTD.
3. Calcular rotación = unidades vendidas / stock promedio del período.
4. Comparar contra 2025 de forma justa: 2026 va hasta hoy (18/10), por lo que comparo contra el mismo tramo de 2025 (1/1 al 18/10), o anualizo ambos y lo aclaro. Comparar YTD contra año completo sería un error.
5. Entregar tabla por producto con rotación 2026, rotación 2025, variación y días de inventario (365/rotación), marcando productos de baja rotación, quiebres y outliers.

Además dejaría asentado que el export es una foto a una fecha de corte: si el ERP no la informa, la anoto como supuesto. Necesito también el export de ventas 2025 y los dos de stock.

## Pedido 2

No asumiría que el ERP está desactualizado: es una hipótesis más entre varias, y todavía no tengo evidencia. Antes de culpar a una de las dos fuentes, conciliaría.

Causas habituales de diferencia entre un export y la pantalla del ERP:
- Fecha de corte distinta (el export se sacó otro día u hora que lo que se ve ahora).
- Filtros distintos: moneda, sucursal, empresa, estado (incluir o no anulados, en disputa o incobrables), clientes inactivos.
- Notas de crédito, pagos a cuenta o anticipos sin imputar; deuda vencida vs. total.
- Exports con paginación o límite de filas, duplicados o totales mal sumados (filas de subtotal incluidas).
- Tipo de cambio o redondeos.
- Cache o proceso de actualización pendiente en el ERP (esto sí daría la razón a tu hipótesis).

Cómo lo verificaría:
1. Anotar fecha/hora del export y de la captura del ERP.
2. Comparar cliente por cliente (no solo el total) para ubicar dónde está la diferencia; si se concentra en pocos clientes o documentos, la causa se ve rápido.
3. Revisar si la diferencia coincide con algún documento puntual (monto exacto, un pago reciente).
4. Recién entonces, si el movimiento posterior a la fecha del export explica todo, concluir que es desfase temporal; si no, hay un problema de filtros o de datos.

Mientras tanto, reportaría ambos números con su fecha de corte, sin elegir uno.

## Pedido 3

Para el margen por producto 2025 necesito, como mínimo, ingresos y costo por producto. Supuesto: margen bruto = (venta neta - costo de lo vendido) / venta neta.

Le pediría al cliente estos exports, todos de 1/1/2025 a 31/12/2025:
1. Ventas por producto: código, descripción, unidades, importe neto (después de descuentos y devoluciones), moneda.
2. Costo de ventas por producto: costo unitario o costo total imputado de lo vendido, aclarando el método de valuación (promedio ponderado, FIFO, último costo, estándar).
3. Maestro de productos: código, descripción, línea/categoría.
4. Notas de crédito y devoluciones, si no vienen netas en el export de ventas.

Cómo lo pediría: un mensaje corto y concreto con esa lista, formato CSV o Excel, una fila por producto (o por línea de factura, que me sirve más), y que confirmen quién lo genera y la fecha de corte. Les aclararía que si el costo no está disponible por producto en el ERP, me avisen, porque entonces el margen sería solo una estimación con costo promedio.

Con eso calcularía margen en importe y en porcentaje por producto, y señalaría productos con margen negativo o muy fuera de la media. No pediría datos de gastos operativos ni de otras áreas: no hacen falta para margen bruto.
