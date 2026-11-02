# Inventario: perfil Hermes vs tap

Medido el 2026-10-31 (ola 1) y recontado el 2026-11-01 (ola 2) sobre
`%LOCALAPPDATA%\hermes\skills` y `<clon>\skills` (este
repo). El tap publicaba 7 skills antes de ola 1 y 11 antes de ola 2.

## Cómo se leyó

Un `SKILL.md` por carpeta, recorriendo el perfil y saltando `.hub` / `.locks`.
El conteo de líneas es el de `Measure-Object -Line` (no vacías). Las 7 del tap
ya viven en este repo; el perfil las tiene además como copias o como skills
hermanas con otro nombre.

## Ola 1 (esta rama): destilar al tap

Elegidas porque caben (o se recortan) bajo el tope de 500 líneas del validador,
no copian skills propias del repo de cliente, y sirven al primer proyecto de dogfood
(`rastro-publico`: cron, fuentes públicas, citas).

| Skill | Origen en el perfil | Líneas origen | Qué se hizo |
|---|---|---|---|
| `designing-mechanical-guards` | `software-development/` | 1101 | Procedimiento en `SKILL.md` (≤500). Catálogo de pitfalls en `references/pitfalls.md`. 22 refs copiadas. |
| `unattended-run-verification` | raíz del perfil | 199 | Neutralizada (sin carpeta de planificador ni skill de cliente). Cabe entera. |
| `external-data-source-intake` | `productivity/` | 336 | Copiada con 3 refs. Description ampliada. Cifras de forma, no de negocio. |
| `grounded-citations` | `research/` | 208 | Copiada con ledger `scripts/sources.py` (stdlib; sin import de `hermes_constants`). |

## Ola 2 (esta rama): destilar al tap

Elegidas porque caben bajo 500 líneas, no copian skills propias del repo de cliente, y el dogfood de rastro
las usa (tests de fixtures, ntfy apagado por defecto). `documentation-drift-audit`
entra al tap; el dogfood no duplica el candado README↔`TAREAS` de rastro.

| Skill | Origen en el perfil | Líneas origen | Qué se hizo |
|---|---|---|---|
| `tests-over-changing-data-exports` | `software-development/` | 138 | Neutralizada (sin patente ni flag de cliente). Cabe entera. |
| `outbound-notification-channels` | `software-development/` | 223 | Neutralizada. Se dejó afuera `scripts/guardar-secreto-desde-archivo.py` (`import keyring`, el AST del validador lo cobra también en `try/except`). |
| `recurring-report-design` | `productivity/` | 331 | Copiada con 3 refs. Related skills del tap, no las que esperan. |
| `documentation-drift-audit` | `productivity/` | 350 | Copiada con 2 refs y `check_docs_integrity.py`. Punto de entrada `README.md`. |

## Siguiente ola (espera)

No entran en esta rama. Motivo al lado.

| Skill | Origen | Líneas | Por qué espera |
|---|---|---|---|
| `production-database-queries` | `productivity/` | 1039 | Pasa las 500 líneas; hay que partirla. Toca SQL vivo / ERP. |
| `legacy-office-data-extraction` | `productivity/` | 1130 | Misma talla. El tap ya cubre exports de ERP vía `erp-business-analysis`. |
| `multi-agent-shared-workspace` | `autonomous-ai-agents/` | 970 | Solapa con `agent-ready-project` (worktrees). Recortar contra esa skill primero. |
| `controlling-hand-keyed-data` | `productivity/` | 354 | Útil, no es el camino de rastro (fuentes públicas, no planillas a mano). |
| `fleet-telemetry` | `productivity/` | — | Caso GPS; `external-data-source-intake` ya cubre el método. |
| `printable-field-forms` | `productivity/` | — | Papel de campo; rastro no lo necesita. |
| `uydatos-y-mcp-uruguay` | perfil | — | Rutas absolutas, pines que envejecen, citas de cliente. |

El resto del perfil (Apple, creative, social-media, CLIs de agente, Notion, Office)
es de otro producto o ya tiene skill oficial. No se destila acá.

## Qué no se copia nunca a este tap

- Skills propias del repo de cliente (apuntan al vault, no se publican).
- Cifras de negocio, razones sociales, rutas de planificador de un cliente.
- `production-database-queries` sin partir y sin pasar el escáner de montos /
  `.private-terms`.
