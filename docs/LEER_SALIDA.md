# Cómo leer la salida de nec2c con un programa

**Recomendación: hacer tolerantes los analizadores.** Un programa que lea la salida de NEC-2 no debería depender de
espacios exactos, de posiciones de columna ni de un único estilo de línea, porque distintos motores y versiones
escriben la misma información con pequeñas diferencias.

## Un caso real

`nec2c` escribe la frecuencia así (así está en su código, `main.c`):

```
FREQUENCY : 1.4100E+01 MHz
```

Un analizador escrito para otro motor que use `=` en vez de `:` no la encuentra:

```
FREQUENCY = 1.4100E+01 MHz
```

La solución correcta es aceptar ambas formas, no modificar el motor:

```python
import re
m = re.search(r"FREQUENCY\s*[:=]\s*([0-9.+\-Ee]+)\s*MHz", linea)
f_mhz = float(m.group(1))
```

## Buenas prácticas

- **Buscar por títulos de sección, no por número de línea:** `FREQUENCY`, `ANTENNA INPUT PARAMETERS`, `RADIATION PATTERNS`.
- **Aceptar `:` y `=`** (y cualquier cantidad de espacios) en las líneas de tipo `CLAVE : valor`.
- **Extraer los números con una expresión regular** en vez de cortar columnas fijas. El patrón de ejemplo es
  `[-+]?\d+\.?\d*(?:[Ee][-+]?\d+)?`.
- **Exigir que una fila de datos empiece con un número.** Líneas como `DATA CARD No: 5 EN 0 0 0 …` también contienen
  números y, si no se descartan, se leen como si fueran una fila de la tabla.
- **Tratar `-999.99` como "sin valor".** `nec2c` lo imprime donde una ganancia no está definida, por ejemplo la componente
  vertical de un dipolo horizontal.
- **No suponer que el patrón cubre todos los ángulos.** En el ejemplo con suelo (`GN`), la tabla solo llega hasta θ = 90°.
- **Una salida puede tener varias frecuencias** (tarjeta `FR` con barrido): crear un bloque de resultados por cada línea
  `FREQUENCY`.
- **Comprobar el resultado:** si no se encontró ninguna frecuencia o la tabla quedó vacía, avisar con un error claro en vez
  de continuar con datos vacíos.

## Ejemplo completo

[`examples/leer_salida.py`](../examples/leer_salida.py) implementa estas reglas. Devuelve, para cada frecuencia, la
frecuencia en MHz, la impedancia de entrada (como número complejo) y la tabla de ganancias.

```
python examples/leer_salida.py dipolo_20m.txt
```

Con la salida de `examples/dipolo_20m.nec` imprime la frecuencia (14,1 MHz), la impedancia de entrada, 10 puntos del
patrón y una ganancia máxima de 7,06 dB en θ = 60°.

**Qué se probó:** el script se ejecutó con la salida de `dipolo_20m.nec` y con la del caso `Input/3E_.NEC`. Para comprobar
que acepta ambos estilos, se repitió la lectura de la salida del dipolo reemplazando `FREQUENCY :` por `FREQUENCY =`, y
el resultado fue el mismo.

**Limitaciones:** solo toma la primera impedancia de entrada de cada frecuencia (si hay varias fuentes, habría que leer
todas las filas), y no interpreta otras secciones de la salida, como corrientes en los segmentos.
