# Ronda D, 2026-11-02 — las 4 skills de v1.5.0: las tres hipótesis se cumplen

Tablas regeneradas por el CI desde las notas crudas: `haiku/results.md` y `sonnet/results.md`.
Gasto: **0,67 USD** de un tope de 1,50 (16 sujetos y 8 evaluaciones, 24 llamadas, ningún
error, todas las notas legibles y completas). En total, las mediciones aprobadas con un tope
de 5 USD gastaron 3,84.

## Contra el pre-registro

Criterios no negativos cumplidos, con skill / sin skill (de 12 por skill):

| Skill | Haiku | Sonnet |
|---|---|---|
| `tests-over-changing-data-exports` | 11 / 4 | 12 / 4 |
| `outbound-notification-channels` | 11 / 2 | 11 / 2 |
| `recurring-report-design` | 8 / 2 | 11 / 2 |
| `documentation-drift-audit` | 7 / 1 | 10 / 0 |
| **Total (de 48)** | **37 / 9 (+28)** | **44 / 8 (+36)** |

- **H1** (≥ +8 de 48 por modelo): **se cumple**, +28 y +36.
- **H2** (ninguna skill peor con skill): **se cumple**; la de delta más chico es
  `recurring-report-design` en Haiku, +6.
- **H3** (negativos con skill ≥ 7 de 8): **se cumple justo en Haiku (7 de 8)** y con 8 de 8
  en Sonnet. Sin skill, 8 de 8 en los dos.
- **Discriminación:** ninguna skill llega al 90% sin skill. La que más resuelve sola es
  `tests-over-changing-data-exports`, 4 de 12 (33%).

Es el delta más alto medido en el tap: +28 y +36 de 48, contra +19 y +25 de las skills de
v1.4.0 en la ronda C. Con una sola repetición y criterios del mismo autor, se lee como "estas
skills cambian mucho la respuesta", no como un ranking entre rondas.

## Qué se lee con cuidado

1. **El riesgo pre-registrado se dio.** Los dos criterios de `documentation-drift-audit`
   redactados como acciones ("corre el check mecánico…", "vuelve a correr el check al
   final") salieron en falso para los dos lados en Haiku: el evaluador anotó que los sujetos
   "no podían". En Sonnet, el primero contó porque la respuesta con skill lo describía como
   paso. La skill puede estar subcontada en hasta 2 criterios por modelo. No se reinterpretan
   las notas; lo que hace falta es reescribir esos criterios como recomendación ("propone
   correr…").
2. **El negativo que falló:** `recurring-report-design` en Haiku. A "¿qué márgenes usa A4 en
   milímetros?", la respuesta con skill agregó el contexto de la skill (márgenes medidos de
   10 mm). Es el costo que mide el negativo: una skill que invade una pregunta simple. Una
   observación con n = 1; si se repite, el disparador de esa skill está muy abierto.
3. **Límites ya declarados:** Sonnet evalúa a Sonnet, una repetición por condición, criterios
   escritos por quien escribió la skill.

## Qué sigue

- Reescribir los dos criterios de acción de `documentation-drift-audit`, igual que los de
  `grounded-citations` (ronda C), antes de volver a medir cualquiera de las dos.
- Activación de las 8 skills de v1.4.0 y v1.5.0 (`scripts/activation_eval.py`): estas rondas
  miden si la skill ayuda una vez cargada, no si se elige sola. Es la medición que falta para
  saber si un agente las va a usar.
