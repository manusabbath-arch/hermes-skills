# Casos de origen — agent-ready-project

Las reglas de la skill se escriben en neutro; acá están los proyectos de donde
salen y los incidentes completos, para quien quiera la evidencia o juzgar si un
caso se parece al suyo.

## Los proyectos fuente

- **Bot de trading en mercados de predicción (2026).** ~500 commits escritos por
  agentes (Claude Code, Hermes, OpenCode, Codex) sobre un sistema que operaba con
  dinero real. Fuente del loop de validación, la baseline con trinquete, la doc que
  verifica sus números, la deuda de lint medida y los modos de falla del código de
  agente.
- **Análisis de negocio de una distribuidora (2026).** Un repo de análisis sobre un
  ERP legado, con seis agentes (Claude Code, Hermes, OpenCode, Qwen Code, Kimi Code,
  Antigravity) escribiendo el mismo árbol en Windows. Fuente del verde vacío, varios
  agentes en un repo, planes que declaran cómo fallan, las guardas por consumidor y
  los scripts `prod_write_guard.py`, `worktree_guard.py` y `phantom_wiring.py`.

## Incidentes del bot de trading

- **Wiring fantasma, seis veces.** `getattr(obj, "attr", default)` con un atributo
  que ninguna clase asignaba. El patrón se documentó después de cada aparición y
  recurrió igual; la peor dejó el trailing-stop sin activarse nunca en producción.
  Dejó de recurrir con el script que falla el build.
- **Gates de seguridad que no podían fallar.** `bandit` y `pip-audit` con `|| true`
  durante meses, sobre las librerías que firmaban órdenes.
- **Drift de config.** `MAX_POSITIONS` en 6 por defecto en el código y 2 en el `.env`
  de producción: bloqueaba todas las operaciones.
- **Deploy que no era.** Una sesión editó el `.env` por SSH y reportó "deploy
  completo"; producción corría 265 commits atrás.
- **Lint barrido.** `F841` apagado en la config mientras se perseguía el wiring
  fantasma con scripts a medida; de 53 casos de `B905`, 4 eran defectos reales.
- **Query que tumbó producción.** Una consulta ad-hoc al 97% de CPU durante 1h21m.
- **Diagnóstico con 2 muestras.** Se concluyó "timeout de red"; con 351 muestras, el
  95% era tamaño de frame.

## Incidentes del análisis de la distribuidora

- **Nueve verdes vacíos**, tres críticos, uno con una cifra que ya había salido a los
  vendedores. Un nombre de check mal escrito salía en verde con código 0.
- **El sellado que se comía la línea base:** un `--seal` filtrado dejó 1 entrada de 23.
- **Guarda de datos personales que miraba `*.csv`** y dejó pasar un `.json` con 31
  titulares y direcciones.
- **Hook de solo-lectura con `sed`:** cortaba `command` en la última comilla del
  JSON; con el payload de Hermes (campos después de `command`) una escritura al ERP
  pasaba sin bloquear.
- **Worktree en HEAD detached** creado por la herramienta: commits que no quedaban en
  ninguna rama, días enteros sin que nada lo notara.
- **Commit sin pathspec** que arrastró 29 borrados preparados por otra sesión.
- **Planes sin spec:** con la sección pedida en prosa, 1 de 29 planes la tenía; las
  decisiones, que tenían check, 42 de 42.
- **Backlog con 9 ítems "pendientes"** que otras sesiones ya habían cerrado.
- **Edición por heredoc** que metió un byte NUL en un `.py`.
