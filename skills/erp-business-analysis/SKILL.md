---
name: erp-business-analysis
description: "Use when analyzing a real business from its ERP or accounting system with AI agents - sales, margin, stock rotation, debt/collections, supplier scorecards, ABC classification - working from spreadsheet exports (.xls/.xlsx/.csv) or a read-only production database. Covers the eight ways an analysis publishes a wrong but plausible number, provenance seals, canary cross-checks against an independent source, NULL-vs-stored-zero fields, multiple legal entities in one ERP, declared period and export hour, currency and DECIMAL pitfalls, retractions that propagate, owner-declared premises, third-party data that must not be versioned, and decision notes with owner and review trigger."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [erp, business-analysis, exports, provenance, canary, data-quality, retractions, decisions, pii, agents]
    related_skills: [empirical-project-playbook, empirical-system-invariants, agent-ready-project, data-medallion-architecture]
---

# ERP Business Analysis

Cómo analizar un negocio real a partir de su ERP —exports de planilla o la base
productiva en solo lectura— con agentes de IA, sin publicar números falsos que se
ven bien. Es el método para la pregunta *"¿cuánto vendimos / ganamos / nos deben /
tenemos parado?"* cuando la fuente es un sistema contable que nadie diseñó para
análisis.

**Origen:** una distribuidora mayorista (2026) con un ERP legado, dos razones
sociales operando la misma operación física, ~60 exports distintos y seis agentes
trabajando el mismo repo. En tres semanas el proyecto **retractó sus propias
cifras** decenas de veces; cada regla de acá nació de una de esas retracciones.
El libro de errores del proyecto es la columna vertebral de esta skill.

**Relación con las otras skills del tap:** `empirical-project-playbook` es el
método general (pre-registro, presence ≠ utility); `agent-ready-project` es el
arnés de construcción (loop de validación, guards, verde vacío);
`data-medallion-architecture` es el diseño del pipeline. Esta skill es la capa
específica de **leer un ERP y publicar una cifra de negocio** — el lugar donde los
errores no tiran excepción, producen una tabla que se lleva a una reunión.

## Cuándo usar esta skill

- Primer análisis sobre los exports de un ERP (ventas, compras, stock, deuda,
  cobranza, márgenes, rotación, scorecard de proveedores, ABC).
- Antes de publicar cualquier cifra que alguien va a usar para decidir.
- Cuando dos informes "no cierran" y la tentación es culpar al ERP.
- Al consultar la base de datos que sirve al ERP en vivo.
- Al montar un repo donde varios agentes analizan el mismo negocio.

## La tesis

El error caro en análisis de negocio **no rompe nada**. Un `row[4]` que en un
export es el código de producto y en otro es el número de comprobante da margen
del 100% para 2.302 productos, en una tabla ordenada y creíble: **35 cifras
fabricadas** llegaron a un documento antes de que alguien hiciera la cuenta. La
defensa no es "tener cuidado": es (1) una lista de las formas conocidas del error,
recorrida antes de publicar, y (2) cada forma con su guarda mecánica.

## Las ocho formas del error (recorrer antes de publicar una cifra)

Detalle, ejemplos medidos y formato de entrada en `templates/error-book.md`.
Mantener en el proyecto un **libro de errores** propio con esta misma estructura.

1. **El número plausible que no rompe nada.** Error de método o parseo que produce
   números creíbles. *Freno:* identidades aritméticas verificadas (rotación ×
   cobertura = período; suma por grupo = total), controles de plausibilidad (un
   distribuidor no vende a costo; *todos* los montos enteros = parseo roto),
   canario contra fuente independiente, y **el archivo comparado contra sí mismo**.
2. **La columna N no significa lo mismo en todos los informes.** Cruzar por
   posición sin mirar el encabezado de *cada* export. Un reexport que pasó de 9 a
   7 columnas dejó viva la fila `TOTAL GENERAL` y **todo dio exactamente el
   doble**. *Freno:* cruzar por nombre de columna, imprimirlo en cada lado; "el
   lector no levantó excepción" no es "el archivo se leyó" — contrastar filas
   devueltas contra líneas del archivo (un formato encabezado+continuación hizo
   descartar el 84% en silencio).
