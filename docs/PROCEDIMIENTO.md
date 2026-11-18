# Procedimiento: cómo se obtuvo `nec2c.exe`

Los comandos de este documento son los que se ejecutaron. Cada bloque indica **dónde** se probó:

- **Linux:** probado en un entorno Linux con `gcc`.
- **GitHub Actions:** ejecutado por el workflow `build-nec2c-win64` en un runner `windows-latest`.
- **Tu PC:** instrucciones equivalentes que no se han ejecutado en un PC real (usan los mismos comandos del runner).

## 1. Obtener el código fuente (Linux)

```bash
git clone https://github.com/KJ7LNW/nec2c.git
cd nec2c
git log --oneline | head -1        # 55be1e0
```

El código se compila a partir de `calculations.c geometry.c input.c matrix.c network.c shared.c fields.c ground.c main.c misc.c radiation.c somnec.c`.
`nec2c.c` es una versión antigua en un solo archivo y no forma parte de la compilación. El ejecutable no queda en `src/`: ese directorio no existe.

## 2. Qué impide compilar en Windows (Linux)

```bash
grep -n -E "sigaction|times\(|sys/times|sysconf" *.c *.h
```

Aparecen `sigaction()` en `main.c`, `times()` y `sysconf(_SC_CLK_TCK)` en `misc.c`, y `#include <sys/times.h>` en `nec2c.h`.
Ninguno existe en el MinGW nativo (MSYS2 UCRT64).

## 3. El parche

Está en [`patches/windows-portability.patch`](../patches/windows-portability.patch) (3 archivos, 19 líneas añadidas). Se activa con `_WIN32` o con `-DNEC2C_PORTABLE`.
Para aplicarlo sobre el código original:

```bash
git apply patches/windows-portability.patch
```

## 4. Comprobar que el parche no cambia los resultados (Linux)

Se compilaron las dos variantes (la estándar y la de Windows, forzada con `-DNEC2C_PORTABLE`) y se compararon sus salidas con un caso de ejemplo.
`configure` aporta normalmente `PACKAGE_STRING`; como aquí no se usó, se define a mano.

```bash
SRC="calculations.c geometry.c input.c matrix.c network.c shared.c fields.c ground.c main.c misc.c radiation.c somnec.c"
D='-DPACKAGE_STRING="nec2c 1.3"'

gcc -O2 -w "$D" -o nec2c_std  $SRC -lm
gcc -O2 -w "$D" -DNEC2C_PORTABLE -o nec2c_port $SRC -lm

./nec2c_std  -v
./nec2c_port -v

./nec2c_std  -i Input/3E_.NEC -o out_std.txt
./nec2c_port -i Input/3E_.NEC -o out_port.txt

diff <(grep -v -i -E "time|sec" out_std.txt) <(grep -v -i -E "time|sec" out_port.txt)
```

Resultado: ambas imprimen `nec2c 1.3`, terminan con código 0 y el `diff` no muestra diferencias.

## 5. Compilar en Windows (GitHub Actions)

El workflow [`.github/workflows/build-win64.yml`](../.github/workflows/build-win64.yml) usa MSYS2 UCRT64 y ejecuta:

```bash
gcc -O2 -static -Wl,--no-insert-timestamp -DPACKAGE_STRING='"nec2c 1.3"' -o nec2c.exe \
  calculations.c geometry.c input.c matrix.c network.c shared.c fields.c \
  ground.c main.c misc.c radiation.c somnec.c -lm
objdump -p nec2c.exe | grep -E "DLL Name|Characteristics|Magic"
sha256sum nec2c.exe
```

Luego prueba el ejecutable desde **CMD**, sin MSYS2 en el PATH, para detectar DLL faltantes:

```bat
nec2c.exe -v
nec2c.exe -i Input\3E_.NEC -o smoke_test_3E_output.txt
echo exit code: %ERRORLEVEL%
```

Finalmente sube `nec2c.exe`, `nec2c.exe.sha256`, `dlls.txt` y `smoke_test_3E_output.txt` como artefacto y como Release `v1.3-win64`.
Se puede lanzar a mano desde la pestaña *Actions* con *Run workflow*.

## 6. Compilar en tu PC (MSYS2 UCRT64)

Abre la terminal **MSYS2 UCRT64** (no la MSYS ni la MINGW64):

```bash
pacman -Syu                                           # si pide cerrar la terminal, ciérrala y ábrela de nuevo
pacman -S --needed git mingw-w64-ucrt-x86_64-gcc
git clone https://github.com/sergiozxp/nec2c-windows
cd nec2c-windows
gcc -O2 -static -Wl,--no-insert-timestamp -DPACKAGE_STRING='"nec2c 1.3"' -o nec2c.exe \
  calculations.c geometry.c input.c matrix.c network.c shared.c fields.c \
  ground.c main.c misc.c radiation.c somnec.c -lm
./nec2c.exe -v
```

Luego, en el **CMD de Windows** (no en MSYS2), dentro de la carpeta donde dejes `nec2c.exe`:

```bat
nec2c.exe -v
nec2c.exe -i examples\dipolo_20m.nec -o dipolo_20m.txt
```

Si Windows dice que falta una DLL, el ejecutable no quedó independiente: revisa que la compilación usara `-static`.

## 7. Comprobar una descarga del Release

```bash
curl -L -O https://github.com/sergiozxp/nec2c-windows/releases/download/v1.3-win64/nec2c.exe
curl -L -O https://github.com/sergiozxp/nec2c-windows/releases/download/v1.3-win64/nec2c.exe.sha256
sha256sum nec2c.exe          # en Windows: certutil -hashfile nec2c.exe SHA256
cat nec2c.exe.sha256
```

Las dos huellas deben coincidir. En el último ejecutable publicado, el archivo `dlls.txt` del Release lista solo `KERNEL32.dll` y las `api-ms-win-crt-*`.

## 8. Cómo se armó este repositorio

```bash
# commit 1: código importado sin cambios (git archive del commit 55be1e0)
# commit 2: parche de portabilidad + workflow
# commit 3: documentación
git push -u origin main
```

El push a `main` lanza el workflow, salvo que solo cambien archivos `.md` o `examples/`.
