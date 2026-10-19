---
name: data-medallion-architecture
description: "Use when designing an end-to-end data architecture: choosing a source (API, database, SFTP), building a medallion bronze-silver-gold lakehouse pipeline, and turning it into hypothetical-scenario dashboards and AI/ML/MCP consumption. Covers source-selection tradeoffs, ingest per source type (API, DB, SFTP), idempotent re-deliveries, deduplication and NULL handling in Silver, and layer design patterns. Not for operating an existing Delta table (vacuum, optimize, time travel): use delta-lakehouse."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [medallion, architecture, bronze-silver-gold, lakehouse, delta, duckdb, dashboard, scenarios, data-engineering]
    related_skills: [delta-lakehouse, empirical-project-playbook]
---

# Data Medallion Architecture (fuente → bronze → silver → gold → consumo)

Diseño punta a punta para un pipeline de datos: elegir la FUENTE, armar la arquitectura
**medallion** (Bronze/Silver/Gold), y alimentar consumo (AI, ML, MCP, dashboards). El
objetivo es que cada capa tenga un rol único y auditable — no una pila de pipelines
ad-hoc.

**Origen:** extensión del stack `delta-lakehouse` (2026). El lakehouse resuelve el
almacenado; esta skill resuelve el DISEÑO: qué va en cada capa, cómo elegir fuente, y cómo
llegar de una fuente cruda a un dashboard de escenarios hipotéticos.

## Cuándo NO aplicarla

Si el pedido es una pregunta puntual de formatos o herramientas (CSV vs Parquet, cómo leer un archivo), se responde **solo eso**, directo y sin agregar procesos, chequeos ni advertencias de esta skill que nadie pidió: esta skill aplica al *diseñar* un pipeline de punta a punta. Operaciones sobre una tabla Delta existente (vacuum, optimize, time-travel, lectura sin red): `delta-lakehouse`.

## Stack (validado end-to-end sobre deltalake 1.6 + duckdb 1.5 + pyarrow)

`deltalake` (tablas Delta + history/time-travel) · `duckdb` (SQL sobre Arrow; `delta_scan`
necesita descargar la extensión `delta`) ·
`pyarrow` (ingesta a `pa.Table`). Instalar en venv (PEP 668): `pip install deltalake duckdb pyarrow`.

## La capa medallion — roles (cada capa SÓLO hace lo suyo)

```
FUENTE → BRONZE → SILVER → GOLD → CONSUMO
(API/DB/SFTP)  (raw)   (clean)  (agregado)
```

**BRONZE (raw, append-only, fuente de verdad):**
- Ingestiona el dato TAL COMO llega (JSON, CSV, XML). NO se limpia, NO se dedupe.
- Append-only: una fila = un evento recibido; el historial es inmutable.
- Es la capa de auditoría / re-procesamiento: si silver/gold se rompen, se re-deduce desde
  bronze. Con Delta, el historial y el **time-travel** (`DeltaTable(path, version=n)`)
  dejan reproducir exactamente qué crudo había cuando se calculó un número.
- **Por eso no se limpia al ingestar:** si la limpieza tiene un bug, sin Bronze el dato
  original ya no existe y no hay de dónde reprocesar.

**SILVER (limpia, dedup, tipos, NULL gestionado):**
- Dedup por PK, coerce tipos (string → float/int), filtra/rellena.
- Lo que no parsea queda **NULL**, nunca un 0 ni otro sentinel dentro del dominio: un 0
  inventado se suma como dato real. Regla NULL≠0 del playbook: NULL = no medido (defecto
  a corregir), 0 = medido legítimo. Contar los NULL por campo y reportarlos.
- Es lo que consumen los análisis por defecto (gold se materializa desde acá).

**GOLD (agregada, pregunta de negocio, dashboard-ready):**
- Agrega a la dimensión de corte (producto/día/cliente). Es la capa que responde la pregunta.
- **Se verifica antes de darla por buena:** valores plausibles (rangos, signos), cada
  partición con filas, y un total que cierra contra una fuente independiente. Una Gold que
  "tiene filas" no está validada (presence ≠ utility).
- Se materializa como tabla Delta (para consumo) o como query DuckDB (para dashboards en
  vivo).

**CONSUMO (AI / ML / MCP / análisis):**
- La misma tabla que consume un modelo, agente o dashboard es la que el sistema escribe —
  nunca una copia que drifte (mismo principio que MCP-fuente-única).
- DuckDB conecta en memoria (barata, sin servidor) a silver/gold.

## Código validado (medallion completo, copia-pega)

