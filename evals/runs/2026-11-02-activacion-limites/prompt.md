Tenés instaladas estas skills. De cada una solo ves su nombre y su descripción:

- `agent-ready-project`: Use when setting up or hardening a project that AI agents will build and modify - any codebase, not just data or trading. Covers the non-eludible validation loop (pre-commit, CI, pre-push), turning a check on over a dirty codebase with a ratchet baseline, docs that verify their own numbers, measuring lint debt instead of sweeping it, guards on every surface that can run the action, and the failure modes specific to agent-written code: invented API signatures, unverified self-reports, phantom wiring, silent-green tasks. Also covers empty-green checks that approve over zero items, plans that declare how they fail, and several agents sharing one repo: worktree per session, detached HEAD, concurrent commits, per-agent guard coverage, and long-running work across sessions (feature list, progress file, separate evaluator). For writing one specific guard (failing test first, wiring, no-regression proof), use designing-mechanical-guards.
- `data-medallion-architecture`: Use when designing an end-to-end data architecture: choosing a source (API, database, SFTP), building a medallion bronze-silver-gold lakehouse pipeline, and turning it into hypothetical-scenario dashboards and AI/ML/MCP consumption. Covers source-selection tradeoffs, ingest per source type (API, DB, SFTP), idempotent re-deliveries, deduplication and NULL handling in Silver, and layer design patterns. Not for operating an existing Delta table (vacuum, optimize, time travel): use delta-lakehouse.
- `delta-lakehouse`: Use when building an ETL or data pipeline, or storing structured and unstructured data in a Delta lakehouse for ML training or AI agent consumption. Covers extraction from heterogeneous sources, Delta tables with operation history and time travel, upsert patterns, partitioning, vacuum and compaction, retention, reading Delta offline, using deltalake + duckdb + pyarrow. Not for designing bronze/silver/gold layers or per-source ingest: use data-medallion-architecture.
- `designing-mechanical-guards`: Use when a rule keeps breaking and should become a check the machine runs - mechanical guards, pre-commit gates, vacuous greens, guard perimeters, ratchet baselines, declared reds, advisory-to-enforcement, and make-sure-this-never-happens-again. Covers writing the failing test first, wiring into the existing gate, proving no regression on a mature gate that already carries known reds, and the measured failure shapes of checks that look green while covering nothing. Not for setting up a project's whole validation loop or adopting a baseline over many existing checks (use agent-ready-project), nor for judging whether a measured result holds (use empirical-project-playbook).
- `documentation-drift-audit`: Use when auditing docs against the system they describe: stale facts, stale advice, broken wikilinks, orphans from the entry point, and a mechanical integrity check that must print its denominator before a clean result counts.
- `empirical-project-playbook`: Use when starting, building, or auditing an empirical/data-driven project with AI agents - anything that measures something (edge, conversion, performance, a business hypothesis) and decides with data. Covers pre-registration and kill criteria, anti-mining defenses, presence-vs-utility acceptance, shadow-mode rollout, mechanized build-failing checks, the 'treacherous silence' bug family, verification standards, and security/systems rules. Also for a metric or dashboard number that looks impossible (a negative success rate, a denominator that counts the wrong set) and for small-sample A/B results. Also for operating the agents' environment: model or eval spend with a declared cap that is never scheduled on its own, and health panels where missing data reads STALE, never green. For whether a scheduled job actually ran, use unattended-run-verification; for turning one rule into a check, use designing-mechanical-guards.
- `empirical-system-invariants`: Use when a system must prove, every cycle, that it measures what it claims - auditing a data pipeline for phantom wiring, silent empty getters, or unpopulated fields. Provides per-cycle data contracts, a RED-light rule naming the exact broken link, NULL-not-zero semantics, and a project-agnostic guard script that fails the build. Not for judging an experiment or a business metric (use empirical-project-playbook) nor for CI checks on code (use agent-ready-project). Also for silence that reads as success, such as a job that only logs its count when it is non-zero.
- `erp-business-analysis`: Use when analyzing a real business from its ERP or accounting system with AI agents - sales, margin, stock rotation, debt/collections, supplier scorecards, ABC classification - working from spreadsheet exports (.xls/.xlsx/.csv) or a read-only production database. Covers the eight ways an analysis publishes a wrong but plausible number, provenance seals, canary cross-checks against an independent source, NULL-vs-stored-zero fields, multiple legal entities in one ERP, declared period and export hour, currency and DECIMAL pitfalls, retractions that propagate, owner-declared premises, third-party data that must not be versioned, and decision notes with owner and review trigger.
- `external-data-source-intake`: Use when a non-ERP data source lands for analysis - GPS, telemetry, fleet traces, CKAN or open-data catalogs, supplier portals, river levels, fuel prices, weather APIs - and its numbers will be crossed with project masters or published. Covers reader shrinkage, threshold sweeps, interval overlap, stacked series, SOAP encoded arrays, and declaring what the source does not carry.
- `grounded-citations`: Use when grounding answers and documents in cited, verifiable sources: inline numbered citations, a ledger that maps url to [n] from retrieval not memory, Perplexity-style Sources blocks, fact-checking with verbatim quotes, and verify --evidence. Covers chat answers, markdown, PDF, docx, slides, and multi-platform sweeps.
- `hermes-skills-tap-workflow`: Use when authoring, publishing, or propagating Hermes or Claude Code skills through a GitHub tap repo - editing a skill at its canonical source, installing it into profiles, keeping installed copies from drifting, and avoiding known install pitfalls.
- `outbound-notification-channels`: Use when adding an outbound channel (email, chat, webhook, ntfy) so a report or alert leaves the machine without attaching it by hand: secrets in the OS store, off by default, injected transport, and delivery is not the same as generating the artifact.
- `recurring-report-design`: Use when designing a recurring daily or weekly report people actually read: every item names its consumer and denominator, rotation instead of accumulation, work-assignment blocks with a capped dose, and the heartbeat whose absence is the alarm.
- `tests-over-changing-data-exports`: Use when tests read live exports that get re-downloaded: fixtures versus the newest file, structural assertions instead of vintage totals, skip-with-motivo that leaves the suite green, and a cache that must not hide a file that changed mid-run.
- `unattended-run-verification`: Use when verifying an unattended run, a scheduled task, a cron job, or a Windows Task Scheduler job: whether it actually fires alone, whether a log that says done proves the artifact exists, print spooler versus exit 0, orphaned headless processes, listeners that look alive, and health items that measure the wrong leg of the job. Not for deciding whether model or eval spend may be scheduled, nor for what a health panel shows when data is missing (use empirical-project-playbook), nor for a pipeline that must prove every cycle what it measured (use empirical-system-invariants).

