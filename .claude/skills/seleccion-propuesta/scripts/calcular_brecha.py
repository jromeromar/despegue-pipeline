#!/usr/bin/env python3
"""Escribe los PUNTOS de brecha_fuera_de_alcance (C6, contrato v0.5).
Uso: python3 calcular_brecha.py propuesta.json
Regla de la casa: el modelo decide QUÉ (los textos por_que/responsable/
que_puede_hacer), Python decide CUÁNTO (los puntos). Este script:
- deriva el techo del plan recomendado desde madurez[].p;
- si el techo es 100, ELIMINA el bloque entero (el contrato lo omite);
- si es < 100, escribe global.puntos y por_modulo[].puntos con la aritmética
  déficit × 100/28 y redondeo por resto mayor (la suma siempre cuadra);
- exige que los textos de cada módulo con déficit ya existan: los puntos son
  del script, las razones son del consultor."""
import json, sys

MODULOS = ["Gestión","Atracción","Nutrición","Cierre","Reactivación","Referidos y Fidelización","Tableros"]

def calcular(prop):
    plan = str((prop.get('plan_recomendado') or {}).get('plan') or '')
    if plan not in ('1', '2', '3'):
        raise SystemExit("✖ sin plan_recomendado.plan: la brecha se calcula contra el plan recomendado")
    p = {}
    for m in prop.get('madurez', []):
        nivel = (m.get('p') or {}).get(plan)
        if nivel is None:
            raise SystemExit(f"✖ madurez de {m.get('m')} sin p['{plan}']: no hay techo que calcular")
        p[m['m']] = nivel
    if set(p) != set(MODULOS):
        raise SystemExit(f"✖ madurez incompleta: {sorted(set(MODULOS) - set(p))}")

    techo = round(sum(p.values()) / (len(MODULOS) * 4) * 100)
    if techo >= 100:
        if 'brecha_fuera_de_alcance' in prop:
            del prop['brecha_fuera_de_alcance']
            return techo, 'el plan recomendado llega a 100: bloque eliminado (el contrato lo omite entero)'
        return techo, 'el plan recomendado llega a 100: sin brecha'

    total = 100 - techo
    defi = {m: 4 - p[m] for m in MODULOS if 4 - p[m] > 0}
    raw = {m: d * 100 / 28 for m, d in defi.items()}
    pts = {m: int(raw[m]) for m in raw}
    for m in sorted(raw, key=lambda m: (-(raw[m] - int(raw[m])), MODULOS.index(m)))[:max(total - sum(pts.values()), 0)]:
        pts[m] += 1

    br = prop.setdefault('brecha_fuera_de_alcance', {})
    g = br.setdefault('global', {})
    g['puntos'] = total
    if not str(g.get('por_que', '')).strip():
        raise SystemExit("✖ brecha global sin por_que: el texto es del consultor, el script solo pone los puntos")
    filas = {f.get('m'): f for f in br.get('por_modulo', [])}
    faltan_texto = [m for m in pts if m not in filas]
    if faltan_texto:
        raise SystemExit(f"✖ módulos con déficit sin texto de brecha (por_que/responsable/que_puede_hacer): "
                         f"{faltan_texto} — el consultor los redacta y el script pone los puntos")
    sobran = [m for m in filas if m not in pts]
    if sobran:
        raise SystemExit(f"✖ módulos en la brecha sin déficit en el plan {plan}: {sobran}")
    br['por_modulo'] = []
    for m in MODULOS:
        if m in pts:
            fila = filas[m]
            fila['puntos'] = pts[m]
            br['por_modulo'].append(fila)
    return techo, f"techo plan {plan} = {techo} · brecha {total} pts · {pts}"

if __name__ == '__main__':
    prop = json.load(open(sys.argv[1]))
    techo, msg = calcular(prop)
    json.dump(prop, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
    print(f"✔ {msg} — escrito en {sys.argv[1]}")
