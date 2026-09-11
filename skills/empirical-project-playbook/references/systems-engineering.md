# Ingeniería de sistemas — referencia operativa

Detalle de las reglas de sistemas del playbook. Cargar on-demand (como el repo
hace con los sub-CLAUDE.md por directorio), NO en cada sesión.

## Diseño para falla / blast radius

Cada componente debe aislarse para que una explosión no tumbe el loop principal:

- Subsistemas en su propio proceso/contador cuando una falla pueda cascadear.
- Degradación graceful: degradar a shadow/modo lectura antes que morir. Un
  componente que muere con todo es peor que uno que degrada a recolección sin
  capital.
- Circuit breaker por dependencia externa: si la API externa falla N veces
  seguidas, cortar y degradar en vez de reintentar en bucle contra un
  endpoint caído. (El repo fuente tiene `circuit_breaker.py`, `async_retry.py`.)

## Release engineering

- **Feature flag con kill switch por feature.** Cada feature nuevo arranca
  default OFF; el flag es el kill switch de emergencia. Documentar el flag en
  la tabla de canales desde el commit que lo introduce, no después.
- **Rollback = revertir un SHA deployado**, nunca "editar el .env y esperar".
  Un `.env` editado a mano puede reportarse "deploy completo" mientras el
  código corre 265 commits atrás.
- **Escape hatches EXPLÍCITOS y documentados** (`FORCE_DEPLOY`, `ALLOW_*`) que
  solo se activan tras verificación, no por confort.
- **Canary / staged rollout** para configs nuevas, no solo para código.

## SLOs y error budgets

- Para cada señal (uptime, latencia, frescura, throughput) definir un objetivo
  medible y un "error budget": cuánto desvío tolerás antes de intervenir, sin
  fatiga de alertas.
- Comparar cada métrica contra SU propia línea base (nunca absoluto), y contra
  el SLO, no contra un deseo.
- Un check cuyo umbral describe la configuración deseada en vez de un defecto
  → FAIL permanente → fatiga → nadie mira más. Es la lección central del repo
  (guards_ok=0 con book lleno era estado conocido, quedó como FAIL eterno).

## Disaster recovery que se TESTEA

- **Un backup que no se restaura periódicamente en un entorno limpio no es un
  backup, es un deseo.**
- Backup con checksum que efectivamente valide: la lección del repo — el script
  guardaba el sha256 del `.db` y dos líneas abajo `gzip` lo borraba, así que
  `sha256sum -c` daba FAILED para los 15 backups "presentes". Un backup sin
  checksum es deuda; un checksum que no valida es peor.
- Restauración probada: correr el restore completo en un entorno de prueba al
  menos periódicamente, no solo verificar que el archivo existe.
- Corrupción SQLite: `PRAGMA integrity_check(100000)` (el default corta a 100
  errores y parece acotado). No reparar in-place con DROP/ALTER sobre el archivo
  vivo — reconstruir en archivo nuevo, validar con conexión nueva antes del
  `mv` atómico.
- Migraciones atómicas y verificables; probar la DB en cada deploy.

## Capacidad / recursos / costos

- Alertar por capacidad (disco, RAM, inodes, conexiones), no solo por "canal
  silencioso". El incidente del disco al 88% (orderbook_snapshots 1.57GB, 45%
  de la DB) comenzó como un problema de retención, no de alertas de canal.
- Estructuras en memoria keyed por entidad externa: purga que corra SOLA
  (loop propio), límite duro LRU + grace period, y medir RSS en PROD durante
  horas — un test unitario de la lógica no prueba que el proceso real no siga
  creciendo (la brecha entre ambas FUE el bug, ~35MB/hora).
- Costo / cuota finita: alertar antes de agotarse, no después. (El fuente tiene
  un watchdog de presupuesto API que alerta ≥ umbral antes del exhaust.)
- Costo in-cycle vs CLI: una función de análisis manual y la misma llamada
  in-cycle NO comparten el default caro (un bootstrap de 5000 réplicas bloquea
  el loop 348s). Señal: los ciclos más lentos caen en múltiplos exactos
  (200, 400, 600…) = un `_EVERY_N_CYCLES` caro.

## Concurrencia y estado compartido

- Estado mutable de instancia cruzando un `await` bajo concurrencia = race
  condition. Buscar `self.` mutable en el camino de código concurrente.
- Idempotencia: un retry no debe duplicar efecto. Retry con backoff exponencial
  + jitter. Dead-letter de operaciones que fallan definitivamente.
- Timeout explícito por operación, verificado contra el tiempo real disponible
  (bajo límite de ciclo).

## Superficie de red

- Firewall que exponga solo lo necesario.
- Health endpoint sin datos sensibles; paneles admin detrás de auth.
- Verificar headers `deprecation`/`sunset`/`warning` en APIs dependidas — una API
  externa deprecada que "funciona" pero devuelve datos cacheados se descubre por
  los headers, no por el bug propio.
