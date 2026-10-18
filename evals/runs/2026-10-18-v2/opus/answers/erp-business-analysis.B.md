## Pedido 1

No veo el archivo adjunto, así que te cuento cómo lo haría:

1. **Período real, no el del nombre.** Leo el preámbulo del export: un "2026 YTD" puede cubrir 39 días o 182. Ese período declarado es el que uso.
2. **Universo.** Declaro razón social (si hay más de una, no las sumo sin decirlo), depósito y grano (producto por código, no por nombre). Saco del ranking los ítems de gasto (fletes) que figuran como producto.
3. **Stock.** Ventas solo no alcanza: necesito un export de stock, valorizado a costo, de la misma entidad, con código de producto y fechado (idealmente stock promedio, o inicial y final).
4. **Cálculo.** Rotación = costo de lo vendido / stock promedio, **agregando** por producto (promediar ratios da resultados imposibles). Controlo la identidad rotación × cobertura = días del período.
5. **Comparar con 2025.** Normalizo por días (anualizo o comparo el mismo tramo de 2025). Los montos brutos de períodos de distinto largo inventan caídas.
6. **Controles antes de entregar.** La suma del detalle tiene que dar el total del mismo archivo, sin filas TOTAL colgadas. Miro si los montos son todos enteros (señal de parseo roto). Reviso a ojo el top del ranking y cruzo el total de ventas contra un informe independiente del ERP.

Al final dejo el sello con archivo, entidad, período, hora del export, sha256 y filas leídas/descartadas. Supuesto: si no tengo el stock, entrego ventas normalizadas y dejo pedido el export que falta.

## Pedido 2

Antes de echarle la culpa al ERP, hay que descartar que la diferencia la hayamos hecho nosotros. Es la explicación cómoda y suele estar mal (un "ERP desactualizado 1,4%" terminó siendo un `abs()` nuestro).

Revisaría esto, en orden:

1. **El export contra sí mismo.** ¿La suma del detalle da el total del propio archivo? Si no da, el problema está en nuestra lectura: filas de subtotal, columnas cruzadas por posición, `replace` a mano sobre números, `abs()` que dio vuelta los saldos a favor.
2. **Entidad.** La deuda suele estar particionada por razón social. ¿El ERP muestra la misma entidad con la que se entró al hacer el export?
3. **Hora.** ¿A qué hora se sacó el export y a qué hora miraste la pantalla? Un recibo cargado entre las dos explica la brecha.
4. **Moneda.** ¿Hay saldos en dólares sumados como pesos? Si el cociente del desvío da un número redondo, buscá qué unidad o moneda representa.
5. **Filtros.** Fecha de corte, anulados y clientes excluidos tienen que ser iguales en los dos lados.

Hasta cerrar esto, no publicaría "el ERP está desactualizado". Si eso ya circuló, se retracta y se corrige en cada documento que lo citó.

## Pedido 3

Le pediría al cliente esto, con el filtro exacto:

**Informe 1, ventas con costo:** el informe de ventas por artículo del ERP que traiga importe y costo de lo vendido (si no conocés la ruta, buscá "ventas por artículo" o "rentabilidad" en el menú de Ventas/Estadística).
- **Entidad:** [razón social X]. Si hay dos, un export por cada una.
- **Período:** 01/01/2025 al 31/12/2025 inclusive.
- **Detalle:** por artículo, con **código de producto** además del nombre, cantidad, importe neto sin IVA, costo y moneda.
- **Devoluciones y anulados:** incluidos, pero separados.
- **Formato:** `.csv` o `.xlsx`, **nunca `.xls`** (trunca en 65.536 filas). Que no lo abra ni lo vuelva a guardar en Excel.
- **Cifra de control:** el total de ventas 2025 que muestra el ERP en pantalla con esos mismos filtros, y cuántos artículos aprox.

**Si el informe no trae costo:** un listado de costos por artículo (último o promedio, con fecha), también con código.

Cuando llegue: verifico el período en el preámbulo, comparo contra la cifra de control y saco los ítems de gasto (fletes). También chequeo que nadie tenga margen 100% o margen cero en masa, porque eso indica columnas cruzadas.

## Pedido 4

El doble exacto casi nunca es un error del negocio. Es una señal de lectura, y las causas típicas son estas:

1. **Fila de total sumada.** Si el export trae una fila "TOTAL GENERAL" (o subtotales por vendedor o marca) y la sumaste con el detalle, el resultado da justo 2×. Es la causa más común, sobre todo si el archivo es un reexport con columnas distintas al anterior.
2. **Dos razones sociales.** Si el export trae las dos entidades y el informe de Estadística está filtrado por una, puede dar el doble.
3. **Columna equivocada.** Puede que estés sumando por posición una columna que no es la del importe en este export. Cruzá por nombre de encabezado.

Qué haría: filtrar y sacar las filas cuyo vendedor o marca diga "TOTAL" o venga vacío, y volver a sumar. Después comparar la suma del detalle contra el total del propio archivo. También contaría las filas leídas contra las líneas del archivo y confirmaría la entidad y el período del preámbulo en los dos informes.

Cuando cierre contra Estadística dentro de una tolerancia chica, ese número queda validado.

## Pedido 5

Con esos dos datos solos no se puede decir que haya una partición entre razones sociales. Primero hay que descartar la explicación más simple: **la hora**. Entre el export de la mañana y el de la tarde pudo cargarse un recibo, una factura o una nota de crédito de ese cliente por $290.000. Nos pasó exactamente así: una "brecha" entre dos exports del mismo día era un recibo cargado en el medio.

Cómo lo verificaría:

1. Leer en el preámbulo de cada export la hora de emisión, la entidad y la fecha de corte.
2. Buscar movimientos de ese cliente con fecha de modificación entre las dos horas. Si suman $290.000, está explicado.
3. Si no aparece nada, recién ahí mirar la entidad. La deuda suele estar particionada por razón social aunque el cliente sea compartido. Si un export se sacó logueado en una y el otro en la otra, el saldo cambia. Comparar los movimientos del cliente en cada entidad y confirmar que cada parte tenga filas.
4. Descartar también moneda (saldo en dólares) y filtros distintos.

Respuesta corta: hoy no hay evidencia de una partición, y lo primero a revisar es la hora.

## Pedido 6

`=SUMA(A:A)` (en Excel en inglés, `=SUM(A:A)`). Reemplazá `A` por la letra de tu columna, o usá un rango como `=SUMA(B2:B500)`.

Ojo: si la columna tiene una fila de total al final, quedaría sumada dos veces. En ese caso usá un rango que la deje afuera.
