---
name: tests-over-changing-data-exports
description: "Use when tests read live exports that get re-downloaded: fixtures versus the newest file, structural assertions instead of vintage totals, skip-with-motivo that leaves the suite green, and a cache that must not hide a file that changed mid-run."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, exports, fixtures, data-quality, pytest]
    category: software-development
    related_skills: [erp-business-analysis, empirical-system-invariants]
---

# Tests sobre exports que cambian


## Cuándo NO aplicarla

Si el pedido es escribir un test sobre un fixture sintético que ya está en el repo, se
responde **solo eso**. Esta skill aplica cuando el test lee (o quiere leer) un archivo que
alguien vuelve a bajar.

Un test que lee «la descarga más nueva» de un sistema externo (ERP, CRM, GPS, banco) no
protege un defecto: protege el archivo que había cuando se escribió. El síntoma es un rojo
con diagnóstico equivocado —«¿se coló la hoja de totales?»— en un día en que lo único que
pasó fue que alguien bajó otro período. Medido en un caso real: siete descargas en quince
minutos, de tres períodos distintos y varias de un solo cliente/móvil, y la misma corrida
devolvió 130 y 1.176 filas sin que cambiara una línea de código.

## Procedimiento

1. **Declarar la fuente en el código, no en el test.** La función que lee acepta la ruta
   (`leer(ruta=None)`), el script imprime nombre de archivo y período, y el test puede
   pasarle un archivo explícito. Mientras el resolutor tome «la más nueva» a ciegas, todo
   número que produzca depende de quién descargó último.
2. **Separar estructura de vintage.** La aserción va sobre la forma del dato: no se duplica
   la hoja/fila agregada, hay una hoja por entidad, las filas con coordenada o clave son
   ≥95% de las filas, los totales son uno por entidad y sin repetidos. Nada de
   `700 < total < 800`, `len(hojas) == 5` ni un total absoluto.
3. **Si falta el insumo que el test necesita para medir, saltear con el motivo escrito**
   (`pytest.skip(f"fuente insuficiente: {ruta} trae {n} hoja(s)")`). Saltear porque la
   descarga es parcial es distinto de aflojar la aserción porque el número no cierra: el
   primero dice qué archivo miró, el segundo esconde el defecto. **Pero un skip por
   insumo ausente deja la suite verde midiendo cero**: el commit puede saltearlo (no pudo
   haber roto lo que no tocó), y el tramo que tiene que medir —push, CI, el chequeo
   completo— tiene que convertir ese skip en fallo con un flag usado sólo ahí
   (`--requiere-datos`). Un marcador de «requiere insumo» más un `conftest` que saltea
   cuando la carpeta falta o está vacía es exactamente el punto donde la suite se vuelve
   verde sin haber medido un solo dato.
4. **Tolerancia en proporción, no en unidades absolutas**, cuando las dos medidas tienen que
   ser «la misma magnitud» (día contra tramos, comprobante contra detalle): `0,5%`. Un
   `1 km` o `$1` se calibró contra un período y se rompe con otro.
5. **Poblar los tests unitarios con un fixture sintético** del archivo (una hoja por entidad
   más la agregada que las suma), escrito en `tmp_path` con la librería que escribe el
   formato. Ese test es determinista y cubre la trampa; el test contra el archivo real queda
   como humo con aserciones estructurales.

## La aserción contra el archivo: contar por el otro camino

Cuando el test tiene que leer el insumo real, la forma que sobrevive a la próxima descarga es
comparar el lector contra **el archivo**, contado por un camino independiente:

1. Abrir el archivo en el propio test con la librería del formato
   (`openpyxl.load_workbook(ruta, read_only=True, data_only=True)`) y ubicar la fila de
   encabezado **por su nombre**, no por posición: las hojas traen título y filas en blanco arriba.
2. Contar sólo lo que **es** una entidad, por la forma de la clave, no por «la celda no está
   vacía». En un export de cargas la clave es una patente (`re.fullmatch(r"[A-Z]{3}\d{4}", movil)`);
   con «no vacío» entra la fila `Total: ` que cada hoja agrega al pie y el conteo da 14 donde hay 9.
