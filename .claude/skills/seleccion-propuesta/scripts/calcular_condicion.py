#!/usr/bin/env python3
"""Calcula TODO lo numérico de la etapa 3 y lo escribe en la propuesta:
instancias por componente, multiplicador por plan, factor por tramos y precios.
Uso: python3 calcular_condicion.py propuesta.json ficha.json
Estos números NUNCA se calculan a mano ni con el modelo: siempre con este script.
El modelo decide QUÉ aplica (aplica_si es semántico); este script decide CUÁNTO."""
import json, sys, re

ORDEN = {'fundamental': 1, 'avanzado': 2, 'inteligente': 3}

def ejes_desde_ficha(ficha):
    E = ficha.get('E_multiplicadores', {})
    lineas_comerciales = [l for l in ficha.get('A_lineas_de_negocio', [])
                          if l.get('sujeto_del_embudo') in ('demandante', 'oferente')]
    return {
        'linea_negocio': int(E.get('lineas_de_negocio') or len(lineas_comerciales) or 1),
        'linea_comercial': max(1, len(lineas_comerciales)),
        'sujeto_del_embudo': int(E.get('sujetos_del_embudo') or 1),
        'mecanismo': int(E.get('mecanismos_de_cierre') or 1),
        'territorio': 2 if str(E.get('territorio', '')).startswith('nacional') else 1,
        'funcion': max(1, len({p.get('funcion') for p in
                               ficha.get('B_estructura', {}).get('personas_declaradas', [])})),
        'unico': 1,
    }

def instancias_de(inst_por, ejes):
    """se_instancia_por es una lista de ejes: el resultado es el MAYOR eje aplicable
    (no el producto: un pipeline por línea no se multiplica además por territorio)."""
    claves = re.findall(r'[a-z_]+', str(inst_por or 'unico'))
    valores = [ejes.get(k, 1) for k in claves] or [1]
    return max(valores)

def calcular(prop, ficha):
    ejes = ejes_desde_ficha(ficha)
    ajustes_manuales = []
    for cid, c in prop.get('componentes', {}).items():
        calculado = instancias_de(c.get('inst_por'), ejes)
        if c.get('instancias_fijadas_por_consultor'):
            ajustes_manuales.append(f"{cid}: consultor fijó {c['instancias']} (cálculo daba {calculado})")
        else:
            c['instancias'] = calculado
    # multiplicador por plan — derivado de la selección, único lugar donde se calcula
    mult = {}
    for plan in (1, 2, 3):
        act = [c for c in prop['componentes'].values() if ORDEN.get(c.get('plan'), 9) <= plan]
        mult[str(plan)] = {'piezas': len(act), 'config': sum(c['instancias'] for c in act)}
    prop['multiplicador_calculado'] = mult
    # precios por tramos
    cc = prop.setdefault('condicion_comercial', {})
    base, tramos = cc.get('base_por_plan'), cc.get('tramos_factor')
    if not base or not tramos:
        raise SystemExit("✖ condicion_comercial sin base_por_plan o tramos_factor: son política de negocio, no se inventan")
    def factor(r):
        for lim, f in tramos:
            if r <= lim: return f
        return tramos[-1][1]
    cc['precio_por_plan'] = {}
    detalle = []
    for plan in ('1', '2', '3'):
        m = mult[plan]
        r = m['config'] / m['piezas'] if m['piezas'] else 0
        f = factor(r)
        cc['precio_por_plan'][plan] = round(base[plan] * f)
        detalle.append(f"plan {plan}: {m['piezas']} piezas · {m['config']} config · "
                       f"complejidad {r:.2f} → factor ×{f} → {cc['precio_por_plan'][plan]} {cc.get('moneda','USD')}")
    return detalle, ajustes_manuales, ejes

if __name__ == '__main__':
    prop = json.load(open(sys.argv[1]))
    ficha = json.load(open(sys.argv[2]))
    detalle, ajustes, ejes = calcular(prop, ficha)
    json.dump(prop, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
    print("✔ ejes:", ejes)
    for d in detalle: print("  ", d)
    for a in ajustes: print("  ⚑ ajuste manual respetado —", a)
    print(f"✔ instancias, multiplicador y precios escritos en {sys.argv[1]}")
