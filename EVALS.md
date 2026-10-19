# Evaluaciones de las skills

Una skill que nadie midió es una afirmación. Este archivo dice qué se midió, cómo y qué
no prueba. Los datos crudos (cada respuesta, cada nota del evaluador, la clave de qué
respuesta tenía la skill y la foto de los criterios usados) están en `evals/runs/`, y el
CI regenera todas las tablas desde esos datos: si una tabla publicada no coincide, el
build falla.

## Contents

1. Método
2. Resultado actual (v2, tres modelos)
3. Activación: ¿se elige la skill sola?
4. Ronda B: lo que se cambió por la v2 y si funcionó
5. Qué NO prueba esto
6. Historia: v1
7. Cómo repetirla

## 1. Método

- **Escenarios:** cada skill trae `evals/evals.json` con 5 pedidos: 2 base, 2 difíciles
  (con una trampa que la respuesta genérica no ve) y 1 **negativo**, una pregunta simple
  donde la skill no debería cambiar nada. Son 35 pedidos y 105 criterios.
- **Sujetos:** por skill y por modelo (Haiku, Sonnet, Opus), un agente lee la skill y otro
  no lee nada; los dos responden los mismos pedidos, sin comandos ni web.
- **Evaluador ciego:** un agente distinto por skill y modelo recibe los criterios y las
  respuestas A y B; qué letra tuvo la skill se sorteó y vive en `key.json`, que no lee.
- **Activación:** un agente ve solo el `name` y la `description` de las 7 skills y 49
  pedidos barajados (los 35 de las evals + 7 ajenos al tap), y elige qué skills cargaría.
- **Tablas:** `scripts/eval_report.py` y `scripts/activation_eval.py`; un criterio o un
  pedido sin calificar es rojo.

## 2. Resultado actual (v2, tres modelos)

Criterios cumplidos con y sin skill (`evals/runs/2026-10-18-v2/<modelo>/results.md`):

| Skill | Haiku con / sin | Sonnet con / sin | Opus con / sin |
|---|---|---|---|
| `agent-ready-project` | 16 / 7 | 16 / 7 | 17 / 10 |
| `data-medallion-architecture` | 14 / 9 | 14 / 12 | 15 / 10 |
| `delta-lakehouse` | 11 / 11 | 15 / 10 | 15 / 10 |
| `empirical-project-playbook` | 13 / 9 | 12 / 8 | 12 / 7 |
| `empirical-system-invariants` | 10 / 7 | 11 / 6 | 12 / 6 |
| `erp-business-analysis` | 12 / 5 | 16 / 6 | 16 / 7 |
| `hermes-skills-tap-workflow` | 12 / 6 | 13 / 8 | 13 / 9 |
| **Total (de 105)** | **88 / 54** | **97 / 57** | **100 / 59** |

Lo que dice: las skills agregan entre +34 y +41 criterios en los tres modelos, y **la v2
ya discrimina** (ninguna skill queda al 100% en todos los modelos). La que más aporta es
`erp-business-analysis` (+7 a +10). La más débil es `delta-lakehouse` en Haiku (+0).

## 3. Activación: ¿se elige la skill sola?

| | Haiku | Sonnet | Opus |
|---|---|---|---|
| Elegida en sus 35 pedidos (ronda B) | 31 | 34 | 32 |
| Falsos positivos en pedidos negativos y ajenos | 0 | 0 | 0 |

**Ninguna skill se activó en un pedido que no era suyo del dominio**: ni en las preguntas
simples ni en los 7 pedidos ajenos al tap. Todos los errores son **confusiones entre
skills hermanas** (medallion ↔ delta, playbook ↔ invariants ↔ agent-ready). Un caso es
genuinamente ambiguo: "un bug que ya documentamos dos veces volvió a aparecer" está en el
playbook, pero `agent-ready-project` también lo cubre y los tres modelos eligieron esa.
No se reasignó el escenario después de ver el resultado: hacerlo sería minería.

## 4. Ronda B: lo que se cambió por la v2 y si funcionó

