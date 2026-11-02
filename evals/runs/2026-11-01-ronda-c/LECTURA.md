# Ronda C, 2026-11-01 — Haiku y Sonnet: las tres hipótesis se cumplen

Tablas regeneradas por el CI desde las notas crudas: `haiku/results.md` y `sonnet/results.md`.
Gasto: **1,30 USD** de un tope de 3,00 (28 sujetos y 14 evaluaciones, 42 llamadas, ningún
error, todas las notas legibles y completas). Con el benchmark de trampas, la fase 5 y esta
ronda gastaron 3,17 de los 5 USD aprobados.

## Contra el pre-registro

Criterios no negativos cumplidos, con skill / sin skill:

| | Haiku | Sonnet | Pedido |
|---|---|---|---|
| **H1** grupo 1, escenarios nuevos (de 17) | 10 / 2 (**+8**) | 14 / 6 (**+8**) | ≥ +3 |
| **H2** grupo 2, skills de v1.4.0 (de 48) | 27 / 8 (**+19**) | 37 / 12 (**+25**) | ≥ +8, ninguna skill con < sin |
| **H3** negativos con skill (de 14) | **14** | **14** | ≥ 12 |

- **H1, H2 y H3 se cumplen en los dos modelos.** Ninguna skill tiene menos criterios con skill
  que sin ella en ningún modelo.
- **Discriminación:** ninguna skill y modelo llega al 90% sin skill. La más cerca es
  `erp-business-analysis` en Sonnet: 4 de 6 sin skill (67%).
- **Negativos:** 14 de 14 con skill y 14 de 14 sin skill en los dos modelos. Hacen lo que
  tienen que hacer: muestran que la skill no infla una respuesta simple. No discriminan, ni
  se esperaba que lo hicieran.

## Qué se lee con cuidado

1. **`grounded-citations` no se puede medir con este protocolo.** Sus criterios piden correr
   `sources.py add/verify/render`, citar desde un ledger y hacer fan-out en la web, y los
   sujetos no tienen comandos ni web. 10 de sus 12 criterios no negativos no los puede
   cumplir nadie (las notas del evaluador lo dicen: "ninguno usa sources.py"). Sus cifras
   (Haiku 1/0, Sonnet 5/0 de 12) miden si la respuesta *describe* el procedimiento, no si
   lo ejecuta. Lo que hace falta: escenarios que se respondan en una conversación, o un
   protocolo con herramientas para esa skill. No se tocan en esta ronda.
2. **El grupo 1 puede estar inflado:** sus escenarios se escribieron después de la prosa de
   las skills (declarado en el pre-registro). +8 en los dos modelos es lo que dice esta
   medición, no una estimación limpia de lo que aportan los cambios de v1.5.0.
3. **`agent-ready-project` en Haiku: 1 de 5 con skill.** Es el delta más chico del grupo 1
   (+1). Con 5 criterios y una sola repetición es una observación, no un efecto.
4. **Las dos skills de guardas no se midieron en la misma versión en los dos modelos.**
   Durante la corrida se corrigieron los índices de relleno y las inserciones dentro de
   bloques de código de `designing-mechanical-guards` y `external-data-source-intake`
   (commit `d963deb`; sin cambios de prosa). Haiku corrió entero antes (hasta las 01:01:30,
   con las versiones de v1.4.0) y Sonnet entero después (desde las 01:01:54, con las
   corregidas). Cada modelo vio una sola versión de cada skill.
5. **Límites que ya estaban declarados:** Sonnet evalúa a Sonnet, una repetición por
   condición, criterios escritos por quien escribió la skill.

## Qué sigue

- Reescribir los escenarios de `grounded-citations` para que midan algo respondible sin
  herramientas, o medirla con herramientas, con su propio pre-registro.
- Activación de las 4 skills de v1.4.0 (`scripts/activation_eval.py`): esta ronda mide si la
  skill ayuda una vez cargada, no si se elige sola.
- Un revisor externo de los criterios sigue pendiente.