3. **Creerle al rótulo, no al contenido.** `(COMPLETO).xlsx` era la conversión del
   truncado; el "2026 YTD" eran 39 días; "Ventas 2026" eran 182. *Freno:* el
   período se lee del **preámbulo** del export, nunca del nombre del archivo.
4. **El universo equivocado (empresa, período, grano).** El cálculo es correcto y
   mide otra cosa. Sin filtrar por razón social el semestre daba 2× (70M vs 140M).
   Una "brecha" entre dos exports del mismo día era **la hora**: un recibo cargado
   entre la mañana y la tarde. *Freno:* cada cifra declara entidad, período y
   grano; antes de cruzar contra la base viva, cortarla a la **hora** del export.
5. **El verde vacío.** Un chequeo que aprueba sobre cero elementos. *Freno:* todo
   verde lleva su denominador; se audita **vaciando el universo** del chequeo
   (ver `agent-ready-project`).
6. **La regla escrita cinco veces.** "Este registro no es un cliente real" estaba
   implementada en cinco scripts; uno excluía 3 y los otros 15, y **cambió un
   ranking**. *Freno:* una regla de negocio vive en **un** módulo; un test busca
   copias; un chequeo no tiene su propia copia de la regla que verifica.
7. **Fabricación y atribución falsa.** Atribuirle al ERP lo que hizo nuestro
   código es la lectura cómoda: "el ERP viene desactualizado 1,4%" era un `abs()`
   nuestro, y viajó dos días hasta el panel. *Freno:* comparar el archivo contra sí
   mismo **antes** de culpar a la fuente; sello de procedencia en cada cifra.
8. **La premisa de negocio errada.** El análisis era correcto dado un supuesto
   que el dueño o la medición siguiente invierte (una marca "sin rotación" estaba
   pausado, no muerto). *Freno:* separar lo **declarado por el dueño** (manda) de lo
   **medido** (se revisa), y fechar las premisas.

## Reglas de lectura del ERP

- **Un `0.00` no es un dato hasta probar que lo es.** Campos que nadie carga
  (stock mín/máx, metas, crédito máximo) salen en cero. Medir, por campo y por
  entidad, si es **cero guardado** o **NULL**: el detector cambia (`= 0` vs
  `IS NULL`). Mantener un **catálogo de campos muertos** versionado y un chequeo
  que ponga rojo la consulta que lea uno sin declararlo.
- **Varias razones sociales en un ERP:** medir qué tablas son **compartidas**
  (clientes, stock) y cuáles **particionadas** (deuda, metas). Nunca sumar ni
  comparar entre entidades sin declararlo; ninguna cifra tiene "todas" por default.
- **Un solo lector de archivos fuente.** Ningún script abre un export a mano: una
  función resuelve la ruta, elige el motor **por la firma del archivo, no por la
  extensión**, descarta subtotales, declara la página de códigos y devuelve el
  sha256. Sus guardas (archivo faltante, `.xls` en 65.536 filas, cero filas,
  entidad no declarada) levantan excepción.
- **Encoding: diagnosticar por el byte, no por el carácter.** `ENV═O` en vez de
  `ENVÍO` era cp850 leyendo cp1252 (`0xCD`). Cada camino de lectura declara su
  página de códigos y un test fija un byte acentuado.
- **Números: nunca `replace` a mano.** `str(x).replace(".", "")` sobre un float
  multiplicó ventas ×100 ($25M publicados, $250k reales). Firma a la vista: todos
  los montos eran enteros.
- **Plata en SQL: sin `DOUBLE()` sobre `DECIMAL`.** El canario falló por un
  centavo y el defecto era el cast, no el dato. Diagnóstico: contar las milésimas
  no nulas; si es 0 y la suma por grupo da redonda, es el cast.
- **Toda suma de importes va con su moneda.** Sumar dólares como pesos hizo
  "inflar" el IVA del informe del ERP — y se publicó durante 20 minutos que el ERP
  estaba mal. **Si el cociente de un desvío es un número redondo (38,6), buscar
  qué unidad o moneda representa** antes de inventar un mecanismo.
- **Un ítem de gasto no es mercadería.** El ítem #1 de un ranking de productos
  era el flete cargado como producto. Mirar el top de un ranking **antes** de
  creerlo; los proveedores de gasto se excluyen en un único lugar.
