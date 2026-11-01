## Pedido 1

No puedo darte ese número: no tengo el export ni puedo correr cálculos. Lo que sí puedo decirte es que un único "nunca visitados a 100 m" no se debería publicar todavía, por tres razones:

- **Barrido de radio.** El resultado depende del radio. Antes de publicarlo, calculá el mismo universo a 50, 100, 150, 200 y 400 m y publicá la tabla completa. En otro caso medido, el porcentaje de "nunca visitados" iba de 74% a 50 m a 8% a 400 m: la diferencia era del radio elegido, no del mundo. Ese número no es de ustedes, pero muestra el orden de lo que puede pasar.
- **Clientes sin coordenada.** Si un cliente no tiene coordenada, no puede figurar como visitado ni como no visitado. Contalos aparte y reportalos junto al resultado. Si faltan sobre todo en zonas alejadas, la baja cobertura puede deberse al geocoding y no a que no se atendió esa zona.
- **Base o depósito.** Un punto donde se repiten muchos registros de muchos vehículos es un depósito, no una visita. Excluílo antes de contar.

Además, verificá que el lector del proyecto no descarte filas del export (comparar filas leídas contra filas crudas). Si me pasás el encabezado del archivo y la cantidad de filas y clientes con coordenada, armo el cálculo con la tabla de sensibilidad.

## Pedido 2

No se puede deducir eso de la suma. Sumar `Tiempo Detención` entre vehículos cuenta varias veces los mismos intervalos: si varios camiones pasan la noche en el mismo depósito, cada uno aporta esas horas. En otro caso medido, la suma daba 1.021,5 h y la unión real de los intervalos 275,2 h, un factor de casi 3,7 sin ningún error visible.

Lo que hay que hacer:

1. Dentro de cada vehículo, chequear si sus intervalos se solapan. Si se solapan, es un defecto del origen y hay que reportarlo.
2. Si no hay solapamiento interno, sumar **por vehículo** (no entre vehículos).
3. Dividir por las horas del período (un mes tiene unas 720 h) para obtener el porcentaje de tiempo detenido de cada uno.
4. Aclarar cuál de las dos cifras se cita. Y si hay columnas parecidas (motor encendido, ralentí), declarar cuál es cuál: no se pueden mezclar.

Con 1.000 h, la lectura depende de cuántos vehículos hay. Por ejemplo, si son 20, el promedio es de 50 h cada uno, unas 7% del mes, lejos de "parados todo el día". Pasame la cantidad de vehículos y las columnas de inicio y fin para calcularlo por vehículo.

## Pedido 3

Ese cero no alcanza para concluir que no hay datos de clima. En los portales CKAN, un filtro por un valor que no existe devuelve 0 igual de limpio que una búsqueda con resultados. En un caso medido, filtrar por la etiqueta `clima` dio 0, mientras que filtrar por el organismo que publica datos meteorológicos dio 7.

Para descartar o confirmar:

- Buscá con texto libre (`q=clima`) en lugar de filtrar por etiqueta.
- Pedí los facets de `organization` para ver qué organismos publican sobre el tema, y después filtrá por `organization:<org>` con cada uno.
- Revisá que `success` sea `true`: si es `false`, la llamada falló y no es un cero real.
- Comparar el total con `package_list` y con `package_search` sin filtros, para saber si la cifra es reproducible.

Hasta que hagas eso, lo que se puede afirmar es que "la búsqueda por la etiqueta `clima` no devolvió nada", no que no hay datos. Es probable que existan en el organismo meteorológico nacional del país, pero eso hay que verificarlo en el catálogo.

## Pedido 4

No la usaría como input del ruteo todavía. Que una hoja tenga más filas no dice qué grano tiene. Hay que abrir ambas hojas y leer sus columnas.

Si Parciales trae inicio, fin, distancia y duración, pero no destino, cliente, coordenada ni rumbo, es una descomposición del movimiento entre paradas del motor, no un registro de viajes. Con esas columnas no se puede saber a dónde fue cada vehículo, así que no sirve para ruteo.

La regla es usar la tabla que tenga la columna de ubicación, aunque tenga menos filas. Si `Viajes` trae destino o coordenadas, esa es la candidata.

Pasame los nombres de columnas y la primera fila de cada hoja, y te digo cuál sirve.

## Pedido 5

Con pandas:

```python
import pandas as pd

df = pd.read_csv("archivo.csv")
```

Si los datos vienen con otro formato, ajustá los parámetros:

- `sep=";"` si el separador es punto y coma.
- `decimal=","` si los números usan coma decimal.
- `encoding="utf-8-sig"` o `encoding="cp1252"` si aparecen caracteres mal leídos, como tildes o ñ rotas.
