# Casos de origen — empirical-project-playbook

El playbook está escrito en neutro. Acá están los dos proyectos de donde sale el
método y los incidentes que lo forjaron, con los nombres propios que en el cuerpo se
sacaron.

## Bot de trading en mercados de predicción (2026)

Sistema en producción con dinero real, construido con agentes (Claude Code, Hermes,
OpenCode, Codex). Acumuló 25+ patrones de incidente mecanizados, un registry de
findings con lifecycle y un norte de decisión único: `EDGE_CONFIRMED` sobre señales
usables.

- **Pre-registro y anti-minería:** sweet spots de precio encontrados post-hoc que no
  replicaban en muestra fresca; de ahí el pre-registro con kill/success a n≥80.
- **Shadow pre-gate:** el componente que veía señales tenía que recolectar datos aunque
  `Guard0Cap` bloqueara todas las órdenes; el *shadow ledger* se enganchó antes del
  gate y siguió creciendo con `ordenes=0`.
- **Feedback loop roto:** `would_have_won` sin resolución en el ciclo dejaba filas que
  nadie podía juzgar.
- **Dedup por etiqueta:** `profile_tag` compartido entre fuentes inflaba `n` ~4x; las
  queries ad-hoc no deduplicaban y solo `edge_verdict` daba el número correcto.
- **Campos de enriquecimiento nunca conectados:** `edge_elo/form/casino/h2h/residual`,
  0 de 1.384 filas no-NULL en `rejected_signals`.
- **Wiring fantasma:** el trailing-stop nunca se activó en producción.
- **Protocolo mal desde el origen:** un WebSocket que ningún test detectó porque los
  tests mockeaban el protocolo viejo.
- **Costo in-cycle:** un bootstrap de 5.000 réplicas compartido con el CLI bloqueaba el
  loop 348 s; los ciclos lentos caían en múltiplos exactos de un `_EVERY_N_CYCLES`.
- **Memoria y estado:** veredictos persistidos en engram con `topic_key` estable; health
  y checks expuestos por MCP para que agentes y dashboards lean el mismo dato.

## Análisis de negocio sobre un ERP (2026)

Una distribuidora mayorista con un ERP legado y dos razones sociales, analizada por
seis agentes sobre el mismo repo. Aportó al playbook la confirmación de que **la prosa
no frena**: la regla del denominador se escribió en un check y al día siguiente estaba
violada en seis más; con check, 42 de 42 decisiones tenían dueño, y sin check, 1 de 29
planes tenía su spec. El detalle de ese proyecto vive en la skill
`erp-business-analysis` y en `agent-ready-project`.
