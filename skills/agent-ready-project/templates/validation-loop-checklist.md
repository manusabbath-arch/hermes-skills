# Checklist: arnés de validación para un proyecto construido con agentes

Copiar, marcar, y dejar en el repo. Lo que no se marca queda como deuda contada,
no como olvido.

## 0. Guards destructivos (primero — evita el daño irreversible)

- [ ] `git add -A` / `git add .` bloqueado; paths explícitos siempre.
- [ ] Commit directo a la rama principal bloqueado.
- [ ] `force-push` bloqueado.
- [ ] Deploy sin confirmación / sin dry-run bloqueado.
- [ ] Borrado destructivo (`rm -rf`, `DROP`, `truncate`) fuera de temporales, bloqueado.
- [ ] **Cada guard cubre TODAS las superficies** que pueden ejecutar la acción:
      hook de git, plugin/hook del agente, y el camino manual de una persona.
- [ ] Cada guard tiene un **escape hatch nombrado y documentado**
      (`ALLOW_MAIN_COMMIT=1`, `FORCE_DEPLOY=1`), no un "comentá la línea".

## 1. Loop de validación

- [ ] **Pre-commit**: formato + lint + los checks propios del proyecto.
- [ ] **CI bloqueante** en el PR. Nunca mergear en rojo.
- [ ] **Suite completa** antes del push o en el PR.
- [ ] Ningún `|| true`, `continue-on-error`, `stages: [manual]` en un paso que
      dice verificar algo. **Un gate que no puede fallar no es un gate.**
- [ ] El CI **verifica que el intérprete/runner corrió** antes de interpretar su
      salida (un paso propio, ej. `pytest --version`).
- [ ] Versiones de las herramientas de lint pineadas en **un solo lugar**.
- [ ] Probado por mutación: romper algo a propósito pone el CI en rojo.
      Si nunca lo viste fallar, no sabés si funciona.

## 2. Deuda medida

- [ ] Se **midió** el total de hallazgos del linter antes de configurar ignores.
- [ ] Las familias que hoy dan **cero** están prendidas (atrapan bugs futuros gratis).
- [ ] Las familias con hallazgos se clasificaron **caso por caso**, no en bloque.
- [ ] Cada supresión que sobrevive lleva **el motivo al lado**. Visible, no aprobada.
- [ ] Lo que se ignora por deuda lleva **el número** al lado, para ver si crece.

## 3. Checks propios del proyecto

- [ ] Al menos un check del patrón de bug que más mordió a este proyecto.
- [ ] Si el codebase ya lo viola: **baseline con trinquete** (falla solo si crece).
- [ ] La baseline se indexa por **identidad estable** (archivo + símbolo), nunca
      por número de línea.
- [ ] El check reporta las entradas **stale** de la baseline (deuda ya pagada).
- [ ] Ritual activo: **cada fallo del agente se mecaniza en la misma sesión**, o
      queda como fila fechada en un registro de deuda.

## 4. Doc que no miente

- [ ] Bloques `<!-- verify -->` en los 3 números que más rápido envejecen.
- [ ] El verificador corre en pre-commit y en CI.
- [ ] Drift entre el default del código y la config real de producción, chequeado.
- [ ] El **SHA deployado** se compara contra la rama principal, no se asume.
- [ ] Al tocar la doc del agente: verificar que las rutas citadas existen y que
      los verificadores que la prosa declara siguen en CI (**reglas muertas**).

## 5. Doc raíz del agente

- [ ] Existe, está versionada en el repo, y es corta (~300 líneas).
- [ ] El detalle vive en reglas por directorio, lazy-load.
- [ ] Reglas "nunca X / siempre Y", con ejemplo, en orden de prioridad.
- [ ] Runbook de arranque: qué verificar antes de tocar producción.

## 6. Tests

- [ ] **Herméticos**: sin archivos reales del host, sin red, sin reloj.
- [ ] Paths anclados al archivo, nunca al cwd.
- [ ] Todo fix nuevo tiene un test que **falla contra el código previo**.
- [ ] Toda cota afirmada tiene un gemelo que prueba que el fixture la roza.
- [ ] **Characterization tests** antes del primer refactor de un módulo crítico,
      verificados por mutación.

## 7. Antes de cerrar cualquier sesión

- [ ] CI mirado después del push.
- [ ] Trabajo en rama pusheada (stash no es backup multi-sesión).
- [ ] Lo aprendido quedó como check, o como deuda fechada.
