## Pedido 1

No puedo darte ese número todavía, y cualquier porcentaje que te diera hoy sería engañoso. No tengo el archivo y no puedo correr nada. Aun con el archivo, "nunca visitado a 100 m" depende del radio que elegimos nosotros, no solo de los datos.

- **El radio cambia el resultado muchísimo.** En una medición previa sobre un universo parecido, los clientes "nunca visitados" fueron 73,6 % con 50 m, 26,5 % con 150 m y 8,2 % con 400 m. Esos valores son de otro archivo y solo ilustran la forma del problema. Una diferencia de varias veces entre radios es un efecto de la definición, no una incertidumbre. Por eso conviene calcular varios radios (50, 100, 150, 250, 400 m) y publicar la tabla completa, o el 100 m con el radio escrito al lado.
- **Antes de contar, hay que ver cuántas filas pierde nuestro lector.** Un lector pensado para el export del sistema principal puede descartar filas de GPS sin avisar. Por ejemplo, un filtro que exige un id numérico descarta todo si el código de móvil es alfanumérico. Si es un Excel, también puede leer solo la primera hoja. Hay que comparar filas leídas contra filas crudas, por hoja.
- **Los clientes sin coordenada cuentan como "no visitados".** Hay que informar cuántos clientes no tienen coordenada, porque el porcentaje mide la calidad del geocodificado además de la operación. En zonas remotas esto suele ser peor.
- **Una base no es actividad.** Cientos de paradas en una misma coordenada son un depósito, no cientos de visitas. Hay que agruparlas antes de contar.
- **La distancia es en línea recta (haversine).** No es distancia de manejo, y hay que decirlo.

Pasame el archivo, o al menos los conteos de filas por hoja y cuántos clientes tienen coordenada. Con eso armo la tabla de radios.

## Pedido 2

No necesariamente. Más de mil horas en un mes casi seguro es una suma que cuenta las mismas horas varias veces, no vehículos parados todo el día.

- **Sumar entre vehículos duplica el tiempo.** Los intervalos de detención se superponen entre vehículos. Si los camiones duermen en el mismo depósito, la misma noche se cuenta una vez por camión. En una medición previa de este tipo, una columna "Tiempo Detención" sumó 1.021,5 h, y la unión real de los intervalos era 275,2 h. Esos números son de otro caso y solo muestran el orden de magnitud posible del efecto.
- **Cómo hacerlo bien:**
  1. Revisá que dentro de cada vehículo los intervalos no se pisen. Si se pisan, es un defecto de la fuente.
  2. Sumá por vehículo. Ese es el número honesto de "cuánto estuvo parado este vehículo".
  3. No sumes entre vehículos. Si necesitás un total de flota, usá la unión de intervalos y decí cuál de las dos cifras estás citando.
- **Una prueba rápida:** dividí tu total por (cantidad de vehículos × horas del mes). Si cada vehículo da cerca de 24 h por día, el dato ya es sospechoso por sí solo. Un vehículo con 24 h de motor encendido también en feriados y fines de semana es un hallazgo sobre la fuente. Puede ser un motor realmente encendido, una señal que nunca se apagó o trabajo estacionario. El archivo no alcanza para distinguirlo, así que lo dejaría como pregunta abierta.
- **"Detención", "ralentí" y "motor encendido" pueden ser reportes distintos** sobre el mismo intervalo. Confirmá qué mide exactamente esa columna antes de interpretarla.

## Pedido 3

No, un `count: 0` no alcanza para concluir que no hay datos de clima. Es el resultado más peligroso de leer como "no hay".

- **Filtrar por un valor que no existe devuelve cero igual de limpio.** En un catálogo CKAN real, filtrar por la etiqueta `clima` dio 0, mientras que filtrar por el organismo que publica sobre ese tema dio 7. Ese conteo es de otro momento y hay que re-medirlo.
- **Qué hacer:**
  - Repetí la consulta por otra vía. Usá `q=clima` (texto libre) y probá sinónimos como meteorología, temperatura, precipitación o lluvia. Un nombre de etiqueta no va en `q`.
  - Usá `fq=organization:<organismo>` con el organismo que presumiblemente publica clima.
  - Pedí `rows=0` con facets de `organization` y `res_format`, que dan los conteos de toda la consulta.
  - Comprobá que la respuesta haya sido `success: true`. Una búsqueda rota o un error puede aparecer como lista vacía. En un catálogo medido, la búsqueda por relevancia devolvía 0 para todos los términos aunque los datasets estaban en el listado completo.
  - Mirá también `package_list` y filtrá por nombre.
  - Considerá los formatos XLS y XLSX, que son miles de recursos en algunos catálogos.
- **Cuando la respuesta sea 0 tras varias vías**, escribí qué consultas hiciste y con qué resultado, y dejalo como "no encontrado por estas vías", no como "no existe".

## Pedido 4

Todavía no la usaría. Que tenga más filas y se llame "Parciales" no dice qué grano tiene.

- **Primero abrí la hoja y leé las columnas.** Una hoja de "viajes" con hora de inicio, hora de fin y distancia, pero sin destino, cliente, coordenada ni rumbo, no puede decir adónde fue nada. Suele ser una descomposición del movimiento entre paradas de motor, no un registro de viajes. Si es así, no sirve como input de un ruteo.
- **Preferí la tabla que tiene la ubicación.** Si Viajes (u otra hoja hermana) trae la columna de ubicación que necesitamos, usá esa aunque tenga menos filas.
- **Pasame la lista de columnas de las dos hojas**, o pegame el encabezado y tres filas de cada una. Con eso te digo cuál sirve y cuál no. La lista de columnas conviene dejarla escrita en el documento, para que nadie tenga que reabrir el archivo.
- **Verificá además si las hojas se componen o se pisan.** Si dos hojas suman el mismo total, por ejemplo los mismos kilómetros, son dos vistas del mismo trabajo y no se deben sumar. Una hoja combinada tipo "Todos" puede ser la suma exacta de sus hermanas.

## Pedido 5

Con `pandas.read_csv`:

```python
import pandas as pd

df = pd.read_csv("archivo.csv")
print(df.head())
```

Si hace falta, estos parámetros son los más usados:

- `sep=";"`: para CSV con punto y coma, común en configuraciones regionales en español.
- `encoding="utf-8-sig"` o `encoding="latin-1"` (o `"cp1252"`): si ves caracteres raros como `Ã±` o un BOM al inicio del primer nombre de columna.
- `decimal=","`: si los decimales usan coma.
