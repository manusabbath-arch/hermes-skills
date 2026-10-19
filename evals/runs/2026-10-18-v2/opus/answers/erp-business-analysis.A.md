## Pedido 1

No me llegó el archivo adjunto, así que te cuento cómo lo haría.

Hay un límite importante: con un export de **ventas** no alcanza para calcular rotación de stock. La rotación es **costo de lo vendido / stock promedio valorizado al costo** (o en unidades: unidades vendidas / stock promedio en unidades). Con ventas tengo el numerador, pero me falta el denominador.

Necesito además:
1. **Stock por producto** al inicio y al cierre de cada período (o los saldos mensuales, que es mejor), de 2025 y de 2026.
2. **Ventas 2025** con la misma estructura, para la comparación.
3. El **costo unitario**, si querés la rotación en pesos y no en unidades.

Pasos:
- Normalizo los códigos de producto y excluyo notas de crédito o devoluciones (o las resto, según cómo vengan en el export).
- Como 2026 es YTD (hasta octubre), comparo **contra el mismo período de 2025** (enero a octubre) o anualizo los dos. Si pongo un año parcial contra un año completo, la comparación sale distorsionada.
- Rotación = unidades vendidas / stock promedio. Días de stock = días del período / rotación.
- Te armo una tabla con producto, rotación 2025, rotación 2026, la variación en % y los días de stock, y marco los productos sin movimiento o con stock promedio en cero.

Supuesto: si no hay stock histórico disponible, puedo usar el stock actual como proxy, avisando que eso sesga el resultado.

## Pedido 2

Yo no concluiría todavía que el ERP está desactualizado. Lo más habitual es que la diferencia venga del export o de cómo se sumó. Revisaría estas causas, en este orden:

1. **Fecha de corte:** el export y la pantalla del ERP pueden tener distinto "al día". Si hubo cobranzas o facturas entre un momento y el otro, la diferencia es legítima.
2. **Filtros distintos:** razón social, sucursal, vendedor, si incluye clientes inactivos o dados de baja, y si toma todos los tipos de comprobante.
3. **Signos y comprobantes:** notas de crédito, anticipos o pagos a cuenta que el ERP descuenta y que en el export quizás quedaron sumando en positivo, o al revés.
4. **Duplicados:** filas repetidas por un join, como cliente × comprobante × cuota.
5. **Moneda:** saldos en dólares mezclados con pesos, o convertidos a tipos de cambio distintos.
6. **Cheques en cartera o valores a depositar:** según la configuración, cuentan o no como deuda.

Para encontrarla rápido, compararía **cliente por cliente** el saldo del export contra el saldo del ERP, ordenaría por diferencia y analizaría los primeros casos. Casi siempre aparece el patrón (un tipo de comprobante, una razón social, una fecha).

Si después de eso el ERP sigue mostrando un saldo incorrecto para un cliente puntual, recién ahí revisaría su cuenta corriente en el ERP o lo hablaría con el proveedor del sistema.

## Pedido 3

Para el margen por producto de 2025 le pediría al cliente lo siguiente:

1. **Ventas 2025 por producto, a nivel comprobante o renglón:** fecha, tipo de comprobante (factura, NC, ND), código de producto, cantidad, precio neto **sin IVA** y descuentos aplicados. Las notas de crédito tienen que estar incluidas.
2. **Costo de los productos:** idealmente el **costo de la mercadería vendida por renglón**, si el ERP lo registra al momento de la venta. Si no, el **costo unitario por producto**, aclarando el criterio (último costo, costo promedio ponderado o costo estándar) y a qué fecha está.
3. **Maestro de productos:** código, descripción, rubro o familia y unidad de medida, para agrupar y evitar errores de unidades (caja contra unidad).
4. Si el costo no viene en la venta, las **compras 2025** por producto, para reconstruir un costo promedio.

El pedido iría así:
> "Necesitamos un export de ventas 2025 a nivel renglón (incluyendo NC), con cantidades e importes netos sin IVA, y el costo por producto indicando el criterio de valuación. Formato CSV o Excel, con códigos de producto consistentes entre ambos archivos."

Supuesto: el margen se calcula como (venta neta − costo) / venta neta, en pesos corrientes. Si hubo mucha inflación en el año, conviene aclarar que un costo de reposición actual va a subestimar el margen histórico.

## Pedido 4

Que dé **exactamente el doble** casi nunca es casualidad. Lo más probable es que el export tenga **filas de subtotal** y las estés sumando junto con el detalle.

Los informes "por vendedor y marca" suelen traer una fila de subtotal por cada vendedor (y a veces por marca) más un total general. Si sumás toda la columna, cada importe entra dos veces: una en su renglón y otra en el subtotal. Por eso da exactamente ×2.

Cómo verificarlo:
- Buscá filas con textos como "Total", "Subtotal" o "Total vendedor", o filas con el código de marca vacío.
- Filtrá esas filas y sumá solo las de detalle. Si eso coincide con Estadística, ahí estaba el problema.
- Otra opción: sumá **solo** las filas de subtotal. También deberían coincidir con el informe del ERP.

Si no hay subtotales, revisaría otras causas que también duplican:
- **Datos repetidos:** el export se generó dos veces y se pegó uno abajo del otro, o se combinaron dos archivos con el mismo período.
- **Dos columnas de importe similares,** por ejemplo neto e importe con un tipo de comprobante que se repite.
- **Un join que duplica,** por ejemplo cuando un vendedor está asignado a dos zonas.

Para sumar sin las filas de total en Excel:
`=SUMAR.SI.CONJUNTO(D:D; B:B; "<>*Total*")`
(ajustá las columnas a tu archivo).

## Pedido 5

No se puede afirmar todavía. Una diferencia de $290.000 entre la mañana y la tarde tiene explicaciones más simples que conviene descartar primero:

1. **Movimientos del día:** una cobranza, una factura o una nota de crédito registrada entre los dos exports. Es la causa más común. Buscá en la cuenta corriente comprobantes de ese cliente por $290.000 (o que sumen eso) con fecha de hoy.
2. **Imputaciones:** un pago que a la mañana estaba "a cuenta" y a la tarde se imputó, o al revés.
3. **Filtros o parámetros distintos** al generar cada export: fecha de corte, sucursal, moneda o si incluye cheques en cartera.

Sobre la partición entre razones sociales, es posible si el cliente opera con las dos empresas. Para comprobarlo:
- Mirá si alguno de los dos exports trae una columna de empresa o razón social, y filtrá ese cliente.
- Compará el saldo del cliente **en cada razón social por separado** en los dos exports. Si en uno de ellos el total es la suma de las dos empresas y en el otro solo una, la diferencia debería coincidir con el saldo de una de ellas.
- Revisá si el export se generó logueado en empresas distintas: muchos ERP exportan según la empresa activa en la sesión.

Mi conclusión: si $290.000 coincide exactamente con el saldo del cliente en una de las razones sociales, es la partición. Si coincide con un comprobante del día, es un movimiento. Esa comparación lo resuelve en pocos minutos.

## Pedido 6

Usá **SUMA**:

`=SUMA(A:A)` suma toda la columna A.
`=SUMA(A2:A100)` suma solo ese rango.

Si tu Excel está en inglés, la función es `=SUM(A:A)`. Si querés sumar con una condición, usá `=SUMAR.SI(rango; criterio; rango_suma)`.