3. Afirmar las tres cosas: cantidad del lector == cantidad por entidad, suma del lector == suma del
   archivo, y —si hay hoja agregada— cantidad del lector < cantidad contando la agregada.
4. La agrupación (mes, entidad) se afirma por consistencia, no por literal: la tabla suma lo mismo
   que las filas, cada clave existe en las filas y su mes es el de sus fechas. Nunca
   `tabla[("2026-09", "ABC1234")] == 12.00`.

## Clasificar el rojo antes de tocar el test

Un rojo sobre datos reales es una de dos cosas, y se decide midiendo antes de editar nada:

- **Verdadero positivo**: el mundo cambió (volvió un equipo que no reportaba, apareció una
  entidad nueva, cambió el padrón). Se corrige la afirmación —la tabla, la validación, la
  constante del código— y el test **no se toca**: hizo su trabajo.
- **Falso positivo**: caducó la premisa del test (un literal, un rango, un `== N`). Se
  reescribe la aserción, no se borra.

La pregunta que decide: ¿cambió la **forma** del insumo (hojas, período, filas, columnas) o
cambió el **hecho** que el test afirma con el método intacto? Forma → falso positivo.
Hecho → hallazgo: va a una validación con archivo, sha y fecha, y puede confirmar el
diagnóstico anterior en vez de retractarlo. Un hallazgo así se demuestra mejor partiendo el
export en ventanas —una sin la variable y otras con ella— que discutiendo el número.

## Cuando la suite lee el mismo export cientos de veces

Si los tests marcados «requiere insumo» son muchos y cada uno vuelve a parsear el mismo archivo
grande, el costo no está en las aserciones sino en las lecturas repetidas — y se mide antes de
tocar nada: contar cuántas llamadas al lector hace la corrida y cuántas claves distintas hay. En
un caso medido sobre la compuerta: 83 lecturas, 25 distintas, 27 s de 65; las 58 repetidas valían
17,6 s. La forma que funciona es un caché **opt-in y por proceso** (`with cache_de_lecturas():`)
con la clave `(sha256 del archivo, parámetros de la llamada)`: así un export que cambia a mitad de
la corrida da otra clave y no se lee viejo, y el que no entra al contexto sigue viendo el archivo
como está. Lo que el caché devuelve es una **copia estructural**, nunca el mismo objeto: una lista
de filas mutable compartida entre dos tests hace que el que la ordena le cambie el sujeto al
siguiente, y ese rojo aparece lejos y no se atribuye a la caché.

**El ahorro se cita con los dos números, con cuántas lecturas salieron del caché y con las dos
corridas en caliente.** Cronometrar una vez sin caché y después con él mide, sobre todo, el caché de
archivos del sistema operativo: medido, 251 s contra 88 s parecían un 2,8× y eran dos condiciones
distintas; alternando en caliente fueron 175 s contra 161 s —un 8%—. Lo que prueba que el mecanismo
hace algo es el **contador de aciertos** (101 lecturas pedidas, 75 servidas del caché), no el reloj, y
por eso el contador se expone al cerrar la sesión de pytest (`VER_CACHE=1` o equivalente) y se
publica al lado de la cifra. Sin eso el número es una opinión sobre rendimiento, y peor: una que se
sostiene sobre la máquina y no sobre el código.

**Prenderlo para toda la sesión rompe los tests que cuentan parseos.** Los que miden cuántas veces se
parsea —el archivo que prueba el caché, y los que monkeypatchean el lector con el mismo contenido en
distintos `tmp_path`, porque la clave es path+sha256 y no distingue la función parcheada— fallan en
bloque, y el diagnóstico se lee como «el caché rompió algo» cuando lo que pasó es que medían otra
cosa. La forma que funciona: prenderlo en un `pytest_runtest_call` (hookwrapper) **sólo** para los
tests que llevan el marcador de «requiere insumo», compartiendo un único diccionario de módulo entre
esos tests para no perder el ahorro entre uno y otro, y un marcador de escape
(`sin_cache_lecturas`) para los que cuentan parseos. Fuera de los marcados el lector sigue viendo el
archivo como está, y la semántica opt-in que el propio test del caché afirma sigue siendo cierta.

## Trampas

