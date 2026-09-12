# Plantilla de ingesta — por fuente hacia tabla Delta

Para cada ORIGEN de datos, documentar antes de escribir código. El patrón canónico: origen
→ normalizar a `pa.Table` → `write_deltalake`. Declarar la tabla destino y su contrato
(via `empirical-system-invariants`) al MISMO tiempo que la ingesta.

## Campos por fuente

| Origen | Formato bruto | Transformación a Arrow | Tabla Delta destino | Partición | PK / dedup | NULL≠0 |
|--------|--------------|------------------------|---------------------|-----------|------------|--------|
| (API/WS/CSV/JSONL/DB) | | | | | | |

## Pasos (TDD/hermético)

1. **Escribir la query de producción que demostrará que la ingesta sirvió** (aceptación
   ANTES del código): qué tabla, qué columnas, qué valores plausibles post-ingesta.
2. **Test hermético:** `tmp_path` + delta/pyarrow en disco temporal; nunca archivos reales
   del host ni red real.
3. **Normalizar** el bruto a `pa.Table` (manejar tipos Arrow desde acá: int64/bool/double;
   no-estructurado → list/struct, no forzar a plano).
4. **Escritura** `write_deltalake(destino, arrow_table, partition_by=[...], mode="append")`.
5. **Gemelo de frontera:** el test debe fallar si se revierte la transformación (verificar
   que el test está en ROJO contra el código previo).
6. **Historial** `DeltaTable(destino).history()` visible tras cada escritura.

## Ejemplos de origen

### JSONL (eventos/telemetría)
```python
import pyarrow as pa
from deltalake import write_deltalake
rows = []  # pares de cada linea JSONL
write_deltalake("s3://bkt/events", pa.Table.from_pylist(rows), partition_by=["day"])
```

### SQLite/Postgres (estado operativo)
```python
import duckdb
# DuckDB lee SQLite/Postgres y la misma conexion expone delta_scan a la tabla destino
# COPY ... TO 's3://...' (FORMAT PARQUET) o normalizar via pyarrow y write_deltalake
```

### API/WS (en vivo)
```python
# normalizar payload a pa.Table (struct/json) y escribir; no forzar a columnas planas
```

## Cómo verificar la ingesta en prod (presence ≠ utility)

Luego de cada deploy, correr contra la tabla real:
```sql
SELECT COUNT(*), COUNT(IFNULL(columna_clave)), MIN(day) FROM delta_scan('<destino>')
```
esperando valores plausibles, no solo "no crasheó". El contrato (invariant) marca ROJO si
la columna clave queda NULL (NULL≠0: si el dato legítimo es 0, declararlo así).
