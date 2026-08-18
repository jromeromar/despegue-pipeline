#!/usr/bin/env python3
"""Validador de propuesta.json — criterios automáticos de la skill seleccion-propuesta.
Uso: python3 validar_propuesta.py propuesta.json componentes.json [diagnostico.json]
Exit 0 = pasa. Es también la compuerta de entrada del renderizador."""
import json, sys, re

ORDEN = {'fundamental': 1, 'avanzado': 2, 'inteligente': 3}

def validar(p, lib, diag=None):
    E, W = [], []
    comps_lib = lib.get('componentes', lib)

    # ---------- 1. Componentes contra la librería ----------
    sel = p.get('componentes', {})
    if not sel: E.append("1a · cero componentes seleccionados")
    for cid, c in sel.items():
        if cid not in comps_lib:
            E.append(f"1b · '{cid}' no existe en la librería compilada")
            continue
        ref = comps_lib[cid]
        pm = ref.get('plan_minimo')
        if pm is None:
            E.append(f"1c · '{cid}' tiene plan_minimo null en la librería: V11 — va al carril, no al plan")
        elif ORDEN.get(c.get('plan'), 0) < ORDEN.get(pm, 9):
            E.append(f"1d · '{cid}' vendido en {c.get('plan')} pero su plan mínimo es {pm}")
        if not isinstance(c.get('instancias'), int) or c['instancias'] < 1:
            E.append(f"1e · '{cid}' con instancias inválidas: {c.get('instancias')}")

    # ---------- 2. Exclusiones con razón ----------
    na = p.get('no_aplican', [])
    if not na: W.append("2a · no_aplican vacío: una selección sin exclusiones es sospechosa (¿aplica_si evaluado?)")
    for fila in na:
        if len(fila) < 2 or not str(fila[1]).strip():
            E.append(f"2b · exclusión sin razón: {fila}")
        if len(fila) > 1 and re.match(r'^[a-z]+(-[a-z0-9]+)+$', str(fila[0])):
            E.append(f"2c · exclusión con id interno visible al cliente: '{fila[0]}' — usar nombre_cliente")

    # ---------- 3. Carril de integraciones ----------
    ETIQ = {'incluido', 'consumo_variable', 'licencia_del_cliente', 'desarrollo_a_cotizar'}
    for fila in p.get('integraciones', []):
        if len(fila) < 3 or fila[2] not in ETIQ:
            E.append(f"3 · integración sin etiqueta de costo válida: {fila[:1]}")

    # ---------- 4. Multiplicador aritmético ----------
    mult = p.get('multiplicador_calculado', {})
    for plan in ('1', '2', '3'):
        if plan not in mult:
            E.append(f"4a · multiplicador sin plan {plan}")
            continue
        act = [c for c in sel.values() if ORDEN.get(c.get('plan'), 9) <= int(plan)]
        piezas, config = len(act), sum(c.get('instancias', 0) for c in act)
        if mult[plan].get('piezas') != piezas or mult[plan].get('config') != config:
            E.append(f"4b · multiplicador plan {plan} dice {mult[plan]}, la selección da "
                     f"{{'piezas': {piezas}, 'config': {config}}}")

    # ---------- 5. Precio verificable ----------
    cc = p.get('condicion_comercial', {})
    base, tramos, precio = cc.get('base_por_plan', {}), cc.get('tramos_factor', []), cc.get('precio_por_plan', {})
    if not (base and tramos and precio):
        E.append("5a · condicion_comercial incompleta (base, tramos o precio)")
    else:
        def factor(r):
            for lim, f in tramos:
                if r <= lim: return f
            return tramos[-1][1]
        for plan in ('1', '2', '3'):
            if plan in mult and mult[plan].get('piezas'):
                r = mult[plan]['config'] / mult[plan]['piezas']
                esperado = round(base[plan] * factor(r))
                if precio.get(plan) != esperado:
                    E.append(f"5b · precio plan {plan} dice {precio.get(plan)}, base×factor da {esperado}")

    # ---------- 6. Herencia sin edición ----------
    if diag:
        if p.get('modo') != diag.get('modo'):
            E.append(f"6a · modo editado: diagnóstico {diag.get('modo')} vs propuesta {p.get('modo')}")
        f_diag = {f['id'] for f in diag.get('fugas', [])}
        f_prop = {f.get('id') for f in p.get('fugas', [])}
        if f_diag != f_prop:
            E.append(f"6b · fugas editadas: diagnóstico {sorted(f_diag)} vs propuesta {sorted(f_prop)}")
        m_diag = {m['m']: m['hoy'] for m in diag.get('madurez', [])}
        for m in p.get('madurez', []):
            if m['m'] in m_diag and m.get('hoy') != m_diag[m['m']]:
                E.append(f"6c · madurez de {m['m']} editada: {m_diag[m['m']]} → {m.get('hoy')}")

    # ---------- 7. Pureza: datos, no presentación ----------
    txt = json.dumps(p, ensure_ascii=False)
    if re.search(r'<[a-z]+[ >]', txt): E.append("7a · la propuesta contiene HTML")
    if re.search(r'#[0-9A-Fa-f]{6}\b', txt): E.append("7b · la propuesta contiene colores hex")
    if 'class=' in txt or 'px' in re.sub(r'\bpx\b(?![^"]*")', '', '') and 'style=' in txt:
        E.append("7c · la propuesta contiene markup de presentación")

    # ---------- 8. Advertencias mínimas ----------
    advs = ' '.join(p.get('advertencias', [])).lower()
    if 'copy' not in advs and 'texto' not in advs:
        W.append("8 · las advertencias no incluyen la regla global del copy (el cliente aprueba todo texto)")

    return E, W

if __name__ == '__main__':
    p = json.load(open(sys.argv[1]))
    lib = json.load(open(sys.argv[2]))
    diag = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
    E, W = validar(p, lib, diag)
    for e in E: print("✖", e)
    for w in W: print("⚠", w)
    print(("✔ propuesta válida" + (f" · {len(W)} advertencias" if W else " sin observaciones")) if not E else f"✖ {len(E)} errores")
    sys.exit(1 if E else 0)