La v2 mostró que **con la skill cargada, las preguntas simples se contaminaban**: el agente
respondía y además agregaba el dominio de la skill ("además, en Bronze…", "cuidado con las
filas de total…"). Negativos con skill: Haiku 8/14, Sonnet y Opus 12/14 (sin skill 13-14).

**Cambio:** cada skill suma "Cuándo NO aplicarla", y las descriptions de las hermanas
declaran su límite. **Pre-registro escrito antes de medir:**
`evals/runs/2026-10-18-v2/PRE-REGISTRO-ronda-b.md`.

| Métrica | Ronda A | Ronda B | Criterio | Veredicto |
|---|---|---|---|---|
| Negativos con skill (Haiku) | 8/14 | 12/14 | ≥ 12 | éxito |
| Positivos con skill (Haiku) | 80/91 | 76/91 | ≥ 77 | **fracaso (por 1)** |
| Activación, aciertos (3 modelos) | 94/105 | 97/105 | ≥ 94 | éxito |
| Activación, FP en negativos y ajenos | 0 | 0 | 0 | éxito |

**Desvío declarado del pre-registro.** El pre-registro decía que, si fracasaba, se
revertían las descriptions. No se aplicó, por dos motivos que quedan escritos acá para
que se puedan discutir:

1. **La acción estaba mal especificada.** Las descriptions solo influyen en la
   activación, que mejoró; si algo bajó los positivos, fue la sección "Cuándo NO
   aplicarla", que la acción no tocaba.
2. **El fracaso está dentro del ruido medido del evaluador.** Las respuestas sin skill de
   Haiku son *idénticas* en las dos rondas (verificado byte a byte) y el evaluador les dio
   54 y 55: ±1 punto con las mismas respuestas. El fracaso es por 1 punto.

Lo que corresponde, y queda **pendiente como ronda C**: 3 repeticiones de Haiku con skill
para tener un rango en lugar de un punto, con un criterio de reversión que apunte a la
sección de alcance si los positivos quedan por debajo de 77 en el promedio.

## 5. Qué NO prueba esto

- **Los criterios los escribió el mismo autor de las skills.** Algunos nombran artefactos
  propios; el evaluador acepta equivalentes, pero favorece a la condición con skill.
- **Una corrida por condición** en la v2, y el evaluador tiene ruido de al menos ±1
  punto (sección 4). Diferencias de 1-2 criterios en una skill son ruido.
- **Mide la respuesta, no el trabajo:** los sujetos describen lo que harían; no se
  ejecutó el resultado en un repo real.
- **Mismo idioma y mismo autor de pedidos:** todos en español rioplatense, escritos por
  quien escribió las skills.

## 6. Historia: v1

Corrida inicial con 3 pedidos por skill, solo Sonnet (`evals/runs/2026-10-18/`): 53/58
con skill contra 20/58 sin skill. Encontró tres huecos reales (medallion sin ingesta por
tipo de fuente y con un "sentinel 0.0" que contradecía su propia regla NULL ≠ 0; erp sin
"retractar y propagar"; tap-workflow sin "name = directorio"). Corregidos: 58/58 contra
20/58. Llegó al techo, y por eso se hizo la v2.

## 7. Cómo repetirla

1. Por skill y modelo, un sujeto con la skill y otro sin ella responden los pedidos de
   `evals/evals.json` en `<skill>.A.md` / `<skill>.B.md`, con la letra sorteada en `key.json`.
2. Un evaluador ciego por skill y modelo escribe `grades/<skill>.json`
   (`[{"pedido", "criterio", "A", "B", "nota"}]`).
3. Copiar los `evals.json` usados a `<run>/evals/<skill>.json` (la foto) y correr
   `python3 scripts/eval_report.py --grades <dir>/grades --key <dir>/key.json --evals <run>/evals > <dir>/results.md`.
4. Activación: `python3 scripts/activation_eval.py build --out <dir> --seed <n>`, darle
   `prompt.md` a un agente por modelo y `... score --key <dir>/key.json --answers <respuesta>`.
5. Pre-registrar lo que se espera **antes** de correr una ronda que mide un cambio.
6. Agregar la corrida a `evals/runs/` y sus tablas al CI.
