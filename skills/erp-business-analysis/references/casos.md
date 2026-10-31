# Casos de origen — erp-business-analysis

La skill cuenta los errores sin nombres propios. Acá está el proyecto de origen y
los casos que la forjaron. Los montos absolutos y los nombres del negocio se omiten
a propósito: quedan las proporciones, que son la lección.

## Contents

1. El proyecto fuente
2. Casos por forma de error
3. Casos de lectura del ERP
4. Casos de la base y del método

## 1. El proyecto fuente

Una distribuidora mayorista (2026), con un ERP legado sobre una base
relacional y dos razones sociales —la persona física original y una SAS que opera hoy—
sobre la misma operación física. Clientes y stock compartidos; deuda y metas
particionados por empresa. ~60 exports distintos, la base productiva consultada en
solo lectura fuera de horario comercial, y seis agentes (Claude Code, Hermes,
OpenCode, Qwen Code, Kimi Code, Antigravity) trabajando el mismo repo. En tres
semanas el proyecto retractó sus propias cifras decenas de veces y catalogó cada
retracción en un libro de errores por forma; esa es la estructura de
`templates/error-book.md`.

## 2. Casos por forma de error

| Forma | Caso |
|---|---|
| 1. Número plausible | `row[4]` era código de producto en Ventas y `Nro.` en Compras: 6 de 1.192 claves cruzaban, costo 0, **margen 99,8%** para miles de productos, decenas de cifras fabricadas. Ventas "fantasma" ×100 por un `replace(".", "")` sobre floats de `xlrd`. |
| 2. Columna N | El reexport de `VentasPorVendedorMarca` pasó de 9 a 7 columnas: con el índice heredado, `TOTAL GENERAL` sobrevivía y todo daba **exactamente el doble**. |
| 3. Rótulo | `(COMPLETO).xlsx` era la conversión del `.xls` truncado (faltaba 2,18% del año). El "2026 YTD" eran 39 días. |
| 4. Universo | Sin filtrar por razón social el semestre daba 2×. Una brecha entre dos exports del mismo día era un recibo cargado entre la mañana y la tarde. |
| 5. Verde vacío | Nueve checks en verde sobre cero elementos; una sentencia SQL con `SQL0119N` que el cliente salteaba y seguía, dejando un archivo que "devolvía filas". |
| 6. Regla repetida | "Este registro no es un cliente real" en cinco scripts: cuatro excluían 15 registros, uno 3, y cambió un ranking de morosos. |
| 7. Atribución falsa | "La deuda del ERP viene desactualizada 1,4%" era un `abs()` propio; viajó dos días hasta el panel. IVA "inflado" por el informe del ERP era sumar dólares como pesos: el cociente daba 38,6, la cotización congelada. |
| 8. Premisa | Una marca "sin rotación": 3/4 de sus productos se volvieron a vender; estaba pausada. Decisiones de inventario escritas sobre el stock de una sola empresa en otra fecha. |

## 3. Casos de lectura del ERP

- **Campos muertos en cero guardado:** stock mín/máx/crítico y los 10 indicadores de
  metas, el 100% de las filas en `0` y ninguna NULL; crédito máximo, en cambio, NULL. El
  detector correcto es `= 0` en unos y `IS NULL` en el otro.
- **Encoding:** `cp850` leyendo salida `cp1252` produjo 77 caracteres rotos
  (`ENVÍO` → `ENV═O`).
- **`SUM(DOUBLE(...))` sobre `DECIMAL(16,3)`:** el canario falló por un centavo.
- **El flete como producto:** el ítem #1 de un ranking por clientes era el costo de
  envío cargado como artículo.
- **Hora del export:** un gap de +4,20% contra la base viva se cerró a 0,15%
  cortando la base a las 08:25 del día del export.
- **Consulta lenta:** un `EXISTS` correlacionado tardaba 317 s; el `LEFT JOIN … IS
  NULL` equivalente, 6,8 s.

## 4. Casos de la base y del método

El detalle técnico está en la referencia de la base; acá, la proporción que dejó cada uno.

- **`||` con NULL:** 20 filas declaradas, 16 impresas; sobre ~190 salidas guardadas con
  denominador, 16 habían perdido filas (hasta 4,8% de una consulta). Envolver en
  `COALESCE` cuatro consultas recuperó todas sus filas sin cambiar un valor no nulo.
- **Detector de errores de cinco dígitos:** `SQL0206N` salía `ok`. De ~385 corridas, 60 no
  salieron bien; 10 eran exactamente ese error.
- **0 claves foráneas, 0 `CHECK`:** 17 controles de huérfanos escritos a mano.
- **`SUM(saldo)` sin tipo de documento:** +30% de deuda. Una definición de "cancelada" que
  metía notas de crédito como deuda viva: 9,4×.
- **Un documento en dos viajes:** `MIN(id)` elegía el viaje del turno, no el del repartidor.
- **Lo que "no existía":** el vínculo documento→viaje, dado por ~4%, cubría 8 de cada 10
  ventas; estaba en una tabla que ningún documento del repo nombraba.
- **La salida pisada:** una corrida fallida reescribió el archivo del día y el sha citado
  por un informe dejó de resolver; se perdió la evidencia de la corrida anterior.
- **Cifra heredada:** "0 de 29" era 1 de 29. **Conteo en el panel:** "293 de 293" pasó a
  rojo a las horas, porque escribir la nota siguiente lo llevó a 294.
- **Rama sin integrar:** 8 commits con un cobro corregido (un cheque sumado como efectivo)
  mientras `main` publicaba la cifra vieja.
