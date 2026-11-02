# Ronda E — pre-registro (02/11/26, commiteado antes de correr)

## Qué se mide

`grounded-citations` y `documentation-drift-audit` con sus criterios reescritos (v1.0.1):
11 criterios pedían *ejecutar* comandos (`sources.py`, el check de links), y el protocolo no
da comandos ni web. Ahora piden *proponerlo*; lo que se exige saber es lo mismo. Las
mediciones anteriores (ronda C y ronda D) siguen publicadas como estaban, y esta no las
reemplaza.

Referencia, no criterio: con los criterios viejos, `grounded-citations` dio 1/0 (Haiku) y
5/0 (Sonnet) de 12 no negativos; `documentation-drift-audit`, 7/1 y 10/0.

## Cómo

- `python3 evals/ronda.py --out evals/runs/2026-11-02-ronda-e --tope-usd 0.5 --modelos haiku,sonnet --semilla 20261103 --skills grounded-citations,documentation-drift-audit`
- El mismo protocolo que las rondas C y D. **Tope: 0,50 USD** (8 sujetos y 4 evaluaciones).
  Con lo gastado (3,99 USD) queda dentro de los 5 USD aprobados.

## Criterios, fijados antes de ver nada

- **H1:** `grounded-citations`, con − sin ≥ **+4** de 12 no negativos, en cada modelo.
- **H2:** `documentation-drift-audit`, con − sin ≥ **+4** de 12 no negativos, en cada modelo.
- **H3:** negativos con skill ≥ **3 de 4** en cada modelo.

Si H1 falla con los criterios ya medibles, la lectura es que la skill no cambia la respuesta
en una conversación sin herramientas; no se reescriben los criterios otra vez para que pase.

## Lo que no se hace después de ver la tabla

No se editan skills, escenarios ni criterios dentro de esta ronda; no se corre otra semilla.

## Límites declarados

Los de las rondas C y D: Sonnet evalúa a Sonnet, una repetición, criterios del autor de la
skill, y el sujeto con skill sabe que la tiene. Además, los criterios se reescribieron
*después* de ver las corridas anteriores: el cambio es solo de verbo (ejecutar → proponer), y
el diff está en el mismo commit que este pre-registro.
