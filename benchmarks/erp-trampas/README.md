# Benchmark: trampas de exports de ERP

Ocho exports sintéticos de un ERP, cada uno con una trampa que en el proyecto de origen
terminó en una cifra publicada mal. La pregunta que mide: **dado un export con un error
conocido, ¿el agente lo ve antes de dar la cifra?** Se corre con y sin la skill
`erp-business-analysis`; la puntuación es automática (cifra correcta, cifra ingenua u
otra), sin evaluador.

Todos los datos son **ficticios** (semilla fija en `generar.py`). Sirven para evaluar
cualquier agente de análisis, no solo los de este tap.

## Las trampas

| Caso | Archivo | La trampa | Cómo se cae |
|---|---|---|---|
| `t1_total_general` | `ventas_marzo.csv` | fila `TOTAL GENERAL` al final | sumar todo da el doble |
| `t2_columnas` | `ventas_abril.csv`, `ventas_mayo.csv` | el reexport de mayo cambió el orden de columnas | sumar la columna 4 en los dos |
| `t3_periodo` | `Ventas 2026 YTD.csv` | el nombre dice "YTD", el preámbulo dice 31 días | dividir por 90 días |
| `t4_empresas` | `ventas_junio.csv` | dos razones sociales en el mismo export | no filtrar por empresa |
| `t5_monedas` | `ventas_julio.csv` | filas en pesos y en dólares | sumar las dos monedas |
| `t6_campos_muertos` | `stock.csv` | el stock mínimo es `0.00` en el 100% de las filas | contestar "ninguno bajo mínimo" |
| `t7_encoding` | `ventas_agosto.csv` | archivo en cp1252 | leído como UTF-8, `ENVÍO` no matchea y el flete queda adentro |
| `t8_duplicados` | `cobros_1_al_14.csv` | dos exports solapados pegados, y el mismo número en dos series | sumar todo, o deduplicar por número solo |

Más dos **negativos** (`n1`, `n2`): preguntas triviales sobre los mismos archivos, donde la
skill no debería cambiar la cifra ni alargar la respuesta.

## Piezas

- `generar.py` — escribe `datos/` y `verdad.json` (la verdad en memoria del generador).
- `referencia.py` — vuelve a calcular la cifra ingenua y la correcta **leyendo los
  archivos**. `tests/test_benchmark.py` exige que coincida con `verdad.json` (canario), que
  los datos publicados salgan byte a byte del generador, y que en cada trampa la ingenua
  difiera de la correcta (una trampa que no trampea no discrimina).
- `casos.json` — la pregunta de cada caso.
- `correr.py` — corre los casos con `claude -p --bare` en carpetas aisladas (solo una
  copia de `datos/`, y de la skill en la condición con skill), sin MCP ni ejecución de
  código. **Gasta dinero:** `--tope-usd` es obligatorio y corta la corrida al pasarlo;
  nunca se programa.
- `puntuar.py` — tabla por caso y por modelo: `C` correcta, `I` ingenua, `O` otra, `-` sin
  cifra (falta = fallo). Las corridas publicadas viven en `runs/<fecha>/` y el CI
  regenera su tabla y la compara.

## Límites

- **Solo CSV.** El tap solo admite la librería estándar y escribir XLSX a mano no compensa;
  la trampa del `.xls` truncado en 65.536 filas queda fuera.
- Los archivos son chicos para que un agente sin ejecución de código pueda sumarlos
  leyendo: un error de aritmética cuenta como `O`, no como trampa.
- Un modelo que ya vio este repo puede conocer las respuestas. Por eso se publica la
  semilla: para una corrida limpia, cambiarla y regenerar.

## Cómo repetirlo

```
python3 generar.py                         # solo si cambia la semilla o una trampa
python3 -m pytest tests                    # canario y reproducibilidad
python3 correr.py --out runs/<fecha> --tope-usd <tope> --modelos haiku,sonnet
python3 puntuar.py --run runs/<fecha> > runs/<fecha>/results.md
```
