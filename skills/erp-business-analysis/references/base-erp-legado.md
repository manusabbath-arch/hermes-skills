# La base de un ERP legado — referencia

Detalle de "La base productiva" de `erp-business-analysis`: cómo leer la base relacional
que sirve a un ERP en vivo cuando nadie la diseñó para análisis. **Origen:** la
distribuidora del proyecto de origen, un ERP sobre DB2 con ~180 tablas, dos razones
sociales y cuatro semanas de consultas en solo lectura (casi 400 corridas registradas,
1 de cada 6 no salió bien). Cada punto tiene detrás una cifra que se perdió o se publicó
mal. Lo de DB2 se marca como tal; el resto vale para cualquier motor.

## Contents

1. Medir el modelo antes de consultarlo
2. La integridad que la base no declara
3. Trampas de join
4. El universo de una suma
5. Dialecto DB2: la fila que se pierde sin error
6. Leer la salida por contenido, no por el código de salida
7. El wrapper de solo lectura
8. Exports: lo que el archivo cambia respecto de la base
9. Antes de decir "ese dato no existe"

## 1. Medir el modelo antes de consultarlo

- **Escanear cada columna por partición** (por empresa, si la base está particionada) y
  clasificarla: `CONSTANTE` (un solo valor en el 100% de las filas), `VACÍA` (todo NULL),
  `CON_DATO`, con un umbral de rareza para las casi vacías. Versionar el resultado como
  catálogo (`campos.json` o equivalente) y consultarlo **antes** de usar un campo.
- **Cero guardado ≠ NULL, y el detector cambia.** En la misma base, stock mínimo/máximo y
  metas eran `0` guardado en el 100% de las filas, y el crédito máximo era NULL. Un
  detector `IS NULL` sobre los primeros da "todo cargado". El de precio de compra fue
  otro: `> 0`, porque había líneas compradas con precio `0.0` (77 de los 105 productos
  de la cabeza de venta sin costo) y otras con precio NULL.
- **Los centinelas son el mismo modo de falla en otro tipo:** fechas `1900-01-01`,
  ids `0`, timestamps de ciclo que nunca se actualizan. El escaneo los busca igual que al
  `0.00`.
- **Una columna poblada al 96% con valores discretos no es un cero guardado**: es un
  dato. El catálogo distingue los dos; el juicio a ojo, no.
- **El nombre de la columna no dice lo que trae.** Una columna `RUTAID` en la tabla que
  une documentos con viajes valía `0` en las ~187 mil filas: la ruta estaba en otra tabla.
- **Usar un campo muerto a propósito se declara** (archivo de usos declarados con su
  motivo) y un chequeo pone rojo la consulta nueva que lee uno sin declararlo — y avisa
  cuando una declaración ya no tiene uso.

## 2. La integridad que la base no declara

El catálogo del sistema mostró **0 claves foráneas y 0 `CHECK`** en todo el schema: la
integridad la sostiene la aplicación. Consecuencia: un huérfano no rompe nada y un join
interno lo descarta sin aviso. Se escriben los controles que la base no tiene (en el
origen, 17: líneas sin documento, documentos sin cliente, cobros sin documento…) como
un archivo de consultas versionado y se corren como chequeo, no una vez.

## 3. Trampas de join

- **Clave no única:** la localidad se repetía entre departamentos; unir solo por el id de
  localidad mezclaba pueblos. Se une por la clave compuesta completa, y un chequeo verifica
  que todo join a esa tabla la use.
- **`CHAR(n)` con relleno:** el id de producto era `CHAR(20)` con espacios; cruzarlo con el
  código de un export daba 0 coincidencias **sin error**. Se cruza por la columna de código
  con `TRIM`.
- **Un LEFT JOIN con 0 coincidencias no es "no hay datos": es la clave equivocada.** Contar
  las coincidencias de cada join nuevo antes de mirar el resultado.
- **Una fila de A en dos filas de B:** un documento estaba en dos viajes (el del turno y el
  del repartidor). `MIN(id)` eligió el equivocado; la regla correcta era "la fila con el
  movimiento vacío", y aun así quedaban documentos sin ninguna fila actual, que el análisis
  tiene que **contar y declarar**, no dejar afuera.
