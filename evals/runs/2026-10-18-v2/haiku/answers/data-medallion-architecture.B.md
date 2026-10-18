## Pedido 1

Supuestos: volumen diario moderado, dashboard consultado por analistas, y la pregunta de negocio es "¿cómo cambian ventas y margen si varían precio o costo?". La declaro porque no la diste.

Flujo: FUENTE → BRONZE → SILVER → GOLD → DASHBOARD.

**Bronze** (una tabla Delta por fuente, append-only):
- API de ventas: carga incremental por cursor `updated_since`, paginada, con reintentos y backoff. Guardo el JSON crudo y la hora de extracción. Cuidado con la paginación que cambia mientras se lee.
- Maestro de clientes (Postgres): snapshot completo diario, porque es chico, desde réplica y fuera de hora pico. Un incremental no ve los borrados; si importan, el snapshot es la opción.
- CSV por SFTP: copio el archivo tal cual, con nombre, hora y checksum. Idempotente por checksum.

**Silver**: dedup por PK (venta_id, cliente_id), tipos coercionados, y lo que no parsea queda NULL, nunca 0. Uno ventas con clientes.

**Gold**: agregado por producto, día y segmento de cliente, que responde la pregunta de negocio. Cada escenario es la misma query con un parámetro (precio +x %, costo +y %), no consultas sueltas.

**Consumo**: el dashboard consulta Gold con DuckDB (`delta_scan`) y la query parametrizada, sin copias que deriven.

**Verificación**: totales de Gold que cierran contra Silver, conteo de NULL por campo, y que un escenario cambie de forma esperada al mover el parámetro.

Stack: deltalake, duckdb y pyarrow.

## Pedido 2

No conviene. Si limpiás y deduplicás al ingestar, el crudo se pierde. Si la regla de limpieza tiene un bug (descarta filas válidas, convierte mal un precio), no hay de dónde reprocesar y los números publicados no se pueden reproducir. Bronze es lo que permite reconstruir Silver y Gold con time-travel.

Lo que sí podés hacer para no gastar de más:
- Validar al ingestar sin modificar: mandar a una tabla de cuarentena las filas que no cumplen un contrato mínimo (por ejemplo, PK presente), pero guardar igual el archivo original.
- Controlar la idempotencia por checksum del archivo. Es un chequeo de archivo, no de limpieza.
- Guardar metadatos (archivo, checksum, hora de carga), que cuestan casi nada.

El costo de Bronze es almacenamiento barato y a cambio tenés auditoría. Si el volumen fuera muy grande, lo decidiría con números, no por ahorrar una capa.

## Pedido 3

No recibí el archivo. Supongo columnas `venta_id, sku, fecha, precio` con encabezado.

```python
import os, hashlib, tempfile, pyarrow as pa, duckdb
from deltalake import write_deltalake, DeltaTable, QueryBuilder

LAKE = os.environ.get("LAKE", tempfile.mkdtemp())  # en prod: ruta del lake
BRONZE, SILVER, GOLD = (os.path.join(LAKE, c) for c in ("bronze", "silver", "gold"))

def leer(path):
    return pa.table(QueryBuilder().register("t", DeltaTable(path)).execute("SELECT * FROM t").read_all())

def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def bronze_ingest(csv_path):
    # Crudo: todo como texto, sin limpiar. El checksum evita cargar el mismo archivo dos veces.
    checksum = hashlib.sha256(open(csv_path, "rb").read()).hexdigest()
    if DeltaTable.is_deltatable(BRONZE) and checksum in set(leer(BRONZE)["_checksum"].to_pylist()):
        return "duplicado descartado"
    t = duckdb.sql(f"SELECT * FROM read_csv('{csv_path}', all_varchar=true)").to_arrow_table()
    t = t.append_column("_archivo", pa.array([os.path.basename(csv_path)] * t.num_rows))
    t = t.append_column("_checksum", pa.array([checksum] * t.num_rows))
    write_deltalake(BRONZE, t, mode="append")
    return f"cargadas {t.num_rows} filas"

def silver_build():
    seen = {}
    for r in leer(BRONZE).to_pylist():  # primera aparición gana por PK
        seen.setdefault(r["venta_id"], {"venta_id": r["venta_id"], "sku": r["sku"],
                                        "fecha": r["fecha"], "precio": to_float(r["precio"])})
    schema = pa.schema([("venta_id", pa.string()), ("sku", pa.string()),
                        ("fecha", pa.string()), ("precio", pa.float64())])
    write_deltalake(SILVER, pa.Table.from_pylist(list(seen.values()), schema=schema), mode="overwrite")

def gold_build():
    s = leer(SILVER)
    con = duckdb.connect()
    g = con.execute("SELECT sku, fecha, COUNT(*) AS filas, COUNT(precio) AS medidos, "
                    "SUM(precio) AS ventas FROM s GROUP BY sku, fecha ORDER BY sku, fecha").to_arrow_table()
    write_deltalake(GOLD, g, mode="overwrite")
    final = leer(GOLD).to_pylist()
    assert sum(r["filas"] for r in final) == s.num_rows  # Gold cierra contra Silver
    assert all(r["ventas"] is None or r["ventas"] >= 0 for r in final)
    return final

if __name__ == "__main__":
    print(bronze_ingest("ventas.csv"))
    silver_build()
    print(gold_build())
```

