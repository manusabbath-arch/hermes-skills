# Ronda D — pre-registro (02/11/26, commiteado antes de correr)

## Qué se mide

Las 4 skills de v1.5.0, que entraron con `evals/evals.json` y sin corrida:
`tests-over-changing-data-exports`, `outbound-notification-channels`,
`recurring-report-design` y `documentation-drift-audit`. Los 5 escenarios de cada una
(1 negativo): 48 criterios no negativos y 8 negativos.

## Cómo

- `python3 evals/ronda.py --out evals/runs/2026-11-02-ronda-d --tope-usd 1.5 --modelos haiku,sonnet --semilla 20261102 --skills tests-over-changing-data-exports,outbound-notification-channels,recurring-report-design,documentation-drift-audit`
- Igual que la ronda C: sujetos Haiku y Sonnet con la skill (copia de su carpeta, sin
  `evals/` ni `tests/`) y sin nada, Read/Glob/Grep sobre su carpeta, sin comandos ni web;
  evaluador ciego Sonnet; tabla con `scripts/eval_report.py`, regenerada por el CI.
- **Tope: 1,50 USD** (16 sujetos + 8 evaluaciones). Con lo ya gastado (3,17 USD) queda
  dentro de los 5 USD aprobados.

## Criterios, fijados antes de ver nada

- **H1:** con − sin ≥ **+8** de los 48 criterios no negativos, en cada modelo (el mismo
  umbral que la ronda C usó para las skills de v1.4.0).
- **H2:** ninguna de las 4 skills con menos criterios con skill que sin ella, en ningún
  modelo.
- **H3 (negativos):** con skill cumple ≥ **7 de 8** criterios negativos en cada modelo.
- **Discriminación:** una skill y modelo donde sin skill ya cumple ≥ 90% de sus criterios no
  discrimina ahí, y se reporta así.

Referencia, no criterio: en la ronda C, las skills de v1.4.0 dieron +19 (Haiku) y +25
(Sonnet) de 48.

## Riesgo declarado antes de correr

Dos criterios de `documentation-drift-audit` están redactados como acciones ("corre el
check mecánico…", "vuelve a correr el check al final"), y los sujetos no pueden correr
comandos. Si el evaluador los lee como ejecución, esa skill sale subcontada: se reporta así
y no se reinterpreta la nota. El resto de los criterios de las 4 skills se pueden cumplir
en una conversación. No es el caso de `grounded-citations` en la ronda C, cuyos criterios
nombran comandos concretos.

## Lo que no se hace después de ver la tabla

- No se editan skills, escenarios ni criterios dentro de esta ronda.
- No se corre otra vez para elegir la mejor de dos.
- Si una hipótesis falla, se escribe que falló y por qué parece haber fallado.

## Límites declarados

Sonnet evalúa a Sonnet; una repetición por condición; criterios escritos por quien escribió
la skill; el sujeto con skill sabe que la tiene.
