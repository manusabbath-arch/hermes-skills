## Pedido 1

Supuestos: volumen de millones de filas (no miles de millones), equipo chico, sin plataforma de datos previa. Propongo arquitectura medallion (Bronze, Silver, Gold) sobre almacenamiento de objetos con Parquet, orquestada por Dagster o Airflow.

**Fuentes y Bronze (crudo, inmutable, append-only)**
- API REST de ventas: extracción incremental por fecha de modificación o cursor, con paginación y reintentos. Se guarda la respuesta tal cual (JSON o Parquet) en `bronze/ventas_api/ingest_date=YYYY-MM-DD/`.
- Maestro de clientes en Postgres: snapshot diario o CDC liviano (columna `updated_at`) hacia `bronze/clientes/`.
- CSV diario por SFTP: se copia el archivo original sin tocar a `bronze/ventas_csv/`, con nombre y fecha.
- A cada registro se le agregan metadatos: `_ingested_at`, `_source`, `_batch_id`, `_file_name`. Nada se borra ni se corrige en esta capa.

**Silver (limpio, conformado)**
- Tipado, normalización de fechas, monedas y códigos, y deduplicación por clave de negocio (`id_venta`) quedándose con el registro más reciente.
- Unificación de ventas API y CSV en un esquema único. Si ambas fuentes se solapan, se define una regla de precedencia.
- Validaciones de calidad (nulos, rangos, integridad contra clientes). Lo que falla va a una tabla de cuarentena, no se descarta.
- Clientes como dimensión con historia (SCD2) si importa el cambio de segmento o región.

**Gold (modelo para consumo)**
- Esquema estrella: `fact_ventas`, `dim_cliente`, `dim_fecha`, `dim_producto`.
- Agregados por mes, región, segmento y producto.
- Para escenarios: una tabla de supuestos (`escenarios`: crecimiento, descuento, mix, estacionalidad) y vistas que aplican esos parámetros sobre la base histórica. Así el dashboard recalcula sin tocar los datos reales.

**Consumo**: Metabase, Superset o Streamlit sobre Gold, con parámetros de escenario como filtros.

**Transversal**: orquestación diaria con dependencias, tests de datos (dbt tests o Great Expectations), alertas ante falla o archivo faltante, y linaje documentado.

## Pedido 2

Respuesta corta: se puede, pero no te lo recomiendo. Ahorrás una capa y a cambio perdés cosas que después cuestan caras.

**Por qué conviene mantener Bronze**
- **Reprocesamiento**: si descubrís un bug en tu regla de deduplicación o limpieza (y lo vas a descubrir), sin el dato crudo no podés rehacer el historial. La API puede no devolver lo mismo mañana, y el CSV de SFTP suele purgarse.
- **Auditoría y trazabilidad**: podés demostrar qué llegó exactamente y cuándo.
- **Depuración**: cuando un número del dashboard no cierra, comparás contra lo original.
- **Desacople**: la ingesta queda simple y robusta (copiar y guardar). La lógica de negocio cambia seguido y vive aparte, en Silver.
- **Esquema cambiante**: si la fuente agrega o renombra una columna, Bronze no se rompe.

**Costo real de Bronze**: bajo. Es Parquet comprimido en almacenamiento barato. Se puede aplicar retención (por ejemplo 12 meses) para controlar el gasto.

**Alternativa mínima si realmente querés simplificar**
- Mantener Bronze pero sin tabla formal: guardar solo los archivos crudos (JSON de la API, CSV originales, dump de Postgres) en un bucket con fecha, y leerlos directamente desde Silver.
- Esa es la versión liviana de Bronze y conserva el 90% del beneficio.

**Cuándo sí podrías saltearla**: datos pequeños, fuente que se puede volver a consultar completa e idéntica en cualquier momento (por ejemplo, una tabla Postgres que siempre podés releer), y sin requisitos de auditoría. Aun así, tu caso incluye una API y un SFTP, que no cumplen esa condición.

## Pedido 3

Stack que recomiendo: Python + DuckDB + Parquet (liviano, sin servidor, rápido para este volumen). Para producción lo orquestaría con Dagster o Airflow y pasaría Silver/Gold a dbt-duckdb. Supuestos: el CSV tiene columnas `id_venta, fecha, id_cliente, producto, cantidad, precio_unitario`, separador coma, y no hay archivo adjunto, por eso el código es genérico y habría que ajustar nombres de columnas al archivo real.

