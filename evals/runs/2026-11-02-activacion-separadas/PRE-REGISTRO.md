# Activación con las guardas separadas — pre-registro (02/11/26, mismo commit que el cambio)

## Qué cambia

La activación con límites (`evals/runs/2026-11-02-activacion-limites/`) mostró que entre
`designing-mechanical-guards` y `agent-ready-project` una frase en la description no
alcanzaba: las dos enseñaban la línea base, los rojos declarados y el verde vacío. Decisión
del dueño del tap: **separarlas**. En este commit (v1.7.0):

- `agent-ready-project` 1.4.0 queda con el arnés del proyecto: qué checks lleva, dónde corren,
  varios agentes en un repo. Sus secciones de verde vacío y línea base con trinquete se
  reducen a dos reglas y un puntero.
- `designing-mechanical-guards` 1.2.0 pasa a ser dueña del diseño de cada guarda: recibe
  `references/diseno-de-guardas.md`, `scripts/check_baseline.py` con sus tests y la sección
  de la línea base con trinquete.
- **Los escenarios cambian de dueño:** 3 de `agent-ready-project` (180 violaciones con
  trinquete, `validar` en verde vacío, 120 chequeos con rojos ignorados) y 1 de
  `empirical-project-playbook` 1.2.2 ("un bug documentado dos veces volvió") pasan a
  `designing-mechanical-guards`, con sus mismos criterios.

## Cómo

- `python3 evals/activacion.py --out evals/runs/2026-11-02-activacion-separadas --tope-usd 0.3 --modelos haiku,sonnet,opus --semilla 20261102`
- **Misma semilla.** Los 98 pedidos son los mismos, pero no en el mismo orden ni con la misma
  clave: 4 pedidos cambian de skill esperada, y el orden lo arma `build` sobre la lista nueva.
- **Tope: 0,30 USD.** Con lo gastado (4,44 USD) queda dentro de los 5 USD aprobados.

## Criterios, fijados antes de ver nada

Positivos por modelo: `designing-mechanical-guards` 8 (4 propios + 4 que recibe),
`agent-ready-project` 4, las 7 viejas 37, las 8 nuevas 36.

- **H1 (la separación se ve):** `designing-mechanical-guards` elegida en ≥ **6 de 8** y
  `agent-ready-project` en ≥ **3 de 4**, en cada modelo.
- **H2 (no rompe el resto):** las 7 viejas en ≥ **30 de 37** y las 8 nuevas en ≥ **29 de
  36**, en cada modelo (80%).
- **H3:** ≥ **21 de 25** pedidos no positivos con la lista vacía.
- Se reportan los falsos positivos de las dos skills de guardas.

## Lo que no se hace después de ver la tabla

No se tocan descriptions, cuerpos ni escenarios dentro de esta medición, no se corre otra
semilla y no se mueve otro escenario de dueño. Si una hipótesis falla, se escribe así.

## Límites declarados

Los de siempre: una corrida por modelo, pedidos escritos por el autor de cada skill,
descriptions en inglés y pedidos en español. Además, mover escenarios a la skill que mejor
los cubre puede subir su número por definición; por eso H1 exige que también
`agent-ready-project` siga eligiéndose en lo suyo, y H2 mira al resto del tap.