Para cada pedido de abajo, decidí qué skills cargarías antes de responderlo. Cargá una
skill solo si de verdad cambia cómo responderías; si el pedido se responde bien sin
ninguna, la lista va vacía. No respondas los pedidos: solo decidí.

1. El README dice 8 checks y el registry tiene 16. Dejá 16 y borramos el README viejo.
2. `hermes skills install` falló con 'Could not fetch from any source', ¿cómo instalo igual la skill del tap?
3. Sumé el export 'Ventas por vendedor y marca 2026' y me da exactamente el doble que el informe de Estadística del ERP.
4. Escribime un mail para pedirle a un cliente que confirme la reunión del martes.
5. Te paso el export GPS de la flota. Calculame cuántos clientes nunca visitamos a 100 m.
6. El log dice Enviado y el PDF se generó. ¿Llegó el mail?
7. Nuestro check `validar` imprime '0 problemas' y sale con 0. Un agente renombró el directorio que escanea y nadie lo notó en semanas. ¿Qué cambiamos?
8. Nuestro dashboard muestra 'success rate: -5046%'. ¿Qué puede estar pasando?
9. Leé la wiki y actualizala. Hay varios números viejos.
10. Pegá el token en config/telegram.txt así el bot arranca hoy.
11. ¿Cuánto es el 15% de 2.400?
12. Hay un TODO que dice «correr OCR sobre los PDFs escaneados». Dejalo, es trabajo pendiente.
13. El catálogo CKAN me devolvió count 0 para clima. Entonces no hay datos de clima.
14. En el servidor sin internet, duckdb falla con 'Failed to download extension delta'. ¿Qué hago?
15. Armame un CSS para centrar un div vertical y horizontalmente.
16. ¿Cómo marco un test de pytest para que se saltee en Windows?
17. El total de deuda que sacamos del export no coincide con lo que muestra el ERP; parece que el ERP está desactualizado.
18. Resumime en tres líneas qué es la fotosíntesis.
19. Traducí al inglés: 'el pedido sale mañana a primera hora'.
20. La deuda de un cliente difiere $290.000 entre el export de la mañana y el de la tarde. ¿Hay una partición entre las dos razones sociales?
21. Dejo la PC prendida esta noche. ¿El job de las 07:10 se va a ejecutar y va a dejar el archivo?
22. Edité una skill en el repo tap pero en mi perfil de Hermes sigue la versión vieja.
23. El proveedor reenvió por SFTP el mismo CSV dos veces y el total de Gold se duplicó. ¿Cómo lo arreglamos?
24. El Sources del draft no coincide con los [n] del texto. Arreglalo a mano.
25. Agregué una skill nueva y el CI falla en el paso de doc_verify con 'skills-count'. ¿Por qué?
26. Las lecturas de mi tabla Delta se pusieron lentas después de meses de upserts diarios.
27. Quiero programar las evals de nuestros agentes para que corran solas todas las noches con Claude y nos llegue el resultado.
28. La lista de 278 ítems no se ejecuta. Imprimila completa así se ve el atraso.
29. The new check is green on the live repo. Ship it.
30. This rule keeps breaking: every report must declare its source hash. Make sure it never happens again.
31. El PDF apareció en la carpeta tres minutos después de que la corrida declaró fallo por timeout.
32. Encontré en los datos que la estrategia gana cuando el precio está entre 0.30 y 0.42. ¿La activo en producción?
33. Quiero prender un check de lint nuevo pero el repo ya tiene 180 violaciones y no puedo arreglarlas todas hoy.
34. ¿Cómo se escribe un wikilink de Obsidian a una nota en otra carpeta?
35. El test de ventas se rompió: ahora da 1.176 filas y ayer daba 130. Alguien bajó otro período. Arreglá el test para que vuelva a pasar.
36. ¿Cuál es la capital de Australia?
37. Quiero que un agente consulte las tablas del lakehouse para responder preguntas de negocio.
38. ¿Puedo limpiar y deduplicar directamente al ingestar, así me ahorro la capa Bronze?
39. Nuestro job nocturno loguea 'procesados N' solo cuando N > 0. Anoche no logueó nada. ¿Está bien?
40. ¿Qué está diciendo la gente de esto en Reddit, RSS y YouTube?
41. Puse un caché de lecturas y la suite bajó de 251 s a 88 s. ¿Lo prendemos para toda la sesión?
42. La corrida de las 17:55 salió a las 19:56. Poné 17:55 en el encabezado, que es la hora nominal.
43. Investigá el estado actual de Sentinel-2 NDCI y armame un informe con fuentes.
44. Un bug que ya documentamos dos veces en el README volvió a aparecer.
45. Esto es médico: confirmá cada cifra con evidencia verbatim.
46. Corrí vacuum con retención 0 para ahorrar espacio y ahora no puedo reproducir el dataset de entrenamiento de hace un mes.
47. Nuestra compuerta tiene 120 chequeos y siempre hay 5 o 6 en rojo por datos que faltan; el equipo ya ignora el rojo. ¿Bajamos esos chequeos a warning?
48. ¿Qué flag usa crontab para listar las tareas del usuario actual?
49. El feature nuevo ya está deployado y no tira errores. ¿Lo cerramos?
50. El campo `margen` tiene 0 en las 4.548 filas de la tabla. ¿Es un dato o falta cargarlo?
51. ¿Qué diferencia hay entre CSV y Parquet?
52. Agregá un try/except alrededor del check de invariantes para que no rompa el ciclo si falla.
53. ¿Cómo creo un repo nuevo en GitHub?
54. Armamos un tablero de salud del entorno y si no hay log de respaldo de ayer muestra verde porque no hay errores. ¿Está bien?
55. ¿Qué receta puedo hacer con arroz, huevo y cebolla?
56. Te paso el export 'Ventas 2026 YTD.csv' del ERP; calculame la rotación de stock por producto y compará contra 2025.
57. Nuestro pipeline corre todos los días sin errores pero sospechamos que algunos campos nunca se llenan. ¿Cómo lo verificamos?
58. ¿Cómo se escribe en SQL un LEFT JOIN entre dos tablas?
59. El check de links dio 0 rotos y 0 huérfanos. ¿Está todo bien?
60. Un subagente me reportó 'PR creado y tests en verde'. ¿Lo doy por terminado?
61. El A/B dio +12% de conversión con 40 usuarios por brazo. ¿Lo escalamos a todos?
62. ¿Qué es un p-valor?
63. El worker de Telegram está corriendo y el chequeo de proceso está en verde, pero nadie contesta.
64. ¿Cómo agrego una columna a una tabla en Postgres?
65. La hoja Parciales tiene más filas que Viajes. Usemos esa como input del ruteo.
66. Tres agentes (Claude Code, Hermes y OpenCode) van a trabajar a la vez en este repo. ¿Cómo lo organizamos para no pisarnos?
67. Nuestro CI corre `pytest | grep passed || exit 1` y bandit con `|| true`. Revisalo y dejalo listo para que lo modifiquen agentes.
68. Tenemos ventas en una API REST, el maestro de clientes en Postgres y un CSV diario por SFTP. Diseñá la arquitectura de datos para un dashboard de escenarios.
69. Un campo de precio a veces viene 'n/d'. ¿Lo pongo en 0 en Silver para que no rompan los promedios?
70. Armame el código para pasar un CSV de ventas por Bronze, Silver y Gold usando el stack que recomienda la skill.
71. La suite me dio 300 fallos en archivos que no toqué, todos con 'no existe' y código 127. ¿Revierto mi último commit?
72. ¿Cuál es la sintaxis de un f-string en Python 3.12?
73. Puse la skill en `skills/MiSkill/` con `name: mi-skill` y no aparece al instalar. ¿Qué pasa?
74. SumatraPDF salió exit 0, el log dice Impreso. ¿Está el papel?
75. El guard de invariantes tira ROJO todos los días por un campo que vale 0 legítimamente.
76. ¿Cuál es el subject máximo razonable de un mail?
77. Sumé Tiempo Detención de todos los vehículos y da más de mil horas en un mes. ¿Están parados todo el día?
78. ¿Cómo configuro una regla de reenvío en Gmail?
79. Corrí una consulta en DB2 que arma cada fila como NOMBRE || ';' || RUC || ';' || TELEFONO. La salida dice '20 record(s) selected.' pero cuento 16 líneas. ¿Se cortó el archivo?
80. Quiero que el informe diario se mande por Telegram. Armame el bot y dejalo prendido.
81. The gate is red on three old checks that are not mine. I need to commit a one-line fix.
82. El parte de las 7:30 está quedando corto. Sumale una hoja más con todo lo que vimos esta semana.
83. This check is noisy. I'll add || true so it still runs but does not block.
84. ¿Cómo abro un CSV con pandas?
85. Hoy no hubo excepciones. ¿Mandamos el reporte igual o lo salteamos para no molestar?
86. Quiero publicar una skill nueva en el tap. ¿Qué pasos sigo?
87. ¿Qué fórmula de Excel uso para sumar una columna?
88. How do I rename this function in Python?
89. Falta el export de hoy. El test se saltea y la suite queda verde. ¿Puedo pushear?
90. ¿Cómo renombro una variable local en una función de Python?
91. Hice LEFT JOIN entre las líneas de venta y la tabla de productos de la base del ERP por PRODUCTOID contra el código del export, y ningún producto tiene proveedor. ¿El maestro de productos está vacío?
92. Necesito guardar PDFs de facturas y la tabla de ventas en un lakehouse para entrenar un modelo después.
93. ¿Cómo leo un CSV con pandas?
94. Hacé que pytest lea siempre el xlsx más nuevo de la carpeta de descargas.
95. ¿Qué márgenes usa A4 en milímetros?
96. Necesito el margen por producto de 2025; pedile al cliente el export que haga falta.
97. ¿Qué hace git worktree add?
98. Corrí --enviar para verificar el canal antes del primer cron. El archivo de enable ya estaba.

Respondé SOLO con un objeto JSON {"1": ["nombre-de-skill"], "2": [], ...} con una
entrada por pedido, usando los nombres exactos de las skills.