- **La clave de un documento es `(serie, número)`**, nunca el número solo: el número se
  repite entre series. Y en ese ERP **una sola serie de ids internos** se compartía entre
  seis tipos de documento: un hueco en la numeración de un tipo no es un documento perdido.
- **Cabecera ≠ suma de líneas** por el descuento de línea: son dos cifras de venta
  distintas, ninguna es un error. Al citar una venta se dice cuál de las dos.
- **Líneas de descuento con id de documento negativo** que no tienen documento: un `SUM`
  directo sobre esa tabla sumaba de más; todo `SUM` sobre ella cruza con la cabecera.

## 4. El universo de una suma

- **Partición por empresa:** con dos razones sociales en una base, todo agregado sin el
  filtro explícito suma las dos (2× en el semestre). El id de empresa va en cada consulta,
  y la base no lo tenía en todas las tablas (150 de ~180): las compartidas se declaran.
- **Un tipo de documento que duplica la venta:** el pedido y la factura del mismo hecho.
  Excluir por nombre del tipo es frágil (un tipo nuevo entra solo); excluir por la
  **familia** del tipo, si el ERP la tiene, es cerrado.
- **`SUM(saldo)` sin filtrar tipo de documento** sobrestimaba la deuda ~30%: las notas de
  crédito y los traspasos entre fichas tienen saldo con otro signo o mueven deuda sin
  cobro.
- **Monedas:** el saldo del cliente en la ficha sumaba documentos en dos monedas sin
  convertir; la tabla de líneas no tenía columna de moneda (vive en la cabecera, se filtra
  en el join). Un export traía dos bloques de moneda y el lector descartaba el segundo
  entero en silencio: era el 92% de una brecha de 1,7%.
- **Escala:** el costo en una tabla de precios venía con ~4 dígitos de escala de más en
  parte de los productos. El factor no era constante: no se corrige por script, se carga
  bien en el ERP.
- **"Borrar" en la pantalla no borra:** un comprobante clonado y "eliminado" quedó en la
  base como pendiente y facturable. Un análisis de pendientes lo cuenta como vivo; el
  patrón se busca por consulta (mismo cliente, mismo importe, uno emitido y otro pendiente).
- **La base cambia todos los días:** toda cifra de la base citada en un documento lleva la
  fecha y hora de la corrida. 79 de ~180 tablas estaban vacías: el conteo de tablas vacías
  también envejece.

## 5. Dialecto DB2: la fila que se pierde sin error

- **Una columna NULL dentro de `||` vuelve NULL la concatenación**, y una fila con todo el
  `SELECT` armado como una cadena **desaparece de la salida**. Medido: una consulta declaró
  `20 record(s) selected.` e imprimió 16 (en un cruce, 22,5% del maestro perdido sin un
  rojo). Sobre ~190 salidas con denominador, 16 habían perdido filas. Arreglo: `COALESCE(col,
  '')` en cada operando que admite NULL — no cambia ningún valor no nulo.
- **El `NULLIF` del divisor arma el mismo NULL:** `x / NULLIF(y, 0)` con `y = 0` es NULL, y
  dentro de una cadena se lleva la fila igual. El detector de columnas no lo ve porque
  adentro ya hay un `COALESCE`; hay que nombrarlo aparte.
- **Un `CASE` (o un `SUBSTR`) en el `SELECT` se repite idéntico en el `GROUP BY`**, o la
  sentencia cae con `SQL0119N`. Para agrupar por un texto truncado: agrupar por la columna
  y truncar en el `SELECT`.
- **Errores de sintaxis de la misma familia:** `CHAR(timestamp, ISO)` → `SQL0171N`; `TRIM`
  sobre `DECFLOAT` → `SQL0420N`. `SQL0206N` casi siempre es "la columna no existe con ese
  nombre en esa tabla": se mira el catálogo, no la memoria.
- **Correlacionar por fila se paga en minutos:** un `EXISTS` correlacionado, 317 s; el
  anti-join equivalente (`LEFT JOIN … WHERE x IS NULL`), 6,8 s. Acotar la ventana antes de
  subir el timeout.
