# Evaluaciones de las skills

Una skill que nadie midió es una afirmación. Este archivo dice qué se midió, cómo y
qué no prueba. Los datos crudos (cada respuesta, cada nota del evaluador y la clave
de qué respuesta tenía la skill) están en `evals/runs/`, y el CI regenera las tablas
desde esos datos: si la tabla publicada no coincide, el build falla.

## Método (corrida del 2026-10-18)

1. **Escenarios:** cada skill trae `evals/evals.json` con 3 pedidos reales y los
   comportamientos esperados, en el formato de la guía de autoría de Anthropic. Son 21
   pedidos y 58 criterios en total.
2. **Sujetos:** por skill, dos agentes Sonnet responden los mismos 3 pedidos. Uno lee la
   skill antes de responder; el otro no lee ningún archivo. Ninguno corre comandos ni
   busca en la web. Sonnet y no un modelo mayor, porque una skill tiene que servirle
   también a un modelo menos capaz.
3. **Evaluador ciego:** por skill, un agente distinto recibe los criterios y las dos
   respuestas etiquetadas A y B. Qué letra tuvo la skill se sorteó por skill y vive en
   `key.json`, que el evaluador no lee. Califica cada criterio como cumplido o no, con
   una frase de motivo, sin premiar la longitud.
4. **Tabla:** `scripts/eval_report.py` cruza las notas con la clave. Un criterio sin
   calificar es rojo.

## Resultados

**Ronda 1** (`evals/runs/2026-10-18/round1/`):

| Skill | Con skill | Sin skill | Delta |
|---|---|---|---|
| `agent-ready-project` | 10/10 | 2/10 | +8 |
| `data-medallion-architecture` | 5/8 | 4/8 | +1 |
| `delta-lakehouse` | 9/9 | 5/9 | +4 |
| `empirical-project-playbook` | 7/7 | 2/7 | +5 |
| `empirical-system-invariants` | 7/7 | 3/7 | +4 |
| `erp-business-analysis` | 9/10 | 2/10 | +7 |
| `hermes-skills-tap-workflow` | 6/7 | 2/7 | +4 |
| **Total** | **53/58** | **20/58** | **+33** |

**Lo que la ronda 1 encontró en las skills, y se corrigió:**

- `data-medallion-architecture` casi no cambiaba la respuesta (+1). No daba una ingesta
  concreta por tipo de fuente: ahora trae una tabla API/DB/SFTP. Bronze no mencionaba
  time-travel, y Gold no se verificaba (presence ≠ utility). Y la prosa de Silver decía
  "malo → sentinel 0.0", contra la regla NULL ≠ 0 de la misma skill. Ese error se había
  copiado al código de ejemplo.
- `erp-business-analysis` no decía "retractar y propagar" justo en el caso de atribuirle
  un desvío al ERP.
- `hermes-skills-tap-workflow` no decía que `name` tiene que coincidir con el directorio.

**Ronda 2**: se repitió la condición con skill de esas tres, contra las mismas respuestas
sin skill de la ronda 1 (`evals/runs/2026-10-18/round2/`):

| Skill | Con skill | Sin skill | Delta |
|---|---|---|---|
| `agent-ready-project` | 10/10 | 2/10 | +8 |
| `data-medallion-architecture` | 8/8 | 4/8 | +4 |
| `delta-lakehouse` | 9/9 | 5/9 | +4 |
| `empirical-project-playbook` | 7/7 | 2/7 | +5 |
| `empirical-system-invariants` | 7/7 | 3/7 | +4 |
| `erp-business-analysis` | 10/10 | 2/10 | +8 |
| `hermes-skills-tap-workflow` | 7/7 | 2/7 | +5 |
| **Total** | **58/58** | **20/58** | **+38** |

## Qué NO prueba esto

- **Los criterios los escribió el mismo autor de las skills.** Algunos nombran
  artefactos propios (un script, una plantilla), lo que favorece a la condición con
  skill aunque el evaluador acepte equivalentes.
- **Una corrida por condición**, sin repeticiones: no hay intervalo de confianza. Una
  diferencia de 1–2 criterios en una skill es ruido.
- **Techo:** con 58/58 los escenarios ya no discriminan. La próxima ronda necesita
  pedidos más difíciles y casos negativos (pedidos donde la skill NO debería dispararse).
- **Mide la respuesta, no el trabajo:** los sujetos describen lo que harían; no se
  ejecutó el resultado en un repo real.
- **La activación no se midió:** a la condición con skill se le dio la skill. Si el
  agente la elige por su `description` entre muchas es otra pregunta.
- **Un solo modelo sujeto (Sonnet).** La guía de Anthropic pide probar con cada modelo
  que se piensa usar.

## Cómo repetirla

1. Por skill, un agente sujeto con la skill y otro sin ella responden los pedidos de
   `evals/evals.json` y escriben `<skill>.A.md` / `<skill>.B.md`, con la letra sorteada.
2. Un evaluador ciego por skill escribe `grades/<skill>.json` con
   `[{"pedido", "criterio", "A", "B", "nota"}]`.
3. `python3 scripts/eval_report.py --grades <dir>/grades --key <dir>/key.json > <dir>/results.md`
4. Agregar la corrida nueva a `evals/runs/` y al CI.
