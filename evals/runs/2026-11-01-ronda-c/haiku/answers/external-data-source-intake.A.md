## Pedido 1

Con el export GPS, el cálculo es: para cada cliente, buscar la distancia mínima a cualquier punto GPS de la flota, y contar los que quedan a más de 100 m. Antes de contar, hay tres cosas que conviene chequear:

- **Coordenadas:** que sean latitud y longitud en grados decimales, sin filas en cero ni con signos cambiados.
- **Qué cuenta como visita:** si cualquier punto que pasa cerca del cliente cuenta, se sobreestiman las visitas. Lo más sensato es filtrar por puntos con velocidad casi nula o por paradas de cierta duración.
- **Unidades:** la distancia tiene que estar en metros, y el radio en radianes para el BallTree.

Un ejemplo con pandas y scikit-learn (ajustá los nombres de columnas):

```python
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

gps = pd.read_csv("gps.csv", sep=";", decimal=",")
cli = pd.read_csv("clientes.csv", sep=";", decimal=",")

# Opcional: quedarte solo con paradas (velocidad baja)
# gps = gps[gps["velocidad"] < 5]

tree = BallTree(np.radians(gps[["lat", "lon"]].values), metric="haversine")
dist, _ = tree.query(np.radians(cli[["lat", "lon"]].values), k=1)
dist_m = dist[:, 0] * 6371000  # radio terrestre en metros

no_visitados = (dist_m > 100).sum()
print(f"Clientes sin visita a 100 m: {no_visitados} de {len(cli)}")
```

Si me pegás los nombres de las columnas y el separador, lo adapto.

## Pedido 2

No necesariamente. Sumar Tiempo Detención de todos los vehículos da el total de la flota, no el tiempo por vehículo. Por ejemplo, 50 vehículos con 20 horas detenidos cada uno ya suman 1000 horas, y eso es menos de una hora por día por vehículo.

Antes de sacar conclusiones, revisaría:

- **Unidad:** si el campo está en segundos, minutos u horas, el total puede estar inflado por un factor de 60 o 3600.
- **Promedio por vehículo y por día:** dividir el total entre la cantidad de vehículos y de días operativos. Ese número sí se compara con "todo el día" (alrededor de 24 horas, o la jornada laboral).
- **Duplicados o solapamientos:** si hay eventos repetidos o intervalos que se pisan, la suma crece sin que haya más tiempo real parado.
- **Qué incluye:** la detención puede contar el tiempo en clientes, en carga o en espera, no solo parado sin hacer nada.

## Pedido 3

No. Que el catálogo CKAN devuelva count 0 no alcanza para decir que no hay datos de clima. Puede pasar por varias razones:

- La búsqueda usa un término que no coincide con cómo está nombrado el dataset (por ejemplo, "meteorología", "SMN", "precipitaciones" o "temperatura").
- El dataset está en otra organización o aplica un filtro de grupo o de formato.
- Hay datasets privados, o el índice de búsqueda no está actualizado.
- La consulta tiene filtros que excluyen resultados.

Lo que sí haría es listar todos los datasets con `package_list` o `package_search` sin filtros, y revisar por nombre, tags y descripción. También conviene buscar en el portal del organismo que publica datos de clima. Hasta que eso se confirme, la conclusión correcta es "no encontré datos de clima en el catálogo con esta búsqueda", no "no hay datos".

## Pedido 4

No lo usaría como input del ruteo sin verificar antes. Que una hoja tenga más filas que otra no significa que sea la correcta. Lo que importa es el grano de cada una:

- Si Viajes tiene una fila por viaje o por parada, y Parciales tiene varias filas por el mismo viaje (tramos, cargas parciales, reintentos), usar Parciales duplicaría paradas o distancias.
- Para ver cuál es el grano, contaría los identificadores únicos (viaje, vehículo, cliente, parada) en cada hoja, y revisaría si hay filas repetidas por ese identificador.

La regla práctica: el input del ruteo tiene que tener una fila por parada a visitar, con dirección o coordenadas, y sin duplicados. Si Parciales cumple eso, es válida. Si no, conviene usar Viajes o consolidar Parciales por viaje antes de rutear.

## Pedido 5

Con `read_csv`:

```python
import pandas as pd

df = pd.read_csv("ruta/al/archivo.csv")
print(df.head())
```

En Windows, podés usar barras normales (`"C:/Users/.../archivo.csv"`) o una cadena raw (`r"C:\Users\...\archivo.csv"`).

Si el archivo viene de Excel en español, es común que necesites ajustar estos parámetros:

- `sep=";"`: separador por punto y coma.
- `decimal=","`: decimales con coma.
- `encoding="latin-1"` o `encoding="utf-8-sig"`: si aparecen caracteres raros como "Ã±" o "Ã©".

Por ejemplo:

```python
df = pd.read_csv("archivo.csv", sep=";", decimal=",", encoding="utf-8-sig")
```