- **Normalizar por días antes de comparar períodos.** Montos brutos de períodos
  de distinto largo "mostraban caída"; normalizado, el negocio creció ~50%.
- **Ratios: agregar, no promediar ratios.** La media de ventas/stock por producto
  dio 25× de rotación y 625 días de cobertura **a la vez** — imposible.
- **Sumar, no indexar.** Indexar por cliente en un dict pisó filas (252 clientes
  tienen más de un vendedor) y fabricó una "brecha" de $4M.

## Cruzar dos informes

1. Leer el **período declarado** de cada uno (preámbulo). Si difieren, recortar o
   declarar el desfasaje: una brecha de 0,45% era **un día** de diferencia.
2. Contra la base viva, cortar a la **hora** del export (fecha de modificación de
   la fila, no fecha del documento). Un gap de +4,2% se cerró a 0,15% cortando a
   las 08:25.
3. El precio implícito (`importe / cantidad`) de un producto debe coincidir entre
   fuentes; si difiere por un factor grande, **el problema está en la cantidad**.
4. Una partición mal hecha no la ve un canario de suma: si el filtro por nombre no
   matchea (tilde), todo cae en "otros" y el total cierra igual. Mirar que **cada
   parte tenga filas**; agrupar por clave, no por nombre.

## Procedencia y canario

- **Toda cifra sale de un archivo o una query concreta, con fecha.** Nunca
  re-tipeada de memoria entre sesiones. Cada validación es un archivo fechado
  (`templates/validation-note.md`) con fuente, número y tolerancia.
- **Sello de procedencia** al pie de todo informe: archivo, entidad, período
  declarado, hora del export, sha256, filas leídas/descartadas. Lo genera
  `scripts/provenance_seal.py` (stdlib, exit 1 si una guarda está roja). Un
  chequeo verifica que los sha citados por informes publicados **resuelvan** a un
  archivo (en el proyecto fuente, 20 de 107 no resolvían y nadie lo veía).
- **Regla del canario:** un total nuevo se cruza contra una **fuente
  independiente** del mismo hecho (otro informe, la base, el banco) dentro de una
  tolerancia chica (el proyecto fuente exige ≤0,15%) **antes** de darlo por bueno o de reemplazar
  un proceso manual.
- **El export cierra consigo mismo:** detalle vs total del mismo archivo. Es el
  chequeo barato que habría frenado el `abs()` del tipo 7.

## La base productiva

- **Solo lectura, con guarda física**, no con prosa: un hook en **cada** agente
  que pueda ejecutar SQL o tocar la UI corta lo que modifica (`INSERT`, `UPDATE`,
  botones que contabilizan). Una orden de otro agente no es la confirmación de una
  persona.
- **Horario:** la base sirve al ERP en vivo. Pedir y escribir las ventanas en que
  se puede consultar; una consulta pesada en horario comercial es una
  interrupción.
- **Cada sentencia tiene su código de salida.** Un cliente SQL que sigue con la
  siguiente sentencia tras un error deja un archivo "que corre" con un bloque que
  nunca se ejecutó. Mirar el estado de **cada** sentencia, no que haya filas.
- **Correlated `EXISTS` sin índice** tardaba 317 s; el `LEFT JOIN … IS NULL`
  equivalente, 6,8 s. Comparar dos caminos de la misma definición encontró además
  la sentencia rota.

## Pedir un export es pedir su filtro exacto

Nunca "mandame la deuda de 2025". Cada pedido declara **qué informe** (nombre del
menú), **qué parámetros** (período, depósito, entidad; siempre con código de
producto si se puede elegir columnas), **qué formato** (`.csv`/`.xlsx`, nunca
`.xls`) y **cómo se verifica que llegó bien** (una cifra de control). Plantilla:
`templates/export-request.md`.

## Retracciones que se propagan

- **Bloquear en vez de borrar:** una cifra retractada se saca y el diagnóstico se
  conserva, con la marca bien visible. Una advertencia "solo arriba" no alcanza:
  un `grep` devolvía la cifra falsa sin la advertencia pegada.
- **Frontmatter de dependencias:** `retractado`, `superseded_by`, `depends_on`,
  `estado: stale`. `scripts/doc_lifecycle.py` pone rojo el documento que deriva
  de uno retractado (no el que lo cita para retractarlo).