```python
import os, tempfile, pyarrow as pa, duckdb
from deltalake import write_deltalake, DeltaTable, QueryBuilder

lake = tempfile.mkdtemp()                    # en prod: la ruta del lake
bronze, silver, gold = (os.path.join(lake, c) for c in ("bronze", "silver", "gold"))

def leer(path):  # lectura nativa; ver la nota de to_pyarrow_table en delta-lakehouse
    return pa.table(QueryBuilder().register("t", DeltaTable(path)).execute("SELECT * FROM t").read_all())

# BRONZE: crudo tal cual llegó, append-only (incluye duplicados y basura)
raw = [{"sku": "A0", "precio": "55.0", "ts": 10},
       {"sku": "A0", "precio": "55.0", "ts": 10},   # duplicado
       {"sku": "A1", "precio": "n/d", "ts": 11}]    # no parsea
write_deltalake(bronze, pa.Table.from_pylist(raw), mode="append")

# SILVER: dedup por PK + tipo coercionado; lo que no parsea queda NULL, nunca 0
def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
seen = {}
for r in leer(bronze).to_pylist():
    seen[(r["sku"], r["ts"])] = {**r, "precio": to_float(r["precio"])}
schema = pa.schema([("sku", pa.string()), ("precio", pa.float64()), ("ts", pa.int64())])
write_deltalake(silver, pa.Table.from_pylist(list(seen.values()), schema=schema), mode="overwrite")

# GOLD: agregado de consumo (duckdb sobre Arrow: no necesita la extensión delta)
con = duckdb.connect()
s = leer(silver)
g = con.execute("SELECT sku, MAX(precio) AS ultimo_precio, COUNT(precio) AS medidos "
                "FROM s GROUP BY sku ORDER BY sku").to_arrow_table()
# to_arrow_table(), no .arrow(): en duckdb 1.5 .arrow() devuelve un stream
# (RecordBatchReader) y escribirlo a Delta deja el proceso colgado al salir.
write_deltalake(gold, g, mode="overwrite")
final = leer(gold).to_pylist()
# Verificación de Gold (presence != utility): plausible y con el NULL contado, no solo "hay filas"
assert all(r["ultimo_precio"] is None or r["ultimo_precio"] > 0 for r in final)
assert sum(r["medidos"] for r in final) == 1     # 1 precio medido, 1 NULL declarado
print(final)
# [{'sku': 'A0', 'ultimo_precio': 55.0, 'medidos': 1}, {'sku': 'A1', 'ultimo_precio': None, 'medidos': 0}]
```

## Elegir la FUENTE (decisión, no reflejo)

Cada tipo de fuente se ingesta distinto; tratarlas igual pierde datos o duplica:

| Fuente | Ingesta a Bronze | Trampa típica |
|---|---|---|
| **API REST** | Incremental por cursor/`updated_since`, paginada, con reintentos con backoff; guardar el payload crudo (JSON) y la hora de extracción | Paginación que cambia mientras se lee; rate limit; respuestas cacheadas que parecen frescas |
| **Base de datos (Postgres, etc.)** | Snapshot completo para maestros chicos; CDC o incremental por `updated_at` para tablas grandes; siempre desde réplica o fuera de hora pico | Query pesada contra la base que sirve producción; borrados que un incremental no ve |
| **Archivo por SFTP (CSV)** | Copiar el archivo **tal cual** con su nombre, hora y checksum; idempotente por checksum (el mismo archivo dos veces no duplica) | Encoding y separador no declarados; archivo a medio subir; reenvío del mismo archivo |

Y para elegir entre orígenes, criterios explícitos y números, no preferencia:
- **Confiabilidad / freshness:** ¿la API falla en silencio devolviendo datos cacheados?
  (proveedor externo que falla en silencio es peor que local lento pero honesto).
- **Latencia, cuota, costo, disponibilidad.**
- **Formato:** estructurado (DB/CSV) vs no estructurado (JSONL/payloads). Ambos entran — el
  no estructurado viaja como columna list/struct/variante, no forzado a plano.
- Registrar la decisión en `empirical-project-playbook/templates/infra-decision.md`
  (mismo espíritu que el playbook:
  criterio antes de ver los datos).

## De una fuente a escenarios hipotéticos → dashboard

Flujo para llegar de la arquitectura al dashboard:

1. **Fijar la pregunta de negocio GOLD ANTES de construir** (ej. "¿qué productos sostienen
   margen > x si el costo sube un 10%?"). La capa GOLD responde esto.
2. **Definir escenarios hipotéticos** = variaciones de la agregación/segmentación sobre
   GOLD (ej. cambiar el aumento de costo, el horizonte, el descuento). No son
   queries sueltas: son la MISMA pregunta con parámetros.
3. **Materializar/consultar** con DuckDB + `delta_scan` sobre GOLD, con la query parametrizada
   por el escenario.
4. **Ponerlo en el dashboard** — un dashboard es la vista agendada de los escenarios sobre
   GOLD. La query/valor que usa el dashboard debe ser la MISMA del GOLD, nunca una copia.
5. **Medir al punto de operación real:** el dashboard muestra números sobre el tamaño real
   de datos que produce el sistema, no un sample de juguete.

## Prácticas (heredadas)

- **Presence ≠ utility:** una capa "anda" no basta — que una query de PRODUCCIÓN sobre GOLD
  responda la pregunta con valores plausibles post-deploy es la aceptación.
- **Contratos de datos** por capa (ver `empirical-system-invariants`): declarar qué columna
  promete cada capa y el guard verifica. Bronze es append-only y su contrato es "recibí el
  evento"; silver "dedup + tipo"; gold "responde la pregunta".
- **Tests herméticos** para transformaciones: `tmp_path` + delta; nunca archivos reales.
- **Un escalar donde el dominio tiene N entidades** (dict keyed por posición) es un smell —
  el medallion es una jerarquía de capas, no un solo dict.

## Plantillas

- `templates/scenario-dashboard.md` — cómo pasar de GOLD a escenarios hipotéticos → dashboard
  (parametrización de la query, cómo presentar).

## Cómo verificar esta skill

1. `skill_view(name='data-medallion-architecture')` — linked_files muestra templates/.
2. Correr el código validado: bronze append-only, silver dedup, gold agregada; DuckDB lee
   silver y responde la pregunta.
3. Rellenar `templates/scenario-dashboard.md` con un escenario real del proyecto y referenciarlo acá.

## Fuente canónica

Repo-tap `manusabbath-arch/hermes-skills` (skills/data-medallion-architecture). Los perfiles
locales tienen una COPIA instalada que es la que se carga. Al editar, hacerlo en el repo,
commit + push, re-propagar. Ver README del repo tap.
