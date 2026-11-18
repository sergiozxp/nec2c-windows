"""Lector tolerante de la salida de nec2c (y de otros motores NEC-2).

Uso:  python leer_salida.py salida.txt

Extrae, por cada frecuencia: la frecuencia (MHz), la impedancia de entrada y la tabla de ganancias.
No depende de espacios exactos ni de si la línea de frecuencia usa ':' o '='.
"""
import re
import sys

NUM = r"[-+]?\d+\.?\d*(?:[Ee][-+]?\d+)?"
RE_FREQ = re.compile(rf"FREQUENCY\s*[:=]\s*({NUM})\s*MHz", re.I)
RE_NUM = re.compile(NUM)
RE_FILA = re.compile(rf"^\s*{NUM}\s")   # una fila de datos empieza con un número


def numeros(linea):
    return [float(x) for x in RE_NUM.findall(linea)]


def leer(texto):
    """Devuelve una lista con un diccionario por frecuencia encontrada."""
    bloques, actual, modo = [], None, None
    for linea in texto.splitlines():
        m = RE_FREQ.search(linea)
        if m:
            actual = {"f_mhz": float(m.group(1)), "z_ohm": None, "patron": []}
            bloques.append(actual)
            modo = None
            continue
        if actual is None:
            continue
        u = linea.upper()
        if "ANTENNA INPUT PARAMETERS" in u:
            modo = "z"
        elif "RADIATION PATTERNS" in u:
            modo = "patron"
        elif modo == "z" and RE_FILA.match(linea):
            n = numeros(linea)
            if len(n) >= 8 and actual["z_ohm"] is None:   # tag, seg, V(2), I(2), Z(2), Y(2), potencia
                actual["z_ohm"] = complex(n[6], n[7])
        elif modo == "patron" and RE_FILA.match(linea):
            n = numeros(linea)
            if len(n) >= 5:                                # theta, phi, vertical, horizontal, total, ...
                actual["patron"].append(
                    {"theta": n[0], "phi": n[1], "vert_db": n[2], "horiz_db": n[3], "total_db": n[4]}
                )
    return bloques


if __name__ == "__main__":
    with open(sys.argv[1], encoding="latin-1") as fh:
        for b in leer(fh.read()):
            mejor = max(b["patron"], key=lambda p: p["total_db"]) if b["patron"] else None
            print(f"f = {b['f_mhz']} MHz   Z = {b['z_ohm']}   puntos de patrón = {len(b['patron'])}")
            if mejor:
                print(f"   ganancia máxima = {mejor['total_db']} dB en theta = {mejor['theta']}, phi = {mejor['phi']}")
