## Pedido 1

No hay archivo adjunto, así que te cuento qué haría cuando llegue y qué supuestos uso.

**Antes de calcular nada:**
- Leo el período del preámbulo del export, no del nombre. "Ventas 2026 YTD" puede cubrir menos (o más) de lo que dice el rótulo. Declaro entidad (razón social), período y hora del export.
- Cruzo columnas por nombre de encabezado, no por posición. Descarto filas de subtotal/TOTAL GENERAL y verifico filas leídas vs. líneas del archivo.
- Verifico que el detalle cierre con el total del propio archivo.

**Cálculo:**
- Rotación = costo de ventas / stock promedio, calculada por producto pero con totales agregados (nunca promedio de ratios). Control: rotación × cobertura = días del período.
- Ojo: con solo ventas no alcanza. Para rotación necesito stock (idealmente valorizado, al inicio y al cierre de cada período). Supuesto: te pido también el export de stock por producto con código, para 2026 y 2025. Si solo hay stock actual, lo declaro como limitación.
- Comparación 2026 vs 2025: 2026 YTD es un período parcial, así que normalizo por días (o anualizo) antes de comparar; si no, parece caída falsa. Comparo 2025 sobre el mismo tramo calendario además del año completo.
- Excluyo ítems de gasto (fletes, etc.), miro el top del ranking antes de creerlo, y no mezclo razones sociales sin declararlo.

**Entrega:** tabla por producto (rotación, cobertura en días, variación vs 2025) más sello de procedencia (archivo, sha256, filas leídas/descartadas) y una cifra de control contra otro informe del ERP.

## Pedido 2

No voy a concluir que el ERP está desactualizado. Esa es la explicación cómoda, y en estos análisis casi siempre el desvío lo introduce nuestro propio procesamiento o una diferencia de universo.

**Qué hago, en orden:**
1. **Comparar el export contra sí mismo:** el detalle sumado vs. el total del mismo archivo. Si no cierra, el problema es de lectura (fila de total contada dos veces, filas descartadas, un `abs()` o un parseo de números).
2. **Misma entidad:** la deuda suele estar particionada por razón social. Verifico que ERP y export usen la misma entidad.
3. **Misma moneda:** sumar dólares como pesos produce desvíos enormes. Si el cociente del desvío es un número redondo, busco qué unidad o moneda representa.
4. **Mismo período y misma hora:** leo el período del preámbulo y la hora del export. Un recibo cargado entre el export y la consulta al ERP genera una brecha que no es un error de nadie.
5. **Sumar sin indexar:** si agrupé por cliente en un diccionario, pude pisar filas (hay clientes con más de un vendedor).

**Supuesto:** el ERP en pantalla es la cifra de control; el export es lo que hay que explicar. Cuantifico la brecha (monto y %) y la descompongo por estas causas. Solo si queda un residuo con todo lo anterior descartado y dentro de tolerancia (≤0,15% como referencia) puedo hablar de un problema del ERP, con evidencia.

Si ya comunicaste "el ERP está desactualizado" a alguien, mejor no repetirlo hasta cerrar esto; si resulta ser nuestro error, se retracta en todos los lugares donde se citó.

## Pedido 3

Para margen por producto de 2025 necesito dos cosas distintas: ventas y costo, por producto. Te dejo el pedido listo para mandarle al cliente. Supuesto: el ERP tiene más de una razón social y el cliente puede elegir columnas.

**Pedido de export (1): Ventas por producto 2025**
- **Informe:** el de ventas por producto/línea del menú del ERP (si no saben la ruta exacta, que busquen "ventas por artículo" en el menú de informes de ventas). Indicar con qué razón social entran.
- **Parámetros:** desde 01/01/2025 hasta 31/12/2025 inclusive; todos los depósitos y vendedores; nivel por producto (o por línea); **incluir código de producto** además del nombre, con cantidad, importe, costo y moneda si el informe los ofrece. Devoluciones/anulados separados si se puede.
- **Formato:** `.csv` o `.xlsx`, nunca `.xls` (trunca en 65.536 filas). No abrirlo ni guardarlo de nuevo en una planilla.
- **Verificación:** que nos pasen el total de ventas 2025 que muestra el ERP en pantalla con esos filtros, y la cantidad aproximada de filas.

**Pedido (2): Costo por producto**
- Si el informe de ventas no trae costo: informe de costo de ventas o de costo de mercadería por producto, mismo período, misma entidad, con código de producto.

**Repetir por cada razón social** que opere, para no mezclar entidades.

Al recibirlos: leo el período del preámbulo, cruzo por código, verifico contra la cifra de control y reviso el top del ranking (un margen de 100% en muchos productos indica un cruce roto, no un buen negocio).