- **En horario comercial, `WITH UR`** (lectura sin bloqueos) en cada `SELECT`, y una
  franja protegida en la que no se consulta: la base sirve al ERP en vivo.

## 6. Leer la salida por contenido, no por el código de salida

- **El cliente de línea de comandos de DB2 sigue con la próxima sentencia después de un
  error** y puede salir con 0: un archivo de tres bloques "corre" con un bloque que nunca se
  ejecutó.
- **El detector de errores tiene que reconocer el formato real:** `SQL\d{4,5}[NW]`. Un
  patrón que pedía cinco dígitos dejó pasar `SQL0206N` como `ok`.
- **Filas declaradas contra filas impresas** en cada sentencia que trae el conteo; si no
  cierran, la corrida sale con un código propio y lista las columnas candidatas (las que
  admiten NULL y están en la cadena sin `COALESCE`). Una salida sin denominador **lo dice**,
  en vez de dar un verde vacío.
- **Un centinela de fin** (una sentencia final que imprime una marca) distingue "terminó" de
  "el proceso quedó vivo": en Windows `db2cmd` no termina solo.
- **Codificación:** la consola de DB2 escribe en la página de códigos de Windows (cp1252);
  el archivo que guarda el wrapper, en UTF-8. Leer el archivo en cp1252 fabrica "acentos
  doble-codificados" que dos validaciones culparon a la base. Abrir en UTF-8 y caer a cp1252
  solo si no decodifica.

## 7. El wrapper de solo lectura

Un único comando para consultar la base, con tres guardas que nacieron de un incidente
cada una:

1. **Rechaza el SQL que modifica** antes de conectarse, mirando las palabras clave sobre el
   texto **sin comentarios ni literales** (un `LIKE '%CREATE%'` no es un `CREATE`). Lista
   larga: también `CALL`, `MERGE`, `RUNSTATS`, `REORG`, `LOAD`, `IMPORT`, `EXPORT` al servidor.
2. **Rechaza escribir la salida dentro del repo:** trae nombres, identificadores fiscales y
   saldos por cliente.
3. **Una corrida fallida no pisa la salida citada:** escribe al lado con sufijo `.fallida`.
   Nació cuando un proceso tomó "la salida más nueva", que era un error, y reescribió un
   libro contable sin costo. Corolario: **no se re-corre una consulta cuya salida ya está
   citada** para "probar que la base responde"; el sha citado deja de resolver.

La credencial se lee a una variable del proceso y nunca se imprime ni se pasa por la línea
de comandos. Cada corrida queda en una bitácora (comando, duración, resultado, motivo): de
ahí salen las cifras de arriba.

## 8. Exports: lo que el archivo cambia respecto de la base

- `.xls` corta en 65.536 filas sin avisar; el archivo "completo" puede ser la conversión del
  truncado. Pedir `.csv`/`.xlsx`.
- Identificadores fiscales en notación científica, o como `float` al que perder el punto le
  inventa un dígito: cargar como texto, o `int()` antes de rellenar con ceros.
- Un filtro de subtotal que reconoce "Total" puede comerse las filas de continuación de un
  formato cabecera+líneas (84% descartado en silencio): contrastar filas leídas contra
  líneas del archivo.
- Encabezados cruzados (la columna dice vendedor y trae otra cosa) y archivos que **cambian
  de esquema entre sus propias filas**: preguntar por fila, no por archivo.
- **Un informe "a una fecha" es una foto de la hora en que se sacó**, no del cierre de ese
  día. Contra la base viva, cortar a la hora del export.

## 9. Antes de decir "ese dato no existe"

Tres veces el proyecto declaró inexistente algo que la base tenía: la rendición por viaje,
las visitas, el vínculo documento→viaje (que el repo daba en ~4% y cubría 8 de cada 10
ventas). **Buscar la tabla por lo que contiene** (columnas, conteos), no por su nombre, y
leer las tablas vacías como medición: 0 filas en los módulos de lote y vencimiento dice que
el módulo existe y nadie lo usa — a veces la capacidad ya está armada y vacía.
