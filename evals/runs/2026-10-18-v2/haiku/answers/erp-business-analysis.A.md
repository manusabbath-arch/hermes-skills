## Pedido 1

No tengo el archivo adjunto, así que describo lo que haría. Primero leo el período del preámbulo del export, no del nombre "2026 YTD": un YTD puede cubrir solo 39 días. Para la rotación también necesito el stock del mismo corte y de la misma entidad; el export de ventas solo no alcanza.

Por producto, rotación = costo de venta del período / stock promedio del período. Como 2025 tiene 365 días y el YTD tiene menos, normalizo por días antes de comparar, o comparo la rotación anualizada. Agrego por suma (costo total sobre stock total) y no promedio los ratios de cada producto, porque el promedio distorsiona el resultado. Control: rotación × cobertura en días tiene que dar el período. Verifico que la suma por producto cierre contra el total del archivo y que las ventas totales coincidan con el informe de Estadística del ERP dentro de 0,15%.

Supuestos: una sola entidad, costo de venta disponible, y los productos sin stock se reportan aparte.

## Pedido 2

No daría por hecho que el ERP está desactualizado. Atribuirle la diferencia al ERP es la lectura más cómoda y también la más riesgosa, porque si se publica y resulta falsa hay que retractarla después.

Primero comparo el archivo contra sí mismo: la suma del detalle contra el total que trae el propio export. Después reviso la entidad (razón social) de cada lado, el período declarado en el preámbulo, la hora del export (un movimiento cargado después cambia el total) y las columnas por nombre, no por posición. También busco filas de subtotal o "TOTAL GENERAL" que se sumen de más.

Si la diferencia persiste, la contrasto con una fuente independiente (saldo a fecha y hora exactas desde la base, o un estado de cuenta) con tolerancia de 0,15%. Solo si el ERP queda en contra de esa fuente lo señalo como desactualización.

## Pedido 3

Le pediría al cliente un export con filtro exacto: el informe de ventas con costo o de márgenes, según el menú del ERP; período 01/01/2025 al 31/12/2025; entidad declarada; depósito; columna de código de producto; formato .csv o .xlsx (no .xls, que se corta en 65.536 filas). Le pediría también una cifra de control, por ejemplo el total de ventas 2025 del informe de Estadística.

Margen = (venta neta - costo) / venta neta, calculado sobre sumas por producto, no promediando márgenes. Antes de creer el ranking miro el top: un ítem de gasto (flete, comisión) cargado como producto no es mercadería y lo excluyo. Un margen de 0% o negativo lo tomo como señal de costo mal cargado. Si hay ventas en dólares, las convierto a pesos antes de sumar.

Sin la columna de costo no hay margen; en ese caso lo digo y no lo estimo.

## Pedido 4

Un resultado exactamente doble suele ser una fila de total viva dentro del export o un cruce por posición después de un reexport con otra cantidad de columnas. No lo tomo como un problema de criterio.

Verifico en este orden: si el archivo tiene fila de total o subtotal; los encabezados de ambos lados, cruzando por nombre de columna; la suma del detalle contra el total del propio archivo; y que la entidad y el período coincidan con el informe de Estadística. Si uno de los dos es la suma de las razones sociales y el otro es una sola, el factor 2 puede venir de ahí.

Para vendedor y marca agrupo por clave (vendedor + marca) y sumo. No indexo en un diccionario, porque un cliente puede tener más de un vendedor y se pisan filas. Hasta que cierre la comparación, no publico la cifra ni digo que el ERP está mal.

## Pedido 5

Es la hipótesis más probable, pero la verifico antes de afirmarla.

1. Confirmo la entidad de cada export. Si la deuda está particionada por razón social, un cliente compartido puede tener saldo en ambas y un export puede traer solo una. Agrupo por clave de cliente, no por nombre, porque una tilde o una variante de razón social puede hacer que el filtro caiga en "otros" sin error.
2. Busco documentos o cobros de esa entidad con fecha de modificación entre la hora del export de la mañana y la de la tarde. Si suman $290.000, ese es el mecanismo: un recibo cargado entre ambos horarios.
3. Descarto un problema de moneda: si el monto coincide con un importe en dólares sumado como pesos, lo marco.
4. Si no aparece ningún movimiento por ese monto, la brecha no es de hora sino de partición, y la verifico agrupando ambos exports por entidad y clave de cliente.

## Pedido 6

Para sumar una columna: =SUMA(B2:B500) (en Excel en inglés, =SUM).

Si el archivo trae una fila de total, SUMA la incluye y da el doble. En ese caso uso =SUBTOTALES(9;B2:B500), que ignora otros subtotales, aunque no excluye un total escrito como valor fijo. Para sumar solo un vendedor: =SUMAR.SI(A:A;"nombre";B:B).

Si los importes vienen como texto con separadores, los convierto antes de sumar; no los reemplazo a mano con un replace, porque eso puede multiplicar las cifras por 100.
