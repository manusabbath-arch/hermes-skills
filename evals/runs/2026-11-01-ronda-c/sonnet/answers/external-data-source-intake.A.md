## Pedido 1

No puedo calcularlo: no veo el export, no hay adjunto y no puedo correr comandos. Si te doy un número, sería inventado.

Para sacarlo vos, el cálculo tiene esta forma:

1. **Definí "visitado".** Un cliente cuenta como visitado si algún punto GPS de algún vehículo cae a ≤100 m de sus coordenadas. Conviene filtrar también por velocidad baja o por detención, porque pasar de largo por la calle no es una visita.
2. **Calculá la distancia.** Usá haversine entre cada cliente y cada punto GPS. Con muchos puntos, usá un `BallTree` con métrica haversine (sklearn) o un índice espacial, para no hacer el producto cartesiano completo.
3. **Contá los nunca visitados.** Son los clientes sin ningún punto a ≤100 m en todo el período.

Dos cosas que pueden sesgar el resultado:
- **Frecuencia de muestreo.** Si el GPS reporta cada 30–60 s, un vehículo a 40 km/h avanza 300–600 m entre puntos. Puede pasar frente a un cliente sin que quede ningún punto a 100 m. Interpolá entre puntos consecutivos o usá un radio mayor para contrastar.
- **Precisión de las coordenadas.** Si los clientes están geocodificados de forma aproximada, 100 m puede ser demasiado estricto.

Si me pegás un extracto (unas filas de clientes y de GPS con sus columnas), te armo el código exacto.

## Pedido 2

Que la suma pase de mil horas no implica que estén parados todo el día. Depende de cuántos vehículos hay y de cuánto dura el período.

- Un mes tiene unas 720 horas (30 días × 24 h). **Un solo** vehículo no puede acumular más que eso.
- Si tenés, por ejemplo, 20 vehículos, el máximo posible es unas 14.400 horas. Mil horas serían apenas un 7 %.
- Para saberlo, dividí: `horas de detención totales / (n.º de vehículos × horas del período)`.

Verificá además:
- **Unidad de la columna.** Puede estar en minutos o segundos, o en formato `hh:mm:ss` que al sumarse se interpretó mal.
- **Qué cuenta como detención.** Muchos sistemas cuentan "motor encendido sin movimiento" (ralentí) aparte de "apagado". Son situaciones operativas distintas.
- **Duplicados.** Si el export repite filas por vehículo o por evento, la suma se infla.

Mejor mirar el promedio por vehículo y por día laboral, y compararlo con la jornada real de la flota.

## Pedido 3

Todavía no podés concluir eso. Un `count: 0` en CKAN dice que **esa búsqueda** no encontró nada. No dice que no existan datos de clima.

Causas frecuentes:
- **Idioma del término.** Si el portal indexa en inglés, "clima" no coincide con "weather", "climate" o "meteorolog*". Probá también "temperatura", "precipitación" y "meteorología".
- **Sintaxis de la consulta.** En `package_search`, `q=clima` busca en el índice de texto. Si usaste filtros (`fq`) con un tag o grupo exacto, un error de mayúsculas o acentos devuelve 0.
- **Filtros acumulados.** Organización, formato o licencia pueden estar recortando todo.
- **Datasets privados o borrados.** `package_search` por defecto no los incluye.
- **Catálogo equivocado.** Los datos meteorológicos suelen estar en el servicio meteorológico nacional, no en el portal general de datos abiertos.

Qué hacer:
1. Repetí la búsqueda sin filtros y con varios sinónimos.
2. Listá los tags o grupos disponibles (`tag_list`, `group_list`) y fijate si hay algo parecido.
3. Buscá en la fuente oficial del organismo meteorológico.

Si después de eso sigue sin aparecer nada, recién ahí podés decir que ese portal no los publica.

## Pedido 4

Yo no usaría Parciales como input del ruteo solo porque tenga más filas. Más filas no quiere decir mejor input. Hay que saber qué representa cada hoja.

Preguntas antes de elegir:
- **¿Qué es una fila en cada hoja?** Si Viajes tiene una fila por viaje completo y Parciales una por tramo, escala o evento, es normal que Parciales tenga más. Son granularidades distintas.
- **¿Qué necesita el ruteo?** Normalmente paradas con ubicación, ventanas horarias, demanda y vehículo. Fijate cuál de las dos hojas tiene esas columnas.
- **¿Hay duplicados o filas parciales de un mismo viaje?** Si las filas de Parciales se repiten o son fragmentos, meterlas en el ruteo duplicaría paradas.
- **¿Las claves cierran?** Comprobá que cada fila de Parciales tenga un viaje en Viajes (id de viaje) y que los totales de Parciales sumen lo que dice Viajes.

Una comprobación rápida: agrupá Parciales por id de viaje y comparás el conteo y las sumas con Viajes. Si cierran, Parciales es el detalle y Viajes el resumen, y elegís según el nivel que necesite el ruteo. Si no cierran, hay un problema de datos que conviene resolver primero.

Si me contás las columnas de cada hoja, te digo cuál conviene.

## Pedido 5

Con `read_csv`:

```python
import pandas as pd

df = pd.read_csv("archivo.csv")
print(df.head())
```

Parámetros útiles según el caso:

```python
df = pd.read_csv(
    "archivo.csv",
    sep=";",               # separador, si no es coma
    encoding="utf-8",      # o "latin-1" / "cp1252" si hay tildes rotas
    decimal=",",           # si los decimales usan coma
    parse_dates=["fecha"], # convierte columnas a fecha
    dtype={"id": str},     # fuerza tipos, evita perder ceros a la izquierda
    usecols=["id", "fecha", "valor"],  # carga solo estas columnas
)
```

Para archivos muy grandes, leelo por partes:

```python
for chunk in pd.read_csv("archivo.csv", chunksize=100_000):
    procesar(chunk)
```

En Windows, usá una ruta cruda (`r"C:\datos\archivo.csv"`) o barras normales (`"C:/datos/archivo.csv"`) para evitar problemas con las barras invertidas.
