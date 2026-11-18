# nec2c para Windows de 64 bits

Ejecutable `nec2c.exe` para Windows, compilado automáticamente con GitHub Actions a partir del código de
**nec2c 1.3** (motor de simulación de antenas NEC-2 escrito en C por Neoklis Kyriazis, 5B4AZ).
Sirve para ejecutar simulaciones NEC-2 desde la línea de comandos o desde scripts (Python, `.bat`, etc.),
sin interfaz gráfica.

*English summary:* a standalone 64-bit Windows build of nec2c 1.3 (NEC-2 antenna simulation engine, command line),
built on GitHub Actions with MSYS2/GCC and statically linked. Download it from
[Releases](../../releases/latest). GPL-3.0.

## Descarga

Ve a la sección **[Releases](../../releases/latest)** y descarga `nec2c.exe`. No requiere instalación ni DLL de MSYS2:
solo depende de librerías que ya trae Windows 10 y 11 (`KERNEL32.dll` y `api-ms-win-crt-*`).

Para comprobar que el archivo es el publicado, compara su huella SHA-256 con la de `nec2c.exe.sha256`
del mismo Release:

```
certutil -hashfile nec2c.exe SHA256
```

## Uso

```
nec2c.exe -i entrada.nec -o salida.txt
```

| Opción | Efecto |
|---|---|
| `-i archivo` | archivo de entrada (tarjetas NEC) |
| `-o archivo` | archivo de salida |
| `-v` | muestra la versión y termina |
| `-h` | muestra la ayuda y termina |

Sin argumentos, el programa muestra la ayuda y termina.

### Ejemplo

En `examples/dipolo_20m.nec` hay un dipolo de media onda para 20 m, a 10 m de altura sobre suelo real:

```
nec2c.exe -i examples\dipolo_20m.nec -o dipolo_20m.txt
```

En la salida buscar:

- `ANTENNA INPUT PARAMETERS`: impedancia de entrada (real e imaginaria, en ohmios).
- `RADIATION PATTERNS`: ganancia en dB para cada ángulo (`VERTC`, `HORIZ` y `TOTAL`).

La carpeta `Input/` trae unos cien archivos de ejemplo del proyecto original (antenas Yagi, entre otras).

### Formato de entrada

Es el formato clásico de NEC-2, con una tarjeta por línea. Las más usadas:

| Tarjeta | Significado |
|---|---|
| `CM` / `CE` | comentarios / fin de comentarios |
| `GW` | hilo recto (tag, segmentos, extremos, radio) |
| `GE` | fin de la geometría |
| `GN` | suelo (tipo, permitividad, conductividad) |
| `EX` | excitación (fuente) |
| `FR` | frecuencia o barrido de frecuencias |
| `RP` | diagrama de radiación |
| `EN` | fin del archivo |

La referencia completa está en el manual de NEC-2 (Burke y Poggio, Lawrence Livermore National Laboratory).

## De dónde viene

- **Código fuente:** [KJ7LNW/nec2c](https://github.com/KJ7LNW/nec2c), commit `55be1e0`. Es un fork mantenido del nec2c 1.3 de
  Kyriazis; no es el repositorio original.
- **Primer commit de este repositorio:** importación de ese código sin modificaciones.
- **Segundo commit:** parche mínimo de portabilidad, de tres archivos y 19 líneas, porque el original usa funciones
  POSIX que no existen en el MinGW nativo de Windows:

  | Original (POSIX) | Reemplazo en Windows |
  |---|---|
  | `sigaction()` | `signal()` |
  | `times()` y `sysconf()` | `clock()` |
  | `#include <sys/times.h>` | se omite |

  En Linux el comportamiento no cambia: los cambios solo se activan con `_WIN32` o `NEC2C_PORTABLE`.
- El archivo `README` original quedó como `README.upstream.txt`.

## Qué se verificó, y qué no

- El workflow compila con GCC (MSYS2 UCRT64, `-O2 -static`) en un runner `windows-latest`, y ejecuta `-v` y un caso
  de prueba desde CMD, sin MSYS2 en el PATH.
- Con el ejemplo `Input/3E_.NEC`, la salida en Windows coincide con la de la misma versión compilada en Linux
  (ignorando las líneas de fecha y tiempo).
- **No** se ha hecho una validación exhaustiva contra otros casos ni contra otras compilaciones de NEC-2.
- El ejecutable no está firmado digitalmente, así que Windows SmartScreen o un antivirus pueden mostrar un aviso.

## Compilar tú mismo

**En GitHub:** pestaña *Actions* → `build-nec2c-win64` → *Run workflow*. El resultado queda como artefacto y como Release.

**En tu PC**, con [MSYS2](https://www.msys2.org/) abierto en la terminal *UCRT64*:

```
pacman -S --needed git mingw-w64-ucrt-x86_64-gcc
git clone https://github.com/sergiozxp/nec2c-windows
cd nec2c-windows
gcc -O2 -static -Wl,--no-insert-timestamp -DPACKAGE_STRING='"nec2c 1.3"' -o nec2c.exe \
  calculations.c geometry.c input.c matrix.c network.c shared.c fields.c \
  ground.c main.c misc.c radiation.c somnec.c -lm
./nec2c.exe -v
```

No hace falta `autogen.sh` ni `configure`.

## Licencia y créditos

- nec2c: GNU GPL v3 (ver `COPYING`). Autor: Neoklis Kyriazis, 5B4AZ.
- NEC-2: Lawrence Livermore National Laboratory (G. J. Burke y A. J. Poggio).
- Este repositorio solo agrega el parche de portabilidad, el workflow y la documentación, bajo la misma licencia.
