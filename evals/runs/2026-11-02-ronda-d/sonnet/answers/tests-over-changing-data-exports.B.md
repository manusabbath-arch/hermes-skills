## Pedido 1

No retoques el número para que vuelva a pasar. Pasó de 130 a 1.176 filas sin cambios de código. Lo más probable es que haya cambiado la forma del insumo (otro período, más hojas o más móviles) y que el test tenga un literal que ya caducó. Eso lo hace un falso positivo, y la solución es reescribir la aserción, no borrarla.

Antes de tocar nada, confirmá una cosa: ¿cambió la forma del archivo o cambió el hecho que el test afirma? Si es la forma (período, filas, hojas), el test está mal. Si el hecho cambió, por ejemplo apareció una entidad nueva o volvió un equipo que no reportaba, el test hizo su trabajo y lo que hay que corregir es el código o la tabla.

Si es la forma, sigo este camino:

1. **No cambies `== 130` por `== 1176` ni por un piso más bajo.** Cualquiera de las dos es apostar a la descarga de hoy, y el próximo archivo lo rompe otra vez.
2. **Contá por otro camino.** Abrí el xlsx en el propio test con `openpyxl.load_workbook(ruta, read_only=True, data_only=True)`. Ubicá la fila de encabezado por su nombre, no por posición. Contá solo las filas que son una entidad, por la forma de la clave. Para patentes sirve `re.fullmatch(r"[A-Z]{3}\d{4}", movil)`. No uses "la celda no está vacía", porque así se cuela la fila `Total:` del pie de cada hoja.
3. **Afirmá relaciones, no cifras.**
   - La cantidad del lector es igual a la cantidad de filas por entidad en las hojas.
   - La suma del lector es igual a la suma del archivo, o a la fila `Total:` que el archivo declara.
   - Si hay hoja agregada, la cantidad del lector es menor que la cantidad contando esa hoja. Eso prueba que no llegó duplicada.
4. **Que la fuente sea explícita.** El lector tiene que aceptar `leer(ruta=None)`, y el test tiene que pasarle un archivo concreto.
5. **Comprobá que la aserción muerde.** Mutá el lector. Si pierde filas, tiene que dar rojo, por ejemplo `6 != 9`. Si suma la hoja agregada, también, por ejemplo `18 != 9`. Si pasa con las dos mutaciones, está midiendo el mismo camino que el lector y no protege nada.

Pasame el test y el código del lector y lo reescribo con esas aserciones.

## Pedido 2

Se puede, pero con una condición. Un resolutor que toma "el más nuevo" a ciegas es lo que causó el rojo del Pedido 1. Cada número que produce depende de quién descargó último.

Si igual lo querés, hacelo así:

- **El lector recibe la ruta.** Usá `leer(ruta=None)`. El resolutor del más nuevo es solo el valor por defecto, que se usa cuando no pasás ruta.
- **Mostrá qué archivo usó.** Imprimí el nombre del archivo y el período al empezar, por ejemplo en el header de pytest, para que un rojo diga qué archivo miró.
- **Un fixture centraliza la resolución.** Ordená los `*.xlsx` por `mtime` y devolvé el último. Si no hay ninguno, no devuelvas `None`. Salteá con el motivo escrito: `pytest.skip(f"sin export en {carpeta}")`.
- **Las aserciones tienen que ser estructurales.** Si el test seguía apostando a cifras de un período, lo que cambia es la fecha de rotura, no el problema. Vale lo que dice el Pedido 1.
- **Los tests unitarios usan un fixture sintético.** Escribilo en `tmp_path` con `openpyxl`, con una hoja por entidad más la agregada que las suma. Ese test es determinista. El que lee el archivo real queda como humo estructural.

## Pedido 3

**Todavía no.** Que la suite esté verde no dice nada, porque un skip por insumo ausente deja la suite verde sin haber medido nada.

- **Para el commit está bien saltearlo.** No pudiste haber roto lo que no tocaste.
- **Para el push no.** El tramo que tiene que medir, sea el push, el CI o el chequeo completo, tiene que convertir ese skip en fallo. Se hace con un flag que se usa solo ahí, por ejemplo `--requiere-datos`. Con ese flag, los tests marcados como "requiere insumo" fallan si falta el archivo, en vez de saltearse.
- **Primero conseguí el export de hoy.** Descargalo y corré la suite con `--requiere-datos`. Si no podés bajarlo, decidí a conciencia que vas a pushear sin haber medido, y no lo tomes como un verde.
- **Revisá el motivo del skip.** Tiene que decir qué archivo buscó y cuántas hojas trajo. Un skip mudo es indistinguible de un test que no corrió.

Si el flag todavía no existe, conviene agregarlo antes de pushear. Es un `addoption` en el `conftest` y un `pytest_runtest_makereport` o un chequeo en el skip que lo convierta en `pytest.fail`.

## Pedido 4

**No lo prendas para toda la sesión, y no cites 251 s contra 88 s como ahorro.** Los dos puntos son independientes.

**1. El número no prueba el caché.** Cronometrar una vez sin caché y una vez con caché mide sobre todo el caché de archivos del sistema operativo. En un caso medido, 251 s contra 88 s parecían un 2,8× y eran dos condiciones distintas. Alternando corridas en caliente, el resultado fue 175 s contra 161 s, un 8%. Lo que demuestra que el caché hace algo es el contador de aciertos, por ejemplo 101 lecturas pedidas y 75 servidas del caché. Para medirlo bien:

- Exponé el contador al cerrar la sesión de pytest, con algo como `VER_CACHE=1`.
- Corré las dos variantes alternadas y en caliente.
- Publicá los dos tiempos junto con el contador.

**2. Prenderlo global rompe tests.** Los que cuentan cuántas veces se parsea fallan en bloque. Eso incluye el archivo que prueba el caché y los que monkeypatchean el lector con el mismo contenido en distintos `tmp_path`. La clave es path más sha256 y no distingue la función parcheada. El diagnóstico va a parecer "el caché rompió algo", cuando esos tests medían otra cosa.

**Lo que sí te recomiendo:**

- **Opt-in y por proceso.** Usá `with cache_de_lecturas():`, con clave `(sha256 del archivo, parámetros)`. Si el export cambia a mitad de la corrida, la clave cambia y no se lee un dato viejo.
- **Devolvé una copia estructural, nunca el mismo objeto.** Si dos tests comparten una lista mutable y uno la ordena, el siguiente cambia de sujeto. Ese rojo aparece lejos y nadie lo atribuye al caché.
- **Prendelo solo para los tests marcados "requiere insumo".** Hacelo con un `pytest_runtest_call` (hookwrapper), compartiendo un único diccionario de módulo entre ellos. Agregá un marcador de escape, `sin_cache_lecturas`, para los tests que cuentan parseos.

Pasame el contador y las dos corridas en caliente y te digo si el ahorro justifica el cambio.

## Pedido 5

Con `skipif` y `sys.platform`:

```python
import sys
import pytest

@pytest.mark.skipif(sys.platform == "win32", reason="no soportado en Windows: <motivo concreto>")
def test_algo():
    ...
```

- **Todo un módulo:** poné `pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="...")` arriba del archivo.
- **Dentro del test:** `pytest.skip("motivo")` si la condición depende de algo que solo sabés en ejecución.
- **Escribí siempre el `reason`.** Con `-rs` pytest lo muestra en el resumen y un skip mudo no dice por qué se salteó.
- **Alternativa:** `os.name == "nt"` también sirve, pero `sys.platform == "win32"` es lo más usual.
