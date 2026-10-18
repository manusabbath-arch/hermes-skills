# Pre-registro — ronda B (escrito antes de correrla)

**Cambio a medir:** cada skill suma una sección "Cuándo NO aplicarla" (pregunta puntual →
responder solo eso) y las descriptions de las skills hermanas declaran su límite.
Los escenarios de `evals/` NO cambian (cambiarlos después de ver resultados sería minería).

**Qué se re-corre:** Haiku con skill (7 sujetos + 7 evaluadores ciegos, contra las mismas
respuestas sin skill de la ronda A) y la prueba de activación en los tres modelos.

**Criterios fijados antes de medir:**

| Métrica | Ronda A | Éxito si | Fracaso si |
|---|---|---|---|
| Negativos con skill, Haiku | 8/14 | ≥ 12/14 | ≤ 9/14 |
| Criterios positivos con skill, Haiku (sin negativos) | 80/91 | no baja más de 3 (≥ 77/91) | < 77/91 (el freno costó contenido) |
| Activación, aciertos (suma 3 modelos) | 94/105 | ≥ 94/105 | < 90/105 |
| Activación, falsos positivos en negativos y ajenos | 0 | 0 | > 0 |

Si fracasa, se revierte el cambio de descriptions y se deja solo la sección de alcance.
