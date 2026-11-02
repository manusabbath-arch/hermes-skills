# Activación de las 15 skills, 2026-11-02 — las nuevas se eligen; H2 falla en Haiku

Tablas regeneradas por el CI: `results-haiku.md`, `results-sonnet.md`, `results-opus.md`.
Gasto: **0,15 USD** de un tope de 0,60 (3 llamadas; todas las respuestas completas). Con
esto, las mediciones aprobadas con un tope de 5 USD gastaron 3,99.

## Contra el pre-registro

| | Haiku | Sonnet | Opus | Pedido |
|---|---|---|---|---|
| **H1** las 8 nuevas, elegidas en sus positivos (de 32) | **28** | **28** | **30** | ≥ 26, ninguna < 2 de 4 |
| Mínimo por skill nueva (de 4) | 2 | 3 | 3 | ≥ 2 |
| **H2** las 7 viejas, elegidas en sus positivos (de 41) | **31 ✗** | **33** | **35** | ≥ 33 |
| **H3** no positivos con la lista vacía (de 25) | **25** | **25** | **25** | ≥ 21 |
| Falsos positivos (skill elegida en un pedido de otra) | 12 | 11 | 17 | se reporta |

- **H1 se cumple en los tres modelos.** Las 8 skills nuevas se eligen solas por su
  description. La más floja es `recurring-report-design` en Haiku, 2 de 4, justo en el
  mínimo.
- **H3 se cumple sin errores:** 25 de 25 en los tres modelos. Ningún negativo ni pedido
  ajeno al tap carga una skill, así que todos los falsos positivos están en pedidos positivos
  de otra skill.
- **H2 falla en Haiku** (31 de 41, mínimo 33) y pasa justo en Sonnet (33). En la v2, con 7
  skills, las mismas estaban entre 83% y 97%.

## Por qué falla H2: dos skills reclaman el mismo terreno

De los pedidos de skills viejas que no se eligieron, la mayoría se fue a una skill nueva, y
son **los mismos pedidos en los tres modelos**:

| Pedido (de la skill vieja) | Se eligió en su lugar |
|---|---|
| "programar las evals para que corran solas todas las noches" (`empirical-project-playbook`) | `unattended-run-verification` (3 de 3 modelos) |
| "tablero de salud: sin log de respaldo muestra verde" (`empirical-project-playbook`) | `unattended-run-verification` (3 de 3) |
| "un bug que ya documentamos dos veces volvió a aparecer" (`empirical-project-playbook`) | `designing-mechanical-guards` (3 de 3) |
| "120 chequeos, siempre 5 o 6 en rojo, el equipo los ignora" (`agent-ready-project`) | `designing-mechanical-guards` (2 de 3; Haiku eligió otra vieja) |
| "job nocturno que solo loguea si N > 0" (`empirical-system-invariants`) | `unattended-run-verification` (2 de 3) |

No es un error del modelo: esas elecciones son defendibles, porque la skill nueva cubre ese
tema. Lo que falta es el límite en las descriptions. Las de `delta-lakehouse` y
`data-medallion-architecture` ya dicen "Not for X: use Y", y entre ellas casi no se pisan.
Por modelo: Haiku perdió 5 pedidos de las viejas a favor de una nueva, Sonnet 7, Opus 4.

## Qué se lee con cuidado

- **El criterio era de una sola skill por pedido.** En los pedidos de arriba, cargar las dos
  probablemente sería lo mejor. La clave no lo admite, así que H2 mide desplazamiento,
  no daño.
- **Una corrida por modelo y una semilla;** los pedidos los escribió el autor de cada skill.
  Las descriptions de las 8 nuevas están en inglés y casi todos los pedidos en español.

## Qué sigue (no se hace en esta medición)

1. Agregar límites "Not for X: use Y" entre `designing-mechanical-guards` y
   `agent-ready-project` / `empirical-project-playbook`, y entre
   `unattended-run-verification` y `empirical-project-playbook` /
   `empirical-system-invariants`. Re-medir la activación con su propio pre-registro.
2. O bien decidir que esos pedidos esperan las dos skills y cambiar la clave para admitir
   un conjunto. Es una decisión de diseño de la prueba, y va antes de volver a correr, no
   después.
