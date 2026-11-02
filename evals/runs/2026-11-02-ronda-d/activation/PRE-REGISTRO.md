# Activación de las 15 skills — pre-registro (02/11/26, commiteado antes de correr)

## Qué se mide

Si el agente elige la skill correcta viendo solo su `name` y su `description`, ahora con
las 15 skills instaladas juntas. Es la primera medición de activación de las 8 skills de
v1.4.0 y v1.5.0, y además mide si su llegada les quita pedidos a las 7 de v1.3.0.

98 pedidos barajados (`scripts/activation_eval.py build --seed 20261102`): 73 positivos
(32 de las 8 skills nuevas, 41 de las 7 viejas), 18 negativos de los `evals.json` y 7
ajenos al tap.

## Cómo

- `python3 evals/activacion.py --out evals/runs/2026-11-02-ronda-d/activation --tope-usd 0.6 --modelos haiku,sonnet,opus --semilla 20261102`
- Un sujeto por modelo recibe `prompt.md` en una carpeta vacía y devuelve el JSON de
  elecciones; `activation_eval.py score` arma la tabla, y el CI la regenera. Una respuesta
  incompleta es rojo y no se completa a mano.
- **Tope: 0,60 USD** (3 llamadas). Con lo gastado (3,84 USD) queda dentro de los 5 USD
  aprobados.

## Criterios, fijados antes de ver nada

- **H1 (las 8 nuevas):** elegidas en ≥ **26 de sus 32** positivos por modelo, y ninguna en
  menos de 2 de sus 4.
- **H2 (no desplazan a las viejas):** las 7 de v1.3.0 elegidas en ≥ **33 de sus 41**
  positivos por modelo (80%; en la v2 y la ronda B estuvieron entre 83% y 97% con 7 skills).
- **H3 (precisión):** de los 25 pedidos no positivos (negativos + ajenos), ≥ **21** con la
  lista vacía, por modelo.
- Los falsos positivos por skill se reportan siempre, se cumpla o no lo de arriba.

## Lo que no se hace después de ver la tabla

No se editan descriptions ni escenarios dentro de esta medición; no se corre otra semilla
para elegir; una hipótesis que falla se escribe como falló.

## Límites declarados

Una corrida por modelo y una semilla; los pedidos positivos son los de las evals, escritos
por quien escribió cada skill (pueden usar su vocabulario); las descriptions de las 8 skills
nuevas están en inglés y casi todos los pedidos en español.
