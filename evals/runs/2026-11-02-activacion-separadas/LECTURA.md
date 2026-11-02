# Activación con las guardas separadas, 2026-11-02 — las tres hipótesis se cumplen

Tablas regeneradas por el CI: `results-haiku.md`, `results-sonnet.md`, `results-opus.md`.
Gasto: **0,15 USD** de un tope de 0,30. Las mediciones aprobadas con un tope de 5 USD
gastaron 4,59 en total.

## Contra el pre-registro

| | Haiku | Sonnet | Opus | Pedido |
|---|---|---|---|---|
| **H1** `designing-mechanical-guards` (de 8) | **8** | **8** | **8** | ≥ 6 |
| **H1** `agent-ready-project` (de 4) | **3** | **4** | **4** | ≥ 3 |
| **H2** las 7 viejas (de 37) | **32** | **36** | **34** | ≥ 30 |
| **H2** las 8 nuevas (de 36) | **32** | **34** | **34** | ≥ 29 |
| **H3** no positivos vacíos (de 25) | **24** | **25** | **25** | ≥ 21 |
| Total elegidas en sus positivos (de 73) | 64 | 70 | 68 | se reporta |

**Las tres hipótesis se cumplen en los tres modelos.** El total, que con las skills pisadas
era 59, 61 y 65 de 73 y con los límites 60, 63 y 64, ahora es **64, 70 y 68**.

## Qué cambió

- **`designing-mechanical-guards` se elige en todo lo suyo** (8 de 8 en los tres modelos),
  incluidos los 4 escenarios que recibió, y sus falsos positivos bajan a 1, 2 y 0.
- **`agent-ready-project` sigue eligiéndose en el arnés** (3, 4 y 4 de 4). Sus falsos
  positivos (3, 5 y 3) son de dos tipos:
  - en Sonnet, 4 de los 5 son pedidos de guardas donde cargó **las dos** skills, la correcta
    incluida: un costo de contexto, no un error de ruteo;
  - en Haiku y Opus, pedidos de otras skills donde eligió solo el arnés ("el CI falla en
    `doc_verify`" de `hermes-skills-tap-workflow`, "el feature ya está deployado" de
    `empirical-project-playbook`). Esos ya pasaban antes de separar.
- **Haiku cargó `agent-ready-project` en un negativo propio** ("¿qué hace `git worktree
  add`?"): es el único no positivo que no quedó vacío en los tres modelos.

## Qué se lee con cuidado

- **Mover escenarios a la skill que mejor los cubre sube su número por definición.** Por eso
  el pre-registro también exigía que `agent-ready-project` siguiera eligiéndose en lo suyo y
  que el resto del tap no cayera. Las dos cosas se cumplen.
- La clave cambió respecto de las dos activaciones anteriores (4 pedidos con otra skill
  esperada y otro orden), así que la comparación de totales es orientativa, no pedido a
  pedido.
- Una corrida por modelo; pedidos escritos por el autor de cada skill.

## Qué sigue

Nada urgente. Si se quiere bajar el costo de contexto, la description de
`agent-ready-project` podría decir explícitamente que no hace falta cargarla junto a
`designing-mechanical-guards` para un pedido sobre una guarda. Se mediría con su propio
pre-registro.
