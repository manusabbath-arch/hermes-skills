Tenés instaladas estas skills. De cada una solo ves su nombre y su descripción:

- `agent-ready-project`: Use when setting up or hardening a project that AI agents will build and modify - any codebase, not just data or trading. Covers the non-eludible validation loop (pre-commit, CI, pre-push), turning a check on over a dirty codebase with a ratchet baseline, docs that verify their own numbers, measuring lint debt instead of sweeping it, guards on every surface that can run the action, and the failure modes specific to agent-written code: invented API signatures, unverified self-reports, phantom wiring, silent-green tasks. Also covers empty-green checks that approve over zero items, plans that declare how they fail, and several agents sharing one repo: worktree per session, detached HEAD, concurrent commits, per-agent guard coverage, and long-running work across sessions (feature list, progress file, separate evaluator).
- `data-medallion-architecture`: Use when designing an end-to-end data architecture: choosing a source (API, database, SFTP), building a medallion bronze-silver-gold lakehouse pipeline, and turning it into hypothetical-scenario dashboards and AI/ML/MCP consumption. Covers source-selection tradeoffs and layer design patterns.
- `delta-lakehouse`: Use when building an ETL or data pipeline, or storing structured and unstructured data in a Delta lakehouse for ML training or AI agent consumption. Covers extraction from heterogeneous sources, Delta tables with operation history and time travel, upsert patterns, partitioning, vacuum and compaction, using deltalake + duckdb + pyarrow.
- `empirical-project-playbook`: Use when starting, building, or auditing an empirical/data-driven project with AI agents - anything that measures something (edge, conversion, performance, a business hypothesis) and decides with data. Covers pre-registration and kill criteria, anti-mining defenses, presence-vs-utility acceptance, shadow-mode rollout, mechanized build-failing checks, the 'treacherous silence' bug family, verification standards, and security/systems rules.
- `empirical-system-invariants`: Use when a system must prove, every cycle, that it measures what it claims - auditing a data pipeline for phantom wiring, silent empty getters, or unpopulated fields. Provides per-cycle data contracts, a RED-light rule naming the exact broken link, NULL-not-zero semantics, and a project-agnostic guard script that fails the build.
- `erp-business-analysis`: Use when analyzing a real business from its ERP or accounting system with AI agents - sales, margin, stock rotation, debt/collections, supplier scorecards, ABC classification - working from spreadsheet exports (.xls/.xlsx/.csv) or a read-only production database. Covers the eight ways an analysis publishes a wrong but plausible number, provenance seals, canary cross-checks against an independent source, NULL-vs-stored-zero fields, multiple legal entities in one ERP, declared period and export hour, currency and DECIMAL pitfalls, retractions that propagate, owner-declared premises, third-party data that must not be versioned, and decision notes with owner and review trigger.
- `hermes-skills-tap-workflow`: Use when authoring, publishing, or propagating Hermes or Claude Code skills through a GitHub tap repo - editing a skill at its canonical source, installing it into profiles, keeping installed copies from drifting, and avoiding known install pitfalls.

Para cada pedido de abajo, decidí qué skills cargarías antes de responderlo. Cargá una
skill solo si de verdad cambia cómo responderías; si el pedido se responde bien sin
ninguna, la lista va vacía. No respondas los pedidos: solo decidí.