```python
# pipeline_medallion.py
import duckdb
from pathlib import Path
from datetime import datetime, timezone
import shutil, sys

BASE = Path("datalake")
BRONZE, SILVER, GOLD = BASE / "bronze", BASE / "silver", BASE / "gold"
for d in (BRONZE, SILVER, GOLD, SILVER / "cuarentena"):
    d.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()

def bronze(csv_path: str) -> Path:
    """Copia cruda + metadatos. No se limpia nada."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    raw = BRONZE / f"raw_{ts}_{Path(csv_path).name}"
    shutil.copy(csv_path, raw)                       # archivo original intacto
    out = BRONZE / f"ventas_{ts}.parquet"
    con.execute(f"""
        COPY (
            SELECT *, '{raw.name}' AS _file_name,
                   now() AS _ingested_at, 'sftp_csv' AS _source
            FROM read_csv('{raw}', all_varchar=true, header=true)
        ) TO '{out}' (FORMAT parquet)
    """)
    return out

def silver(bronze_files_glob: str):
    """Tipado, validación, deduplicación, cuarentena."""
    con.execute(f"""
        CREATE OR REPLACE TABLE stg AS
        SELECT
            trim(id_venta)                          AS id_venta,
            try_cast(fecha AS DATE)                 AS fecha,
            trim(id_cliente)                        AS id_cliente,
            upper(trim(producto))                   AS producto,
            try_cast(cantidad AS INTEGER)           AS cantidad,
            try_cast(precio_unitario AS DECIMAL(18,2)) AS precio_unitario,
            _file_name, _ingested_at
        FROM read_parquet('{bronze_files_glob}')
    """)
    # Registros inválidos -> cuarentena (no se descartan)
    con.execute(f"""
        COPY (SELECT * FROM stg
              WHERE id_venta IS NULL OR fecha IS NULL OR id_cliente IS NULL
                 OR cantidad IS NULL OR cantidad <= 0
                 OR precio_unitario IS NULL OR precio_unitario < 0)
        TO '{SILVER / "cuarentena" / "ventas_invalidas.parquet"}' (FORMAT parquet)
    """)
    # Válidos + deduplicación: queda la última versión por id_venta
    con.execute(f"""
        COPY (
            SELECT * EXCLUDE (rn, _file_name, _ingested_at),
                   cantidad * precio_unitario AS importe
            FROM (
                SELECT *, row_number() OVER (
                    PARTITION BY id_venta ORDER BY _ingested_at DESC) AS rn
                FROM stg
                WHERE id_venta IS NOT NULL AND fecha IS NOT NULL
                  AND id_cliente IS NOT NULL AND cantidad > 0
                  AND precio_unitario >= 0
            ) WHERE rn = 1
        ) TO '{SILVER / "ventas.parquet"}' (FORMAT parquet)
    """)

def gold():
    """Agregados listos para el dashboard."""
    silver_path = SILVER / "ventas.parquet"
    con.execute(f"""
        COPY (
            SELECT date_trunc('month', fecha) AS mes,
                   producto,
                   count(DISTINCT id_venta)   AS n_ventas,
                   sum(cantidad)              AS unidades,
                   sum(importe)               AS ventas_total,
                   count(DISTINCT id_cliente) AS clientes
            FROM read_parquet('{silver_path}')
            GROUP BY 1, 2
            ORDER BY 1, 2
        ) TO '{GOLD / "ventas_mensuales.parquet"}' (FORMAT parquet)
    """)

def checks():
    n = con.execute(f"SELECT count(*), count(DISTINCT id_venta) "
                    f"FROM read_parquet('{SILVER / 'ventas.parquet'}')").fetchone()
    assert n[0] == n[1], "Silver tiene id_venta duplicados"
    print(f"OK Silver: {n[0]} ventas únicas")

if __name__ == "__main__":
    csv = sys.argv[1]
    bronze(csv)
    silver(str(BRONZE / "ventas_*.parquet"))   # lee todo el histórico de Bronze
    gold()
    checks()
    print("Pipeline completo ->", GOLD / "ventas_mensuales.parquet")
```

Uso: `python pipeline_medallion.py ventas_2026-10-18.csv`

Cómo funciona y qué falta para producción:
- Bronze conserva el archivo original y su copia en Parquet sin alterar valores (todo como texto).
- Silver lee todo Bronze, por eso la deduplicación funciona también entre días distintos.
- Gold queda leíble directo desde Metabase, Streamlit o DuckDB.
- Próximos pasos: parametrizar rutas, agregar el join con `dim_cliente` desde Postgres, tests (dbt o pytest) y programar la corrida diaria con Dagster.
