# Plantilla: de GOLD a escenarios hipotéticos → dashboard

Rellenar ANTES de construir el dashboard. Un dashboard es la vista agendada de los
escenarios sobre la capa GOLD — la query que muestra debe ser la MISMA del GOLD, nunca una
copia que drifta.

## 1. Pregunta de negocio (fijada ANTES de construir GOLD)

¿Qué pregunta responde esta arquitectura?
(ej: "¿qué mercados con edge >x sobreviven el fill y generan PnL neto?")

## 2. Escenarios hipotéticos (parametrizaciones de la MISMA pregunta)

Un escenario = la misma query GOLD con un parámetro distinto. NO queries sueltas.

| Escenario | Parámetro | Query GOLD (parametrizada) | Métrica de salida |
|-----------|-----------|----------------------------|-------------------|
| Conservador | umbral edge = 0.05 | `SELECT ... FROM delta_scan('gold_...') WHERE edge >= ?` | n, EV |
| Agresivo | umbral edge = 0.10 | (misma query, ? = 0.10) | n, EV |

## 3. Cómo exponer al dashboard (DuckDB + delta_scan)

```python
import duckdb
con = duckdb.connect()
# dashboard ejecuta la query parametrizada por escenario sobre la tabla GOLD
rows = con.execute(f"SELECT ... FROM delta_scan('{gold_tbl}') WHERE edge >= {param}").fetchall()
```

## 4. Presentación en el dashboard

- Mostrar la métrica sobre el TAMAÑO REAL de datos (n por escenario), no un sample.
- Marcar el "punto de operación real" — el veredicto es al tamaño en que se midió.
- Si el dashboard usa una copia en vez de `delta_scan` directo → drifta: corregir.

## 5. Verificación (presence ≠ utility)

- La query que muestra el dashboard responde la pregunta con valores plausibles post-deploy.
- Cambiar un parámetro de escenario cambia la salida de forma esperada (gemelo de frontera);
  si un escenario es inalcanzable por cota (todo >0.05 es también >0.00), separarlo.
- Contrato de datos por capa (ver empirical-system-invariants) en verde.