1. El proveedor reenvió por SFTP el mismo CSV dos veces y el total de Gold se duplicó. ¿Cómo lo arreglamos?
2. Te paso el export 'Ventas 2026 YTD.csv' del ERP; calculame la rotación de stock por producto y compará contra 2025.
3. ¿Cómo renombro una variable local en una función de Python?
4. Resumime en tres líneas qué es la fotosíntesis.
5. ¿Qué es un p-valor?
6. Nuestro job nocturno loguea 'procesados N' solo cuando N > 0. Anoche no logueó nada. ¿Está bien?
7. Un campo de precio a veces viene 'n/d'. ¿Lo pongo en 0 en Silver para que no rompan los promedios?
8. ¿Cómo configuro una regla de reenvío en Gmail?
9. Nuestro dashboard muestra 'success rate: -5046%'. ¿Qué puede estar pasando?
10. ¿Qué fórmula de Excel uso para sumar una columna?
11. Nuestro pipeline corre todos los días sin errores pero sospechamos que algunos campos nunca se llenan. ¿Cómo lo verificamos?
12. ¿Cómo creo un repo nuevo en GitHub?
13. Armame el código para pasar un CSV de ventas por Bronze, Silver y Gold usando el stack que recomienda la skill.
14. Quiero prender un check de lint nuevo pero el repo ya tiene 180 violaciones y no puedo arreglarlas todas hoy.
15. Las lecturas de mi tabla Delta se pusieron lentas después de meses de upserts diarios.
16. Nuestro CI corre `pytest | grep passed || exit 1` y bandit con `|| true`. Revisalo y dejalo listo para que lo modifiquen agentes.
17. El total de deuda que sacamos del export no coincide con lo que muestra el ERP; parece que el ERP está desactualizado.
18. Agregá un try/except alrededor del check de invariantes para que no rompa el ciclo si falla.
19. Armame un CSS para centrar un div vertical y horizontalmente.
20. Quiero publicar una skill nueva en el tap. ¿Qué pasos sigo?
21. `hermes skills install` falló con 'Could not fetch from any source', ¿cómo instalo igual la skill del tap?
22. Tenemos ventas en una API REST, el maestro de clientes en Postgres y un CSV diario por SFTP. Diseñá la arquitectura de datos para un dashboard de escenarios.
23. El feature nuevo ya está deployado y no tira errores. ¿Lo cerramos?
24. Escribime un mail para pedirle a un cliente que confirme la reunión del martes.
25. Encontré en los datos que la estrategia gana cuando el precio está entre 0.30 y 0.42. ¿La activo en producción?
26. Tres agentes (Claude Code, Hermes y OpenCode) van a trabajar a la vez en este repo. ¿Cómo lo organizamos para no pisarnos?
27. Sumé el export 'Ventas por vendedor y marca 2026' y me da exactamente el doble que el informe de Estadística del ERP.
28. Un bug que ya documentamos dos veces en el README volvió a aparecer.
29. ¿Qué receta puedo hacer con arroz, huevo y cebolla?
30. El guard de invariantes tira ROJO todos los días por un campo que vale 0 legítimamente.
31. El campo `margen` tiene 0 en las 4.548 filas de la tabla. ¿Es un dato o falta cargarlo?
32. Corrí vacuum con retención 0 para ahorrar espacio y ahora no puedo reproducir el dataset de entrenamiento de hace un mes.
33. Puse la skill en `skills/MiSkill/` con `name: mi-skill` y no aparece al instalar. ¿Qué pasa?
34. Traducí al inglés: 'el pedido sale mañana a primera hora'.
35. ¿Cuál es la capital de Australia?
36. ¿Qué diferencia hay entre CSV y Parquet?
37. Edité una skill en el repo tap pero en mi perfil de Hermes sigue la versión vieja.
38. En el servidor sin internet, duckdb falla con 'Failed to download extension delta'. ¿Qué hago?
39. ¿Cómo leo un CSV con pandas?
40. Agregué una skill nueva y el CI falla en el paso de doc_verify con 'skills-count'. ¿Por qué?
41. Nuestro check `validar` imprime '0 problemas' y sale con 0. Un agente renombró el directorio que escanea y nadie lo notó en semanas. ¿Qué cambiamos?
42. Quiero que un agente consulte las tablas del lakehouse para responder preguntas de negocio.
43. ¿Puedo limpiar y deduplicar directamente al ingestar, así me ahorro la capa Bronze?
44. La deuda de un cliente difiere $290.000 entre el export de la mañana y el de la tarde. ¿Hay una partición entre las dos razones sociales?
45. Necesito el margen por producto de 2025; pedile al cliente el export que haga falta.
46. ¿Cómo agrego una columna a una tabla en Postgres?
47. Un subagente me reportó 'PR creado y tests en verde'. ¿Lo doy por terminado?
48. El A/B dio +12% de conversión con 40 usuarios por brazo. ¿Lo escalamos a todos?
49. Necesito guardar PDFs de facturas y la tabla de ventas en un lakehouse para entrenar un modelo después.

Respondé SOLO con un objeto JSON {"1": ["nombre-de-skill"], "2": [], ...} con una
entrada por pedido, usando los nombres exactos de las skills.
