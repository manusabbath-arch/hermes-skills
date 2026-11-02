# Ronda E, 2026-11-02 — criterios medibles: H2 y H3 se cumplen, H1 falla en Haiku

Tablas regeneradas por el CI: `haiku/results.md` y `sonnet/results.md`. Gasto: **0,30 USD**
de un tope de 0,50 (8 sujetos y 4 evaluaciones, sin errores). Las mediciones aprobadas con
un tope de 5 USD gastaron 4,29 en total.

## Contra el pre-registro

Criterios no negativos, con skill / sin skill (de 12):

| Skill | Haiku | Sonnet | Pedido |
|---|---|---|---|
| **H1** `grounded-citations` | 1 / 0 (**+1 ✗**) | 10 / 0 (**+10**) | ≥ +4 |
| **H2** `documentation-drift-audit` | 8 / 0 (**+8**) | 10 / 0 (**+10**) | ≥ +4 |
| **H3** negativos con skill (de 4) | **4** | **4** | ≥ 3 |

- **H2 y H3 se cumplen en los dos modelos.**
- **H1 se cumple en Sonnet y falla en Haiku.**
- Con los criterios viejos, `grounded-citations` daba 5 / 0 en Sonnet (ronda C). Con los
  medibles da 10 / 0: la mitad de lo que aportaba no se veía porque el criterio pedía
  ejecutar. `documentation-drift-audit` pasa de 7 / 1 y 10 / 0 (ronda D) a 8 / 0 y 10 / 0.

## Por qué falla H1 en Haiku

Haiku leyó la skill: con skill cuesta entre 2 y 3 veces más que sin skill, como en todas las
rondas (0,0035 contra 0,0020 USD). Pero respondió en modo conversación: "no tengo búsqueda
web, esto sale de mi conocimiento", sin mencionar el ledger, `sources.py` ni las citas
numeradas. Sonnet, con la misma skill y sin herramientas, plantea el procedimiento y marca
`[unverified]` lo que dice de memoria. Leído así: **en Haiku, `grounded-citations` no
cambia la respuesta cuando no hay herramientas a mano.** Según el pre-registro, no se
reescriben los criterios otra vez para que pase.

## Qué se lee con cuidado

- **Los criterios se reescribieron después de ver las rondas C y D.** El cambio es solo de
  verbo (ejecutar → proponer) y está en el commit del pre-registro (`4a654a1`). Las
  mediciones viejas quedan publicadas como estaban.
- **Límites de siempre:** una repetición, Sonnet evalúa a Sonnet, criterios del autor de la
  skill.

## Qué sigue

- `grounded-citations` es una skill de procedimiento con herramientas: su medición útil es
  con herramientas (web y `sources.py`) y en Haiku. Ese protocolo todavía no existe en el
  tap. Hasta tenerlo, esta tabla es lo que hay.
