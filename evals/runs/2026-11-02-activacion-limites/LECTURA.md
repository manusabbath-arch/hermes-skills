# Activación con límites, 2026-11-02 — H1, H2 y H3 se cumplen; un límite funcionó y el otro no

Tablas regeneradas por el CI: `results-haiku.md`, `results-sonnet.md`, `results-opus.md`.
Gasto: **0,15 USD** de un tope de 0,30. La clave es idéntica a la de la activación anterior
(misma semilla): lo único que cambió son las 5 descriptions. Las mediciones aprobadas con un
tope de 5 USD gastaron 4,44.

## Antes y después (misma clave)

| | Haiku | Sonnet | Opus | Pedido |
|---|---|---|---|---|
| **H2** las 7 viejas (de 41) | 31 → **33** | 33 → **36** | 35 → **34** | ≥ 33 en los tres |
| **H1** las 8 nuevas (de 32) | 28 → **27** | 28 → **27** | 30 → **30** | ≥ 26, ninguna < 2 |
| Mínimo por skill nueva (de 4) | 2 → 2 | 3 → 3 | 3 → 3 | |
| **H3** no positivos vacíos (de 25) | 25 → **25** | 25 → **25** | 25 → **25** | ≥ 21 |
| Falsos positivos | 12 → 14 | 11 → 12 | 17 → 10 | se reporta |

**Las tres hipótesis se cumplen en los tres modelos.**

## Pedido por pedido

| Pedido que se desplazaba | Haiku | Sonnet | Opus |
|---|---|---|---|
| "programar las evals todas las noches" (`empirical-project-playbook`) | recuperado | recuperado | recuperado |
| "tablero de salud: sin log muestra verde" (`empirical-project-playbook`) | recuperado | recuperado | recuperado |
| "job que solo loguea si N > 0" (`empirical-system-invariants`) | recuperado | recuperado | ya estaba |
| "un bug documentado dos veces volvió" (`empirical-project-playbook`) | sigue en guardas | pasa a `agent-ready-project` | sigue en guardas |
| "120 chequeos, 5 o 6 rojos que se ignoran" (`agent-ready-project`) | suma guardas a otra vieja | sigue en guardas | sigue en guardas |

- **El límite de `unattended-run-verification` funcionó:** recuperó sus 3 pedidos en los
  tres modelos, y sus falsos positivos bajaron de 4, 4 y 3 a 1, 1 y 1. Ayudó también que la
  description de `empirical-project-playbook` ahora dice que cubre operar el entorno.
- **El límite de `designing-mechanical-guards` no funcionó:** sus dos pedidos desplazados
  siguen en esa skill en la mayoría de los modelos, y además le costó uno propio. "El gate
  está rojo en tres chequeos viejos que no son míos" (un pedido de
  `designing-mechanical-guards`) ahora se va a `agent-ready-project` en Haiku y Sonnet, por la
  frase "adopting a baseline over many existing checks". En Haiku la skill queda justo en el
  mínimo (2 de 4).

Leído así: entre `designing-mechanical-guards` y `agent-ready-project` el terreno se pisa en
serio (línea base, rojos declarados, "que no vuelva a pasar"). Una frase en la description
no alcanza para separarlo.

## Qué se lee con cuidado

- **Los límites se escribieron después de ver qué pedidos se desplazaban, y se midieron con
  la misma semilla.** Eso aísla el efecto del cambio, pero puede premiar límites hechos a
  medida. Una semilla nueva diría si generalizan.
- Una corrida por modelo. Las diferencias de 1 o 2 pedidos (Opus 35 → 34 en las viejas) son
  del orden del ruido.

## Qué sigue

Para las guardas, la decisión es de diseño, no de redacción: o `agent-ready-project` deja la
línea base y los rojos declarados en manos de `designing-mechanical-guards` y su body apunta
ahí, o se acepta que esos pedidos esperan las dos skills (la opción B, para este par). No se
hace en esta medición.
