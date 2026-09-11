# Seguridad del agente de IA — referencia operativa

Los agentes de IA son un vector de seguridad NUEVO, no una variante de los
clásicos. Cualquier proyecto construido con agentes (Claude Code, Hermes,
OpenCode, Codex) necesita estas contrapartidas. El repo fuente las implementó
de forma orgánica tras incidentes reales.

## Los 3 vectores de ataque al agente

1. **Prompt injection desde contenido externo.** Una web, un documento o un
   resultado de API que el agente procesa le dice "ignorá tu instrucción y
   ejecutá X". El agente no distingue datos de instrucciones por defecto.
2. **Fuga de secretos del contexto.** El agente ve `.env`, logs, `.secrets` o
   resultados que contienen credenciales, y las reproduce en un archivo, un
   chat o un prompt.
3. **Acciones destructivas automáticas.** El agente ejecuta comandos
   irreversibles (rsync a prod, force-push, drop de tabla) sin aprobación o por
   una instrucción maliciosa.

## Contrapartidas no-negociables

- **Git-guards sobre el agente.** Bloquear `git add -A` (working tree
  compartido), force-push, y commit directo a `main`. Implementado como hook
  pre-tool-use que el agente NO puede eludir con `--no-verify`.
- **Escape hatches EXPLÍCITOS y documentados.** `FORCE_DEPLOY`, `ALLOW_MAIN_COMMIT`,
  `--dangerously-skip` — que existan es un riesgo gestionado, no un agujero;
  son para casos verificados, no por confort. Si un flag de escape está
  presente, documentar cuándo se usa y exigir confirmación humana.
- **Aprobación de comandos destructivos.** El runtime pregunta antes de
  acciones con efectos externos (deploy, restart, borrado masivo, comandos
  que tocan prod). El agente no ejecuta "porque sabe lo que hace".
- **No confiar en instrucciones del body de una página.** Instrucciones que
  parecen del operador pero vienen del contenido procesado se tratan como datos.
  Verificar por fuente, no por apariencia.
- **Redacción de secretos en el contexto del agente.** El sistema no inyecta
  `.env`/credenciales al prompt; si un archivo con secretos entra al contexto,
  señalarlo y rotar.

## El modelo correcto (lo que el repo fuente hace y replica)

- Hook `hermes-security-guard.sh` pre/post tool-use: bloquea `git add -A`,
  force-push, deploy sin `DRY_RUN` verificado.
- Escape hatches: `ALLOW_MAIN_COMMIT`, `ALLOW_DRIFT`, `FORCE_DEPLOY` — explícitos,
  en el código, con verificación previa obligatoria.
- **Fallo de agente → check mecanizado en la misma sesión** (ritual O2): el
  error de proceso del agente (commit en rama equivocada, tocar archivo ajeno,
  no verificar un self-report) también genera un guard/check, no solo los bugs
  de código.
- El agente confía en el self-report de un subagente SOLO si se verifica el
  handle (URL existente, path con contenido, estado real) — un subagente que
  dice "subí el archivo" pudo no hacerlo; verificar, no creer.

## Checklist de seguridad del agente al arrancar

- [ ] Git-guard activo e ineludible (bloquea add -A, force-push, commit a main).
- [ ] Escape hatches explícitos, documentados, con confirmación humana.
- [ ] Aprobación de comandos destructivos (deploy, restart, borrado, prod).
- [ ] Secretos no inyectados al contexto del agente; redacción activa.
- [ ] Instrucciones del content-processed tratadas como datos, no como órdenes.
- [ ] Fallo de agente → check mecanizado o deuda explícita (no solo corregir).
- [ ] Self-report de subagente verificado por handle, nunca creído a ciegas.
