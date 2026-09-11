# Plantilla de contratos de datos (invariants)

Para cada ETAPA del pipeline, declarar el contrato ANTES de escribir código. Un contrato
bien formado es el test de aceptación del feature: no "hay filas" sino valores plausibles
en filas post-deploy.

## Formato por etapa

| Etapa fuente | Etapa consumidora | Campo prometido | Condición que atestigua que se pobló | Query / log de PRODUCCIÓN | NULL≠0 |

## Reglas

1. **La query se escribe ANTES del código** (build con query de aceptación pre-escrita).
2. **Condición = valores plausibles post-deploy**, no "no crashea" ni "hay filas".
3. **Gemelo de frontera:** si la condición afirma una cota (min_ratio), un test debe probar
   que el fixture efectivamente la roza — si no, pasa por accidente.
4. **NULL≠0 explícito:** marcar si "campo ausente" es defecto (NULL, a corregir) o dato
   legítimo (0 medido). Tratar 0 como fallo eterno = fatiga de alertas.
5. **Conexión nueva** para leer DB (no el pool: ve su propia transacción sin commit).
6. **Verificar intérprete** antes de interpretar salida del guard (pytest|grep pitfall).

## Ejemplo REAL (polymarket-bot — deuda documentada)

**Contrato A — enriquecimiento multi-source:**

| Fuente | Consumidor | Campo | Condición | Query prod | NULL≠0 |
|--------|-----------|-------|-----------|------------|--------|
| sports_model | rejected_signals | edge_elo | ratio de filas no-null >= 0.5 | `SELECT COUNT(*) total, COUNT(edge_elo) poblado FROM rejected_signals` | NULL=defecto (nunca se escribió) |

Estado actual del fuente (2026-09): `edge_elo/form/casino`, `edge_h2h`, `edge_residual`
siempre NULL — infra multi-source diseñada pero nunca conectada. El guard lo marca ROJO
hasta que el `sports_model.py` las poble. (No confundir con el dato medido-y-cero.)

**Contrato B — book no degenerado (shadow):**

| Fuente | Consumidor | Campo | Condición | Query prod | NULL≠0 |
|--------|-----------|-------|-----------|------------|--------|
| WS book | shadow_ledger | book_medido | 0 filas sin bids+asks no vacíos | `SELECT COUNT(*) total, SUM(CASE WHEN (bids IS NULL OR asks IS NULL OR json_array_length(bids)=0 OR json_array_length(asks)=0) THEN 1 ELSE 0 END) sin_book FROM orderbook_snapshots` | NULL=defecto |

Bug real corregido: una fila con precio degenerado sin book medido. El check evita regresión.

## Cómo correr el contrato con el guard

```bash
python scripts/invariant_guard.py --contract contrato.json --db data/prod.db
echo $?   # 0 verdes, 1 ROJO de negocio, 2 error de esquema/datos
```

## Cómo promover un check a pre-deploy gate

1. Monitorear en prod durante HORAS (no minutos) — un reconnect hace todo verse sano.
2. Establecer línea base PROPIA (canal que colapsa de 8 filas/día a 1 no cruza un absoluto
   pero sí su propia línea base).
3. Recién entonces (si hace falta) convertirlo en gate de deploy con kill switch flag OFF.
