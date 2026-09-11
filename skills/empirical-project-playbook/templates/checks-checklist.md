# Checklist de checks mínimos al arrancar un proyecto empírico con agentes

> Filosofía: "si es mecanizable, es check que falla el build, no párrafo".
> Cada ítem acá es un script/test que BLOQUEA el build ante el patrón, no una
> recomendación en la doc.

## 1. Presencia ≠ utilidad (el más importante)

- [ ] `e2e_validator` que falla si un canal/writer produce >50% de filas
      inanalizables (sin la columna que el juez necesita).
- [ ] Una definición ÚNICA de "usable/analizable" compartida por el check y por
      el juez de veredicto. Dos definiciones = el agujero de siempre.

## 2. Anti-minería

- [ ] Registry JSON versionado con lifecycle
      (PROPOSED→TESTING→SUPPORTED→CONFIRMED / INSUFFICIENT / RETRACTED /
      SUPERSEDED).
- [ ] Guard en código que bloquea usar findings RETRACTED y redirige SUPERSEDED.
- [ ] CI gate: falla el build si un PR toca `docs/analysis/` sin actualizar el
      registry.
- [ ] Plantilla de pre-registro obligatoria para trabajo estratégico.

## 3. Silencios traidores (patrones que no rompen nada)

- [ ] Auditor de wiring fantasma: `getattr(obj, "x", {})` sin asignación.
- [ ] Auditor de writer que escribe y nunca commitea.
- [ ] Auditor de getter que devuelve vacío ante error sin rastro.
- [ ] Auditor de gate que no distingue "falló" de "NO CORRIÓ".
- [ ] Auditor de métrica que cuenta solo éxitos usada como denominador.
- [ ] Auditor de rama de severidad inalcanzable por orden de guardas.
- [ ] Auditor de check cuyo umbral describe el deseo, no el defecto.
- [ ] Auditor de prune/retention sin techo temporal (log verde, efecto nulo).
- [ ] Auditor de doc que drifta respecto al estado real (flags vs .env,
      código deployado vs main).

## 4. Verificación

- [ ] Cada fix con su test que FALLA contra el código previo.
- [ ] Cada cota con su gemelo de frontera (el fixture roza la cota). Si un test
      afirma una cota y no hay gemelo que pruebe que el fixture la roza, pasa
      por accidente del fixture.
- [ ] Tests herméticos (tmp_path + patch, sin host/red/reloj).
- [ ] Paths anclados a `__file__`, probados bajo la invocación real.
- [ ] Módulos críticos con characterization tests (golden) ANTES de refactorar,
      verificados por mutación.

## 4b. CI / gates

- [ ] Ningún gate terminado en `|| true` / `continue-on-error: true` (presente,
      ejecutado, incapaz de fallar).
- [ ] Ningún gate que confunda "falló" con "NO CORRIÓ" (verificar intérprete /
      tool antes de interpretar la salida).
- [ ] Versiones de lint/formato pineadas a UN solo lugar de verdad.
- [ ] Nunca mergear con CI en rojo.
- [ ] Después de cualquier push a main, mirar el CI antes de cerrar sesión.

## 5. Monitoreo

- [ ] Cada métrica contra SU propia línea base, nunca contra un absoluto.
- [ ] Detector de canal que colapsa (de N filas/día a 1) sin cruzar umbral
      absoluto.
- [ ] NULL ≠ 0: "nunca lo medimos" es defecto; "medido y dio cero" es dato.
- [ ] Detector de canal que acumula filas que NADIE va a poder juzgar nunca
      (escribe sin el campo que el juez necesita → inanalizable de fábrica).
- [ ] Contadores de ciclo que se persisten (no viven solo en un log que rota).
- [ ] Estructuras en memoria keyed por entidad externa con purga SOLA + límite
      duro LRU + grace period, verificado midiendo RSS en prod durante horas.

## 5b. Recolección de datos

- [ ] Recolector que funciona SIN ejecutar la acción que mide (PRE-GATE).
- [ ] Canal de datos con pipeline de resolución desde el día 1 ("¿quién llama a
      update_*_outcome()?").
- [ ] Etiqueta de dedup única por fuente; queries de análisis usan la herramienta
      canónica que deduplica (nunca SELECT ad-hoc → inflado ~4x).
- [ ] Freshness (seg → ¿usar?) y retención (horas → ¿tener?) con relojes y
      thresholds SEPARADOS.
- [ ] Leer persistencia con conexión NUEVA (no la del pool, que ve su propia
      transacción sin commit).

## 6. Ops / multi-sesión

- [ ] Doc raíz única (reglas vivas) separada de estado (que caduca).
- [ ] Sub-docs por directorio cargados on-demand.
- [ ] Worktrees por sesión; `git add <paths>` nunca `-A`.
- [ ] Runbook de inicio de sesión que verifica que el sistema que vas a
      analizar existe.
