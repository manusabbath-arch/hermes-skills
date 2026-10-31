# Inventario: perfil Hermes vs tap

Medido el 2026-10-31 sobre `%LOCALAPPDATA%\hermes\skills` (98 `SKILL.md`) y
`C:\Users\Usuario\hermes-skills\skills` (este repo). El tap publicaba 7 skills
antes de esta ola.

## Cómo se leyó

Un `SKILL.md` por carpeta, recorriendo el perfil y saltando `.hub` / `.locks`.
El conteo de líneas es el de `Measure-Object -Line` (no vacías). Las 7 del tap
ya viven en este repo; el perfil las tiene además como copias o como skills
hermanas con otro nombre.

## Ola 1 (esta rama): destilar al tap

Elegidas porque caben (o se recortan) bajo el tope de 500 líneas del validador,
no copian skills `ng-*` de cliente, y sirven al primer proyecto de dogfood
(`rastro-publico`: cron, fuentes públicas, citas).

| Skill | Origen en el perfil | Líneas origen | Qué se hizo |
|---|---|---|---|
| `designing-mechanical-guards` | `software-development/` | 1101 | Procedimiento en `SKILL.md` (≤500). Catálogo de pitfalls en `references/pitfalls.md`. 22 refs copiadas. |
| `unattended-run-verification` | raíz del perfil | 199 | Neutralizada (sin carpeta de planificador ni skill de cliente). Cabe entera. |
| `external-data-source-intake` | `productivity/` | 336 | Copiada con 3 refs. Description ampliada. Cifras de forma, no de negocio. |
| `grounded-citations` | `research/` | 208 | Copiada con ledger `scripts/sources.py` (stdlib; sin import de `hermes_constants`). |

## Ola 2 (espera)

No entran en esta rama. Motivo al lado.

| Skill | Origen | Líneas | Por qué espera |
|---|---|---|---|
| `production-database-queries` | `productivity/` | 1039 | Pasa las 500 líneas; hay que partirla. Toca SQL vivo / ERP. Dogfood de rastro no la necesita. |
| `legacy-office-data-extraction` | `productivity/` | 1130 | Misma talla. El tap ya cubre exports de ERP vía `erp-business-analysis`. |
| `multi-agent-shared-workspace` | `autonomous-ai-agents/` | 970 | Solapa con `agent-ready-project` (worktrees). Recortar contra esa skill primero. |
| `controlling-hand-keyed-data` | `productivity/` | 354 | Útil, no es el camino de rastro (fuentes públicas, no planillas a mano). |
| `documentation-drift-audit` | `productivity/` | 350 | Rastro ya traba README↔`TAREAS` con un test. No duplicar. |
| `recurring-report-design` | `productivity/` | 331 | Candidata natural para un boletín; después de que ola 1 se use de verdad. |

El resto del perfil (Apple, creative, social-media, CLIs de agente, Notion, Office)
es de otro producto o ya tiene skill oficial. No se destila acá.

## Qué no se copia nunca a este tap

- Skills `ng-*` del repo de cliente (apuntan al vault, no se publican).
- Cifras de negocio, razones sociales, rutas de planificador de un cliente.
- `production-database-queries` sin partir y sin pasar el escáner de montos /
  `.private-terms`.
