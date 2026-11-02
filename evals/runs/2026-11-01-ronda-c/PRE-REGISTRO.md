# Ronda C — pre-registro (01/11/26, commiteado antes de correr)

## Qué se mide

Dos grupos que todavía no tienen tabla:

| Grupo | Skills | Escenarios | Criterios (no negativos + negativos) |
|---|---|---|---|
| 1. Escenarios nuevos de v1.5.0 | `erp-business-analysis`, `agent-ready-project`, `empirical-project-playbook` | los pedidos 7, 8 y 9 de cada `evals.json` (3 por skill, 1 negativo) | 17 + 6 = 23 |
| 2. Skills de v1.4.0 | `designing-mechanical-guards`, `unattended-run-verification`, `external-data-source-intake`, `grounded-citations` | los 5 de cada una (1 negativo) | 48 + 8 = 56 |

Los escenarios del grupo 1 se escribieron **después** de la prosa de las skills, contra la
regla del tap (`CHANGELOG.md`, v1.5.0). Por eso esta ronda puede sobrestimar lo que aportan:
se declara acá y se lee así.

## Cómo

- `python3 evals/ronda.py --out evals/runs/2026-11-01-ronda-c --tope-usd 3 --modelos haiku,sonnet --semilla 20261101 --skills erp-business-analysis:7,8,9,agent-ready-project:7,8,9,empirical-project-playbook:7,8,9,designing-mechanical-guards,unattended-run-verification,external-data-source-intake,grounded-citations`
- Sujetos Haiku y Sonnet, con la skill (copia de su carpeta, sin `evals/` ni `tests/`) y sin
  nada; Read/Glob/Grep sobre su carpeta, sin comandos ni web. Una llamada por skill y condición.
- Evaluador ciego Sonnet, uno por skill y modelo, sin la clave. Notas ilegibles o
  incompletas = rojo, no se completan a mano.
- Tabla: `scripts/eval_report.py`, la misma de las rondas anteriores, y el CI la regenera.
- **Tope: 3,00 USD** para toda la ronda (28 sujetos + 14 evaluaciones). Con lo ya gastado
  en el benchmark (1,87 USD), queda dentro de los 5 USD aprobados para la fase 5 y esta
  ronda.

## Criterios, fijados antes de ver nada

- **H1 (grupo 1):** con − sin ≥ **+3** de los 17 criterios no negativos, en cada modelo.
- **H2 (grupo 2):** con − sin ≥ **+8** de los 48 criterios no negativos, en cada modelo, y
  ninguna de las 4 skills con menos criterios con skill que sin ella en algún modelo.
- **H3 (negativos, los 7):** con skill cumple ≥ **12 de 14** criterios negativos en cada
  modelo: la skill no infla una respuesta simple.
- **Discriminación:** una skill y modelo donde sin skill ya cumple ≥ 90% de sus criterios
  no discrimina ahí, y se reporta así (como el benchmark de trampas).

Referencia, no criterio: en la v2 (18/10/26) las 7 skills agregaron entre +34 y +41 de 105
criterios (alrededor de un tercio). H1 y H2 piden menos (un sexto) a propósito.

## Lo que no se hace después de ver la tabla

- No se editan skills, escenarios ni criterios dentro de esta ronda para que mejore.
- No se corre otra vez para elegir la mejor de dos.
- Si una hipótesis falla, se escribe que falló y por qué parece haber fallado.

## Límites declarados

- Sonnet evalúa respuestas de Sonnet; una sola repetición por condición.
- Los criterios los escribió quien escribió la skill; no hay revisor externo todavía.
- El sujeto con skill sabe que tiene una skill (el prompt lo dice); el sin skill no.

## Enmienda (01/11/26, antes de cualquier llamada)

El primer intento se cayó al crear la carpeta de trabajo `con` (nombre reservado en Windows),
antes de llamar a ningún modelo: 0 USD, 0 respuestas. Se renombró a `con-skill`/`sin-skill`,
con su test, y se corre igual que lo de arriba. Nada más cambia.
