# Casos de origen — empirical-system-invariants

La skill describe los contratos en neutro. Acá está el sistema de donde salen y lo
que cada contrato detectó, para quien quiera ver un caso real.

## El sistema fuente

Un bot de trading en mercados de predicción (2026), en producción con dinero real.
Pipeline: un WebSocket de order books → modelo de probabilidad (`model_prob`) →
señales enriquecidas con varias fuentes (`edge_elo`, `edge_form`, `edge_casino`) →
guards → orden → un *shadow ledger* que registraba lo que se habría hecho.

## Lo que cada contrato detectó

| Contrato | Caso real |
|---|---|
| 1. Ingesta | Books stale procesados como frescos; una reconexión del WS hacía ver todo sano 1-2 minutos. |
| 2. Transformación | `edge_neto` / `edge_bruto` en la tabla de trades **siempre NULL**: el código que los escribía nunca se escribió. |
| 3. Enriquecimiento | `edge_elo/form/casino/h2h/residual` en `rejected_signals`: 0 de 1.384 filas no-NULL. Infra multi-fuente diseñada y nunca conectada. Confirmado por SQL; el guard lo marca ROJO con exit 1. |
| 4. Decisión → acción | Wiring fantasma: un método portado perdió su atributo interno y el trailing-stop nunca se activó en producción. Flags declarados ON que el `.env` no tenía. |
| 5. Registro | El shadow escribía filas sin un book medido (bug corregido; el contrato evita la regresión). |

## Por qué importó

Ninguno de estos rompía nada: el sistema corría, logueaba y reportaba verde. Cada uno se
encontró por suerte en una sesión de debug. La batería por ciclo convirtió esa suerte en
un ROJO con el eslabón exacto.
