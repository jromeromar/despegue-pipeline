#!/usr/bin/env python3
"""Calcula la nota /100 y su letra desde la madurez, y la escribe en el diagnóstico.
Uso: python3 calcular_nota.py diagnostico.json
Modifica el archivo en sitio (campo "nota") e imprime el resultado.
La nota NUNCA se calcula a mano ni con el modelo: siempre con este script."""
import json, sys

MODULOS = 7
NIVEL_MAX = 4

def letra(p):
    return 'A' if p >= 85 else 'B' if p >= 70 else 'C' if p >= 55 else \
           'D' if p >= 40 else 'E' if p >= 25 else 'F'

def calcular(diag):
    mad = diag.get('madurez', [])
    if len(mad) != MODULOS:
        raise SystemExit(f"✖ madurez tiene {len(mad)} módulos, deben ser {MODULOS}")
    for m in mad:
        if m.get('hoy') not in range(NIVEL_MAX + 1):
            raise SystemExit(f"✖ nivel inválido en {m.get('m')}: {m.get('hoy')}")
    puntos = round(sum(m['hoy'] for m in mad) / (MODULOS * NIVEL_MAX) * 100)
    return {'puntos': puntos, 'letra': letra(puntos)}

if __name__ == '__main__':
    ruta = sys.argv[1]
    diag = json.load(open(ruta))
    diag['nota'] = calcular(diag)
    json.dump(diag, open(ruta, 'w'), ensure_ascii=False, indent=1)
    print(f"✔ nota: {diag['nota']['puntos']}/100 → {diag['nota']['letra']} (escrita en {ruta})")
