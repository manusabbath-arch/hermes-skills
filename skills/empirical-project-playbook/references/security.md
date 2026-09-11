# Seguridad — referencia operativa

Detalle de las reglas de seguridad del playbook (plano clásico). La seguridad
del agente de IA tiene su propia referencia (`agent-security.md`).

## Supply chain (la más urgente)

- **Lockfiles pineados exacto** (toda dependencia con versión exacta, no `>=`).
  El repo fuente declaraba 31 dependencias con `>=` y solo pineaba `web3`,
  `eth-account` — las que firman órdenes.
- **SCA (Software Composition Analysis):** pip-audit / dependabot / renovate que
  BLOQUEEN el merge ante una CVE, no que solo avisen.
- **SAST:** bandit / semgrep con reglas reales (no por defecto vacías).
- **El gate de seguridad debe poder fallar.** La lección del fuente: `bandit` y
  `pip-audit` corrieron meses con `|| true` / `continue-on-error` — presentes,
  ejecutados, incapaces de fallar, mientras la prosa de CI se leía como
  cobertura real. Un step "gate" que no puede fallar no es seguridad.
  Verificador: `tests/test_ci_security_gates_block.py` evalúa líneas ejecutables
  (no matchea texto plano del comentario que cita el `|| true` viejo).

## Ciclo de vida de secretos

- **Menor privilegio:** cada proceso/agente con la credencial mínima para lo
  suyo. No compartir una clave maestra entre servicios.
- **Rotación periódica**, no solo "si se filtra". Revocación probada (saber que
  el revoke funciona antes de necesitarlo).
- **Nunca secretos en logs ni en el contexto del agente.** Redacción activa.
- **File system:** permisos estrictos (chmod 400 para privadas), fuera de git,
  fuera del deploy (solo SSH manual). El `.env` de config no son secretos;
  los secretos van aparte.
- **L2 / credenciales derivadas:** claves de API derivadas al arranque en vez de
  almacenadas — una credencial que no se guarda no se puede filtrar por disco.

## Protección de la clave de firma (wallet)

La clave que firma órdenes es el activo más sensible del sistema:

- No materializarla en un proceso que no la necesita.
- Protegerla de dump del proceso (`/proc`, core dumps, logs de excepción).
- Procedimiento si un agente la llega a ver en logs/contexto: rotar de
  inmediato, no "confiar en que no la usó".

## Menor privilegio operativo

- Proceso no-root cuando sea viable; capacidades mínimas sobre privilegio total.
- Tokens de agentes/CI que NO equivalgan a root de producción. El balance con
  simplicidad operativa es real — registrar la decisión y el riesgo, no dejarla
  implícita.

## Respuesta a incidentes de seguridad

- **Contener antes que parchear:** bloquear/revocar la credencial comprometida
  es lo primero; el hot-patch del código viene después.
- Forense mínimo: qué comandos ejecutó el agente/servicio, en qué ventana, con
  qué credencial.
- Registro de quién pudo hacer qué (audit de acciones, no solo de accesos).
- Post-incidente: se mecaniza la firma (guard/check/tests) o se registra deuda
  explícita — nunca solo "arreglar y seguir".

## Checklist de seguridad mínimo al arrancar un proyecto

- [ ] Lockfiles pineados exacto; SCA bloquea el merge ante CVE.
- [ ] SAST con reglas reales; ningún gate de seguridad con `|| true`.
- [ ] Secretos con menor privilegio, rotación, revocación probada; jamás en
      logs/contexto.
- [ ] Clave de firma no materializada donde no se necesita.
- [ ] Firewall con superficie mínima; health sin datos sensibles.
- [ ] Headers `deprecation`/`sunset` verificados en APIs dependidas.
