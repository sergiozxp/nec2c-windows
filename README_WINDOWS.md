# nec2c para Windows de 64 bits

Compilación de `nec2c` 1.3 (Neoklis Kyriazis, 5B4AZ) a partir de
[KJ7LNW/nec2c](https://github.com/KJ7LNW/nec2c) @ `55be1e0`.

- Un único commit de importación sin modificaciones, y un segundo commit con un parche mínimo
  de portabilidad (`sigaction` → `signal`, `times` → `clock`). En Linux el comportamiento no cambia.
- El ejecutable se genera con GitHub Actions (`windows-latest`, MSYS2 UCRT64, `gcc -static`)
  y se publica en la sección *Releases* con su SHA-256.
- Uso: `nec2c.exe -i entrada.nec -o salida.txt`