Falta un control de totales contra una cifra que informe el proveedor, además del cierre entre capas.

## Pedido 4

Bronze guardó el archivo dos veces porque el append no controlaba duplicados, y Gold sumó las dos copias. Conviene aplicar tres defensas:

1. Idempotencia en la ingesta: antes de cargar, comparar el checksum del archivo con lo ya cargado. Si existe, se descarta y se registra. El código de ingesta hace eso, así que el reenvío idéntico no entra.
2. Dedup en Silver por PK (venta_id), no por fila entera. Si llega un duplicado con otro nombre de archivo, no suma dos veces.
3. Control de totales en Gold contra una cifra independiente: el conteo de filas o el importe total que informa el proveedor. Si Gold duplicó, este control lo frena.

Para corregir lo ya publicado: no borres nada de Bronze, que es la auditoría. Reconstruí Silver y Gold desde Bronze con la dedup nueva, comparé contra la versión anterior con time-travel para cuantificar la diferencia, y recién entonces republicá el número.

Supuestos: el CSV trae una PK. Si no la trae, hay que definir una clave natural compuesta y acordarla con el proveedor. Si el reenvío tiene el mismo nombre pero otro contenido, es otro caso: lo trataría como actualización por PK y avisaría al proveedor.

## Pedido 5

No. Poner 0 hace que un precio no medido se trate como precio real: el promedio baja, el mínimo queda en 0 y la Gold queda contaminada sin que nadie lo vea.

Lo que haría:
- Bronze guarda "n/d" tal cual.
- Silver convierte a NULL lo que no parsea. Las agregaciones como AVG ignoran NULL, así que el promedio se calcula solo sobre precios medidos.
- Gold reporta cobertura, por ejemplo COUNT(precio) junto a COUNT(*), para que el dashboard muestre "promedio sobre 92 de 100 filas".
- En cada carga cuento los NULL por campo y alerto si superan un umbral.

Pregunta de fondo: ¿"n/d" significa que el precio no existe, que no se midió o que el proveedor no lo tiene? Si no existe (por ejemplo, un producto sin venta), puede ser un caso legítimo a modelar aparte. Si no se midió, es un defecto a corregir con el proveedor. En ningún caso el reemplazo es 0.

## Pedido 6

CSV es texto plano: una fila por línea, columnas separadas por un carácter, sin tipos ni esquema. Cualquiera lo abre, pero cada lectura vuelve a parsear todo, hay que adivinar encoding y separador, y no guarda tipos: "55.0" y "n/d" son igual de texto.

Parquet es binario y columnar. Guarda el esquema con tipos, comprime (suele pesar mucho menos) y las consultas leen solo las columnas que piden, saltando bloques según estadísticas. No se lee a ojo.

En la práctica: CSV para lo que llega del proveedor, porque es el formato de intercambio y Bronze lo guarda tal cual. Parquet, vía Delta, para Silver y Gold, donde importan tipos, velocidad y tamaño. Delta es Parquet más un log de transacciones que da historial y time-travel.
