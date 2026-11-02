# Activación con límites entre skills — pre-registro (02/11/26, mismo commit que el cambio)

## Qué cambia y qué se mide

La activación del 02/11/26 (`evals/runs/2026-11-02-ronda-d/activation/`) mostró que
`designing-mechanical-guards` y `unattended-run-verification` se quedan con los mismos
pedidos de `agent-ready-project`, `empirical-project-playbook` y
`empirical-system-invariants` en los tres modelos. H2 falló en Haiku: 31 de 41.

Decisión del dueño del tap (opción A): marcar el límite en las descriptions con
"Not for X: use Y", como ya hacen `delta-lakehouse` y `data-medallion-architecture`. Las
5 descriptions cambian en este commit. Además, `empirical-project-playbook` ahora dice que
cubre operar el entorno (gasto con tope, salud sin dato = STALE): la skill lo trae desde
v1.6.0, pero la description no lo decía.

Se mide otra vez la activación **con la misma semilla (20261102)**, así que los pedidos y
su orden son los mismos: lo único que cambia es el catálogo de descriptions.

## Cómo

- `python3 evals/activacion.py --out evals/runs/2026-11-02-activacion-limites --tope-usd 0.3 --modelos haiku,sonnet,opus --semilla 20261102`
- **Tope: 0,30 USD.** Con lo gastado (4,29 USD) queda dentro de los 5 USD aprobados.

## Criterios, fijados antes de ver nada

- **H2 (lo que se quiere arreglar):** las 7 de v1.3.0 elegidas en ≥ **33 de 41** positivos
  **en los tres modelos**.
- **H1 (no romper las nuevas):** las 8 nuevas en ≥ **26 de 32**, y ninguna en menos de 2 de 4.
- **H3 (precisión):** ≥ **21 de 25** pedidos no positivos con la lista vacía.
- Se reporta, pedido por pedido, qué pasó con los 5 que se desplazaban en los tres modelos.

## Lo que no se hace después de ver la tabla

No se vuelven a tocar las descriptions dentro de esta medición, no se corre otra semilla y no
se cambia la clave. Si H2 sigue fallando, se escribe así, junto con los pedidos que siguen
yéndose.

## Límites declarados

Los de la activación anterior: una corrida por modelo, pedidos escritos por el autor de cada
skill, descriptions en inglés y pedidos en español. Además, los límites se escribieron
después de ver qué pedidos se desplazaban; la misma semilla puede premiar límites hechos a
medida de esos pedidos. Una semilla nueva, en otra medición, diría si generalizan.