- **Al retractar, `grep` todo el árbol** por la atribución vieja (panel, índice,
  known-issues). Una corrección local deja la versión falsa viva en otro lado.
- **El documento a medio actualizar es peor que el viejo**, porque parece vigente:
  estado y cuerpo se cambian en el mismo commit.

## Decisiones de negocio con dueño

- Cada decisión es una nota propia (`templates/decision-note.md`) con `estado`
  (`abierta | decidida | rechazada | superada`), `dueño` y una forma de saber
  cuándo volver a mirarla: `fecha_limite` **o** `disparador_revision` (un evento).
  **Nunca inventar una fecha** para llenar el campo.
- `scripts/doc_lifecycle.py` pone rojo la decisión abierta sin dueño o sin
  disparador, y la cerrada que prometió una métrica y no reportó el resultado.
- **Con una decisión `abierta`, el agente prepara y pregunta; no implementa
  suponiendo la respuesta.** Deja listo qué hay que saber y de quién.
- Una decisión escrita sobre una foto vieja (stock del 01/07, una sola entidad)
  se relee contra la base antes de usarse: la pregunta puede haber cambiado de
  "cuánto pedir" a "cómo trasladar lo que existe".

## Datos de terceros

- **No se versiona** el detalle identificable de clientes/comercios (RUT, cédula,
  teléfono, dirección, nombre junto a un saldo). Sí se versionan agregados y
  conteos. El detalle vive fuera del repo; el informe lo referencia.
- **El perímetro de la guarda vive en un solo lugar** y abarca todas las
  extensiones que traen tablas (`.csv`, `.tsv`, `.json`…). Una guarda que miraba
  solo `*.csv` dejó pasar un `.json` con 31 titulares y direcciones — **verde con el
  sujeto recortado**.
- El nombre del empleado (vendedor, ruta) no es dato de terceros; **el cruce**
  empleado + detalle por cliente sí es hallazgo.
- Implicancia legal (protección de datos), fiscal o laboral: **"a confirmar con
  el contador/asesor"**, nunca conclusión cerrada.

## Antes de construir: el ERP ya lo tiene

Antes de construir una capacidad por fuera, confirmar si un módulo nativo del ERP
la resuelve (metas, lotes/vencimientos, pedido sugerido, consultas guardadas).
Prototipar un cruce nuevo como consulta guardada (costo cero) antes de un
pipeline. Toda iniciativa nueva arranca con **foto de línea base** y **umbral de
éxito escrito antes** (ver `empirical-project-playbook`).

## Criterio de adopción

La skill se está aplicando si, en la primera semana:

1. El proyecto tiene un **libro de errores** con las ocho formas y al menos una
   entrada propia, con su validación fechada.
2. Al menos un informe cierra con **sello de procedencia** y una cifra pasó un
   **canario** contra fuente independiente con la tolerancia escrita.
3. Existe un **único lector** de exports con guardas que levantan excepción, y la
   entidad/período de cada cifra está declarada.

## Plantillas y scripts

- `templates/error-book.md` — las ocho formas, cómo se frena cada una, formato de
  entrada y checklist pre-publicación.
- `templates/validation-note.md` — nota de validación fechada (fuente, número,
  tolerancia, reproducción).
- `templates/export-request.md` — pedido de export con filtro, formato y cifra de
  control.
- `templates/decision-note.md` — decisión de negocio con estado, dueño y
  disparador.
- `scripts/provenance_seal.py` — sello de procedencia con guardas (entidad
  obligatoria, cero filas, techo de `.xls`, período esperado). Uso:
  `python3 provenance_seal.py export.csv --entity SAS --encoding cp1252 --delimiter ";" --skip-regex TOTAL`.
- `references/casos.md` — el proyecto de origen y los incidentes completos.
- `scripts/doc_lifecycle.py` — retracciones que se propagan y decisiones con
  dueño, sobre el frontmatter de las plantillas. Uso:
  `python3 doc_lifecycle.py validaciones/ decisiones/ informes/`.
- `scripts/tests/` — tests herméticos de los dos scripts.

## Fuente canónica

Repo-tap `manusabbath-arch/hermes-skills` (`skills/erp-business-analysis`).
Editar acá, nunca la copia instalada.