- **La hoja/fila agregada duplica el total** y no falla ruidosamente: sumar la hoja `Todos`
  y las hojas por entidad da exactamente el doble. El filtro tiene que estar en el lector y
  el test tiene que afirmar que la agregada no llegó, no que el total esté en un rango.
- **Un test que se saltea nunca es verde por accidente**: imprimir el motivo con el nombre
  del archivo y el número de hojas. Un `skip` mudo es indistinguible de un test que no
  corrió.
- **Escribir el código del test a través de un heredoc del shell corrompe los escapes.**
  `\n`, `\r\n` y `\t` se interpretan en el JSON del tool y otra vez en el intérprete: un
  `"uno\r\n§\r\ndos"` termina con saltos reales dentro del literal y el archivo no compila
  (`unterminated string literal`). Construir la secuencia con `chr(92) + 'n'` e interpolar, o
  escribir el archivo con la herramienta de archivos, y verificar con
  `python -c "import ast; ast.parse(open(ruta, encoding='utf-8').read())"` antes de creer que
  quedó bien.
- **Un literal que ya falló una vez no se reemplaza por otro literal — y un piso también lo es.**
  `700 < total < 800` y `total > 900` fallan igual cuando el export pasa de dos meses a seis días:
  bajarlo de 900 a 400 es volver a apostar a la ventana de hoy, y el próximo archivo lo rompe otra vez.
  Reemplazarlo por la relación que el test quería medir: «el total supera la hoja más grande» prueba que
  no se quedó con una sola hoja sin depender del período, y «la cantidad del lector == la suma de filas
  de las hojas» + «la suma == la fila `Total:` que el propio archivo declara» reemplaza cualquier
  conteo o monto histórico. Si el número bajó a la mitad porque el export es más corto, la aserción que
  corresponde es una relación, no un piso más chico.
- **La forma del insumo no se prueba sólo con fixtures sintéticos.** El fixture fija la
  forma que había cuando se escribió. Para saber que la aserción sigue mordiendo el archivo
  real, copiarlo a un temporal, aplicar la corrupción conocida —columna ausente, fila
  duplicada, importe ×100, subtotal en el medio, archivo truncado— y exigir el rojo del
  chequeo que le corresponde, nombrando la ficha.
- **La aserción derivada se prueba mutando el lector, no el archivo.** Si el test nuevo compara
  contra el archivo, la pregunta es si muerde: hacerle perder filas al lector (p. ej. saltear las
  entidades sin un campo opcional) y exigir `6 != 9`; hacerle sumar la hoja agregada y exigir
  `18 != 9` más la guarda específica. Una aserción derivada que pasa con las dos mutaciones está
  midiendo el mismo camino que el lector y no protege nada.
- **El export nuevo puede caer mientras trabajás, y el rojo aparece en un test que no tocaste.** Un
  resolutor que toma «la más nueva» cambia de sujeto en cualquier momento: el commit propio sale verde,
  otra sesión commitea un test con el literal del export anterior, alguien baja el reporte del día y el
  push se corta por un rojo ajeno. Antes de arreglarlo se atribuye: `git log --format='%h %an %s' -1
  <sha>`, `git branch -r --contains <sha>` (¿está empujado?) y correr ese test en el commit padre. Si es
  de otra sesión y no está empujado, es trabajo en vuelo: se reporta con la ruta del archivo nuevo, el
  conteo viejo y el nuevo, y lo arregla quien escribió el literal — corregirlo desde la otra sesión pisa
  lo que esa sesión todavía está haciendo. Y no se empuja salteando el gate para esquivarlo: eso mete el
  rojo en el remoto.
- **Si al rebasar el conflicto es tu propio arreglo equivalente al de main, se queda el de main.** Dos
  sesiones pueden llegar al mismo test roto por el mismo export y escribir la misma aserción derivada; al
  rebasar, el conflicto no se "resuelve" reaplicando la tuya. En un rebase `--ours` es la rama sobre la que
  se rebasa —main— y `--theirs` es tu commit: `git checkout --ours <test>` y seguir. Traer tu versión
  duplica el arreglo y deja el archivo distinto del que ya está integrado, sin ganar nada.

## Fuente canónica

Repo-tap `manusabbath-arch/hermes-skills` (`skills/tests-over-changing-data-exports`). Editar acá, nunca la copia instalada.
