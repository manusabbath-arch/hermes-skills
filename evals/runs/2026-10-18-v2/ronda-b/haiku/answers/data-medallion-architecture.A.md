## Pedido 1

Supuestos: volumen moderado (hasta decenas de millones de filas), refresco diario, sin tiempo real. Propongo una arquitectura medallion sobre un data lake en Parquet (S3, GCS o disco) y un warehouse (BigQuery, Snowflake o Postgres) para servir el dashboard.

Ingesta:
- API de ventas: extracción incremental por watermark (`updated_at`), guardando la respuesta cruda.
- Postgres (clientes): extracción incremental diaria. Si necesitás historia de cambios, CDC.
- CSV por SFTP: un job detecta archivos nuevos, calcula su hash y los archiva.

Capas:
- **Bronze:** datos crudos tal cual llegaron, append-only, con metadatos (fuente, fecha de carga, nombre de archivo, hash).
- **Silver:** tipado, limpieza, deduplicación y claves unificadas. `dim_cliente` como SCD2 desde Postgres; ventas de API y CSV unificadas en una sola tabla.
- **Gold:** modelo estrella para el dashboard: `fct_ventas` (diaria, por cliente y producto), `dim_cliente`, `dim_fecha`, y `dim_escenario` con supuestos versionados (crecimiento, precio, churn), más `fct_escenario_resultados` calculado a partir de ventas base y supuestos.

Orquestación con Airflow o Dagster, con tests de calidad (unicidad, nulos, totales conciliados contra la fuente) antes de publicar Gold.

Los escenarios son parámetros, no copias de datos: el dashboard filtra por escenario y la lógica de proyección queda en una capa versionada.

## Pedido 2

Podés hacerlo, pero no lo recomiendo. Limpiar y deduplicar al ingestar significa descartar el dato original. Si después encontrás un bug en la regla de limpieza o cambia una definición de negocio, no podés reprocesar sin pedir de nuevo el archivo al proveedor, y es posible que no tenga histórico. Además perdés la evidencia de los reenvíos duplicados, que justamente necesitás auditar.

Lo que sí podés simplificar es la transformación en Bronze: guardá el archivo crudo (es barato) y hacé la limpieza en Silver. Si el volumen es chico y el riesgo bajo, podés guardar el archivo crudo en almacenamiento sin tabla Bronze, pero la copia cruda tiene que existir.

## Pedido 3

Supuesto: no tengo una recomendación de stack confirmada para este caso, así que uso Python con pandas y Parquet. Las columnas del CSV son `id_venta`, `fecha`, `id_cliente`, `cantidad`, `precio`.

```python
import hashlib
from pathlib import Path
import pandas as pd

LAKE = Path("lake")
BRONZE = LAKE / "bronze" / "ventas"
SILVER = LAKE / "silver" / "ventas.parquet"
GOLD = LAKE / "gold" / "ventas_diarias.parquet"


def to_bronze(csv_path: Path) -> Path:
    """Guarda el CSV crudo sin modificarlo. Idempotente por hash."""
    raw = csv_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    BRONZE.mkdir(parents=True, exist_ok=True)
    dest = BRONZE / f"{digest}.csv"
    if not dest.exists():
        dest.write_bytes(raw)
    return dest


def to_silver() -> pd.DataFrame:
    """Lee todo Bronze, tipa, limpia y deduplica por id_venta."""
    frames = [pd.read_csv(f, dtype=str) for f in sorted(BRONZE.glob("*.csv"))]
    df = pd.concat(frames, ignore_index=True)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
    precio = df["precio"].where(df["precio"] != "n/d")
    df["precio"] = pd.to_numeric(precio, errors="coerce")
    df["importe"] = df["cantidad"] * df["precio"]
    df = df.drop_duplicates(subset=["id_venta"], keep="last")
    SILVER.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(SILVER, index=False)
    return df


def to_gold(silver: pd.DataFrame) -> pd.DataFrame:
    """Agregado diario para el dashboard, recalculado desde Silver."""
    gold = (silver.assign(dia=silver["fecha"].dt.date)
            .groupby("dia", as_index=False)
            .agg(total=("importe", "sum"), ventas=("id_venta", "nunique")))
    GOLD.parent.mkdir(parents=True, exist_ok=True)
    gold.to_parquet(GOLD, index=False)
    return gold


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:]:
        to_bronze(Path(arg))
    to_gold(to_silver())
```

Si necesitás quedarte con la versión más nueva de una venta corregida, guardá la fecha de carga en Bronze y ordená por ella antes del `keep="last"`.

## Pedido 4

La causa es que Silver deduplica por archivo o no deduplica, y Gold suma filas. Con el mismo CSV dos veces, cada venta entra dos veces. La solución tiene cuatro partes:

1. **Bronze idempotente por hash:** un archivo idéntico byte a byte no se guarda dos veces.
2. **Silver deduplica por clave de negocio (`id_venta`), no por archivo:** cubre reenvíos con otro orden, otro encabezado o otro nombre.
3. **Gold se recalcula desde Silver, no se acumula:** reprocesar no suma dos veces.
4. **Controles:** registrar los archivos cargados, verificar que el total de Gold coincida con la suma de ventas únicas en Silver, y alertar si un archivo llega con 100% de ids ya existentes.

Para corregir lo que ya está mal: reconstruí Silver y Gold desde Bronze con la deduplicación y compará el total contra el número que tiene el ERP o el proveedor. Definí con negocio qué hacer si un reenvío trae una venta con el mismo id pero datos distintos.

## Pedido 5

No, no lo pongas en 0. Un precio 0 significa producto gratis: el promedio baja de forma artificial y el dato faltante queda oculto como si fuera real.

Lo correcto:
- En Silver, convertí `'n/d'` a NULL y agregá una columna booleana `precio_faltante`.
- Los promedios ignoran NULL (`AVG` en SQL y `mean` en pandas lo hacen por defecto), así que no rompen nada.
- Si el dashboard necesita un valor, imputalo en Gold con una regla explícita (por ejemplo, el último precio conocido del producto) y mostralo marcado como estimado.
- Contá cuántos `'n/d'` llegan por día. Si sube, es un problema que hay que reportar al proveedor.

## Pedido 6

**CSV** es texto plano por filas. No tiene tipos (todo es texto hasta que lo parseás), no está comprimido y es legible a simple vista. Es universal, por eso sirve para intercambiar datos con proveedores.

**Parquet** es binario y columnar. Guarda el esquema con tipos, comprime mucho mejor y permite leer solo las columnas necesarias y filtrar bloques enteros. Para analítica es más rápido y más chico, pero no se abre con un editor de texto.

En la práctica: CSV para recibir del proveedor, Parquet para Bronze, Silver y Gold dentro del lake.
