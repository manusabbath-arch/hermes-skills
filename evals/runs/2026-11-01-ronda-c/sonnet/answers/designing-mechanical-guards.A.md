## Pedido 1

Para que una regla como "todo reporte declara su source hash" no se rompa más, no alcanza con documentarla: hay que hacerla mecánica, es decir, que el incumplimiento sea imposible o falle de forma visible.

1. **Generar en vez de escribir a mano.** Que el reporte se produzca desde una única función o plantilla que calcule e inserte el hash. Si nadie lo escribe a mano, nadie lo olvida.
2. **Validar al producir.** Esa misma función se niega a emitir un reporte sin hash, o con uno que no coincide con el de la fuente real.
3. **Un chequeo en el gate (CI o pre-commit).** Que recorra todos los reportes y falle si falta el campo, está vacío o no tiene el formato esperado (por ejemplo, 64 caracteres hex para SHA-256). Que el mensaje de error diga qué archivo falla y cómo arreglarlo.
4. **Probar el chequeo con un caso malo.** Agregá un test con un reporte sin hash y verificá que el gate lo rechaza. Si no lo probás, no sabés que el chequeo funciona.
5. **Cubrir los reportes futuros.** Que el chequeo use un glob sobre el directorio, no una lista fija de archivos, para que los reportes nuevos queden incluidos solos.

Si me decís el formato de los reportes y dónde corre el gate, te escribo el chequeo concreto.

## Pedido 2

Todavía no lo mandaría. "Verde en el repo real" solo dice que el chequeo no encuentra problemas hoy, pero no demuestra que detecte algo. Un chequeo que nunca falla puede estar roto sin que te des cuenta.

Antes de publicarlo:

1. Creá un caso malo a propósito, que viole la regla, y confirmá que el chequeo da rojo.
2. Revertí ese caso y confirmá que vuelve a verde.
3. Verificá que realmente se ejecute en el gate (que esté registrado y no se omita por un filtro o una ruta).

Con eso, sí está listo. Yo no puedo correr comandos acá, así que esa verificación te toca a vos. Si querés, te ayudo a armar el caso malo. Tampoco publiqué nada: eso lo decidís vos.

## Pedido 3

Podés commitear tu fix de una línea sin arreglar los tres chequeos viejos, pero sin saltarte el gate de forma silenciosa.

1. **Confirmá que fallan sin tu cambio.** Corré el gate en la rama base limpia. Si ya están rojos ahí, no son tuyos y tenés la evidencia.
2. **Elegí una vía legítima:**
   - Si el equipo tiene un mecanismo para bypass documentado, usalo y dejá escrito en el mensaje del commit o del PR que los tres fallos son previos.
   - Si no, pedile a quien administra el gate que los marque como fallos conocidos, o abrí un issue por cada uno.
3. **Evitá** `--no-verify`, desactivar los chequeos o editarlos para que pasen, salvo que quien mantiene el gate te lo autorice. Eso debilita la protección para todos.

Un fix de una línea es una buena razón para pedir ese permiso rápido. Si me pasás los nombres de los tres chequeos y el error de cada uno, te ayudo a ver si alguno tiene un arreglo trivial.

## Pedido 4

No te recomiendo `|| true`. Hace que el comando siempre devuelva éxito, así que el chequeo corre pero nadie se entera cuando falla. En la práctica queda desactivado, y con el tiempo la gente deja de mirarlo.

Alternativas según el problema:

- **Falsos positivos:** ajustá la regla o agregá excepciones puntuales y justificadas, en vez de silenciarlo todo.
- **Chequeo en prueba:** si querés observarlo antes de hacerlo obligatorio, usá un modo informativo explícito. Por ejemplo, `continue-on-error: true` en GitHub Actions, o un job marcado como "allow failure". Así el fallo se ve en el resultado, solo que no bloquea.
- **Ruido por volumen:** reducí la salida o separá los avisos de los errores reales.

Si igual lo vas a hacer, dejá un comentario con el motivo y una fecha o un issue para revisarlo, y que el resultado se siga viendo en algún lado. Si me pasás el comando y un ejemplo del ruido, te propongo algo más preciso.

## Pedido 5

It depends on what you want to rename.

- **In your editor (safest):** Use the rename-symbol feature. In VS Code, put the cursor on the name and press `F2`. In PyCharm, use `Shift+F6`. Both update every reference across the project.
- **By hand:** Change the `def` line, then search for every call to the old name, including imports, strings, and tests. For example, `def old_name():` becomes `def new_name():`.
- **Keeping compatibility:** If other code still uses the old name, leave an alias for a while:
  ```python
  def new_name(...):
      ...

  old_name = new_name  # deprecated alias
  ```
- **From a script:** The `rope` library can do refactors programmatically.

Watch for dynamic uses like `getattr(obj, "old_name")` or names in config files. A plain text search won't catch every case, so run your tests afterward.

If you share the function and where it's used, I can show you the exact change.
