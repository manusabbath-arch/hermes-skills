## Pedido 1

No hay archivo adjunto, así que te cuento cómo lo haría y con qué supuestos.

**Antes de calcular nada**
- Leo el período del preámbulo del export, no del nombre. "YTD" puede ser cualquier cosa (ya vimos un "2026 YTD" que eran 39 días). Si no coincide con el año a la fecha real, lo declaro.
- Rotación necesita costo de ventas (o unidades vendidas) y stock. Un export de ventas solo no alcanza: voy a necesitar el stock valorizado o en unidades, idealmente a inicio y fin de cada período, para usar stock promedio. Supuesto: si no lo tengo, uso el stock del ERP con su fecha y lo marco como foto única.
- Supuesto de entidad: una sola razón social. Si el ERP tiene varias, filtro por una y lo declaro; no sumo entre entidades.

**Método**
- Cruzo por nombre de columna (código de producto), imprimiendo el encabezado de cada export. Descarto filas de TOTAL.
- Excluyo ítems de gasto (flete, etc.) y miro el top del ranking antes de creerlo.
- Comparo 2026 contra el mismo tramo de 2025 (mismos días), o normalizo por día. Comparar 39 días contra 365 muestra una caída falsa.
- Rotación y cobertura se agregan (suma de ventas / suma de stock), no se promedian ratios por producto. Chequeo la identidad rotación × cobertura = días del período.
- Plausibilidad: si todos los montos son enteros, sospecho de parseo; si algún producto sale vendiendo a costo, reviso.

**Entrega**: tabla por producto con ventas, stock, rotación y cobertura para ambos períodos, más sello de procedencia (archivo, entidad, período declarado, hora del export, sha256, filas leídas y descartadas) y un canario: el total de ventas contra otro informe del ERP, tolerancia 0,15%.

## Pedido 2

No concluiría que el ERP está desactualizado todavía. Primero hay que descartar que el desvío sea nuestro: en el antecedente más parecido, "el ERP viene desactualizado 1,4%" era un `abs()` de nuestro propio código.

**Orden de chequeo**
1. **El export contra sí mismo**: la suma del detalle contra el total del mismo archivo. Si no cierra, el problema está en mi lectura (fila TOTAL duplicada, columnas corridas, filas descartadas en silencio), no en el ERP.
2. **Entidad**: la deuda está particionada por razón social. Confirmo que ambos números sean de la misma entidad.
3. **Moneda**: sumar dólares como pesos fabrica diferencias. Si el cociente del desvío es un número redondo, busco qué unidad o moneda representa.
4. **Período y hora**: leo la fecha de corte y la hora del export. Un recibo cargado entre la mañana y la tarde explica brechas chicas. Si hay base viva, la corto a la hora del export.
5. **Parseo**: nada de `replace` manual de separadores, ni indexar por cliente en un dict (hay clientes con más de un vendedor y se pisan filas). Sumo.
6. **Cobertura**: que cada parte tenga filas y que el filtro no se haya caído por una tilde.

**Resultado**: reporto la diferencia con su causa y el sello de procedencia. Si tras todo esto sigue una brecha mayor a 0,15% contra el ERP, recién ahí es un hallazgo del ERP, con evidencia. Supuesto: comparamos la misma entidad y moneda hasta que se demuestre otra cosa.

## Pedido 3

No puedo hablar con el cliente desde acá, pero te dejo el pedido listo para enviar. Un pedido de export tiene que llevar el filtro exacto, no "el margen de 2025".

**Texto para el cliente**

Hola, necesitamos dos informes del ERP, ambos del 01/01/2025 al 31/12/2025:

1. **Ventas por producto** (informe de ventas por artículo del menú de ventas): período 01/01/2025 a 31/12/2025, una sola razón social (indicar cuál), todos los depósitos, con columnas código de producto, descripción, cantidad vendida, importe neto y moneda.
2. **Costo de mercadería vendida por producto** del mismo período y entidad, con código de producto, cantidad y costo total. Si el ERP no lo da, el costo unitario vigente más la fecha de ese costo.

Formato: .csv o .xlsx, nunca .xls (tiene tope de 65.536 filas). Si pueden elegir columnas, siempre incluir el código de producto.

**Cifra de control**: pásennos el total de ventas netas 2025 que muestra el ERP en pantalla (ese número y la fecha y hora en que lo sacaron), para verificar que el archivo llegó completo.

**Supuestos míos**: margen = (ventas netas − costo) / ventas netas, por producto, en la moneda declarada, excluyendo ítems de gasto como el flete. Cuando llegue, valido el período en el preámbulo (no en el nombre del archivo), cruzo por nombre de columna y controlo la plausibilidad: un distribuidor no vende a costo, y un margen de 100% casi seguro es una columna corrida.
