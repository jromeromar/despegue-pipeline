#!/usr/bin/env python3
"""Validador de propuesta.json — criterios automáticos de la skill seleccion-propuesta.
Uso: python3 validar_propuesta.py propuesta.json componentes.json [diagnostico.json]
Exit 0 = pasa. Es también la compuerta de entrada del renderizador."""
import json, sys, re

ORDEN = {'fundamental': 1, 'avanzado': 2, 'inteligente': 3}

def validar(p, lib, diag=None):
    E, W = [], []
    comps_lib = lib.get('componentes', lib)

    # ---------- 0. Modo de validación: completa o histórica (contrato v0.4) ----------
    # Una corrección de la librería (dividir o renombrar un componente) deja a las
    # propuestas ya emitidas apuntando a ids que ya no existen. Esas propuestas no se
    # editan (regla 7 de la casa), así que la validación las reconoce como históricas
    # en vez de fallar: estructura, aritmética y herencia sí; ids contra la librería, no.
    hash_lib = (lib.get('_meta') or {}).get('version')
    hash_prop = p.get('libreria_hash')
    ver_c = tuple(int(n) for n in re.findall(r'\d+', str(p.get('_contrato', '')))[:2])
    historica = False
    if hash_prop and hash_lib and hash_prop != hash_lib:
        historica = True
        W.append(f"0h · PROPUESTA HISTÓRICA: emitida contra la librería {hash_prop} y validada contra "
                 f"{hash_lib} — se valida estructura, aritmética y herencia, no los ids contra la "
                 "librería nueva. Si su alcance sigue vigente, se emite -v2 (regla 7: la vieja no se edita)")
    elif not hash_prop:
        if ver_c >= (0, 4):
            E.append("0a · sin libreria_hash y la propuesta se declara v0.4+: la skill de selección debe "
                     "escribirlo al emitir, copiado del _meta.version de la librería compilada que usó")
        else:
            historica = True
            W.append(f"0h · PROPUESTA HISTÓRICA: sin libreria_hash y contrato anterior a v0.4 — se emitió "
                     f"antes de que el campo existiera. Validada contra la librería {hash_lib or '(sin hash)'}: "
                     "estructura, aritmética y herencia solamente")
    # en modo histórico los hallazgos contra la librería informan, no bloquean
    LIB = W if historica else E

    # ---------- 1. Componentes contra la librería ----------
    sel = p.get('componentes', {})
    if not sel: E.append("1a · cero componentes seleccionados")
    for cid, c in sel.items():
        if cid not in comps_lib:
            LIB.append(f"1b · '{cid}' no existe en la librería compilada")
            continue
        ref = comps_lib[cid]
        pm = ref.get('plan_minimo')
        if pm is None:
            LIB.append(f"1c · '{cid}' tiene plan_minimo null en la librería: V11 — va al carril, no al plan")
        elif ORDEN.get(c.get('plan'), 0) < ORDEN.get(pm, 9):
            LIB.append(f"1d · '{cid}' vendido en {c.get('plan')} pero su plan mínimo es {pm}")
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

    # ---------- 9. as_is: la cifra tiene campo, no se escarba de la prosa ----------
    # Un rango unido por guion es UNA cifra ("20–30"); unido por palabras son dos.
    NUM = re.compile(r'\d+(?:[.,]\d+)*(?:\s*[-\u2013\u2014]\s*\d+(?:[.,]\d+)*)?')
    def _norm(x):
        return re.sub(r'\s+', '', str(x).replace('\u2013', '-').replace('\u2014', '-'))
    a = p.get('as_is')
    if not isinstance(a, dict) or not a:
        E.append("9a · sin bloque as_is: la sección 1b del lienzo no tiene de dónde salir")
        a = {}
    for carril in ('de_donde_llegan', 'por_donde_pasan', 'donde_queda'):
        filas = a.get(carril)
        if not isinstance(filas, list) or not filas:
            E.append(f"9b · as_is sin el carril '{carril}' (o vacío)")
            continue
        for fila in filas:
            if not isinstance(fila, list) or not 2 <= len(fila) <= 3:
                E.append(f"9c · fila de as_is.{carril} mal formada — se espera "
                         f"[etiqueta, nota] o [etiqueta, nota, {{cifra, unidad}}]: {fila}")
                continue
            etiqueta, nota = fila[0], fila[1]
            if not str(etiqueta).strip() or not str(nota).strip():
                E.append(f"9d · fila de as_is.{carril} con etiqueta o nota vacía: {fila}")
                continue
            tokens = NUM.findall(str(nota))
            if len(tokens) > 1:
                E.append(f"9e · nota de as_is.{carril} con {len(tokens)} cifras {tokens}: el lienzo no "
                         f"puede saber cuál destacar — dejar una sola en la nota (o partir la fila) y "
                         f"declararla en el tercer elemento · «{nota}»")
            if len(fila) == 2:
                if tokens:
                    W.append(f"9f · as_is.{carril} · «{nota}» trae la cifra {tokens[0]} en la prosa pero la "
                             f"fila no la declara: el lienzo no la destacará (agregar "
                             f'{{"cifra": "{tokens[0]}", "unidad": "…"}} como tercer elemento)')
                continue
            dato = fila[2]
            if not isinstance(dato, dict):
                E.append(f"9g · tercer elemento de as_is.{carril} · «{etiqueta}» no es un objeto "
                         f'{{"cifra", "unidad"}}: {dato!r}')
                continue
            sobra = sorted(set(dato) - {'cifra', 'unidad'})
            if sobra:
                E.append(f"9h · dato destacado de as_is.{carril} · «{etiqueta}» con campos no contratados: {sobra}")
            cifra, unidad = dato.get('cifra'), dato.get('unidad')
            if not isinstance(cifra, str) or not cifra.strip():
                E.append(f"9i · dato destacado de as_is.{carril} · «{etiqueta}» sin 'cifra' de texto "
                         f"no vacío (se copia de la nota, no se calcula): {dato}")
            elif _norm(cifra) not in _norm(nota):
                E.append(f"9j · la cifra '{cifra}' de as_is.{carril} · «{etiqueta}» no aparece en su nota "
                         f"«{nota}»: el número del lienzo debe ser trazable a la frase que lo respalda")
            if not isinstance(unidad, str) or not unidad.strip():
                E.append(f"9k · dato destacado de as_is.{carril} · «{etiqueta}» sin 'unidad': un número "
                         f"suelto en el lienzo no dice nada ({dato})")

    # ---------- 10. Estado de los nombres propios (heredado de la etapa 1) ----------
    # Que un nombre siga por confirmar NO invalida la propuesta: a veces se presenta
    # sabiendo que falta confirmar. Lo que no puede pasar es presentarla sin saberlo.
    ver_p = tuple(int(n) for n in re.findall(r'\d+', str(p.get('_contrato','')))[:2])
    v03_p = ver_p >= (0, 3)
    ESTADOS_G = ('confirmada', 'por_confirmar')
    cli = p.get('cliente')
    cli_txt = cli if isinstance(cli, str) else (cli.get('nombre') if isinstance(cli, dict) else str(cli))
    if not isinstance(cli, str):
        W.append(f"10h · 'cliente' no es texto sino {type(cli).__name__} y el contrato dice str "
                 "(schema-propuesta.md): decidir si el contrato gana esos campos o el archivo los pierde — "
                 "el estado de la grafía viaja aparte en cliente_grafia_estado, no dentro de 'cliente'")
    est_cli = p.get('cliente_grafia_estado')
    if est_cli is None:
        (E if v03_p else W).append(
            "10a · sin cliente_grafia_estado: el estado de la grafía se hereda de la ficha "
            "(contrato v0.3) — sin él nadie sabe si el nombre del cliente está confirmado")
    elif est_cli not in ESTADOS_G:
        E.append(f"10b · cliente_grafia_estado inválido {est_cli!r} — solo 'confirmada' o 'por_confirmar'")
    elif est_cli == 'por_confirmar':
        W.append(f"10c · la propuesta sale con el nombre del cliente ({cli_txt!r}) SIN CONFIRMAR: "
                 "revisar la grafía antes de presentarla — se imprime en el lienzo que el cliente lee")

    pend = p.get('nombres_por_confirmar')
    if pend is None:
        (E if v03_p else W).append("10d · sin nombres_por_confirmar (contrato v0.3): usar [] si están todos confirmados")
    elif not isinstance(pend, list):
        E.append(f"10e · nombres_por_confirmar no es una lista ({type(pend).__name__})")
    else:
        for fila in pend:
            if not isinstance(fila, list) or len(fila) != 2 or not all(str(x).strip() for x in fila):
                E.append(f"10f · fila de nombres_por_confirmar mal formada — se espera [que_es, grafia]: {fila}")
        if pend:
            listado = ' · '.join(f"{f[0]}: {f[1]}" for f in pend if isinstance(f, list) and len(f) == 2)
            W.append(f"10g · {len(pend)} nombre(s) propio(s) que esta propuesta imprime siguen sin confirmar "
                     f"({listado}): se corrigen en la ficha y se rehace la cadena, nunca a mano aquí")

    # ---------- 11. Campos de librería que el renderizador exige por componente ----------
    # El contrato los declara obligatorios (schema-propuesta.md §componentes) y hasta
    # ago-2026 NADIE los verificaba aquí. Costó una carga fallida completa: la propuesta
    # de Bifteki salió con exit 0 y los 56 componentes con 'vis' y 'journey' en null, y el
    # renderizador la rechazó entera con 112 errores.
    #
    # Causa raíz: la librería compilada guarda estos campos con nombre largo
    # ('visibilidad_cliente', 'posicion_journey') y el contrato de la propuesta los espera
    # con nombre corto ('vis', 'journey'). Quien arma la propuesta tiene que traducirlos, y
    # si lee la clave equivocada obtiene null sin que nada se queje. El mapeo canónico vive
    # en scripts/construir_propuesta.py (MAPA_LIBRERIA); esto es la red que lo respalda.
    VIS_OK = {'front', 'back', 'ambos'}
    for cid, c in sel.items():
        ref = comps_lib.get(cid, {})
        v = c.get('vis')
        if v not in VIS_OK:
            E.append(f"11a · '{cid}' con vis {v!r}: el renderizador espera uno de "
                     f"{sorted(VIS_OK)} — en la librería ese campo se llama 'visibilidad_cliente'")
        elif ref and ref.get('visibilidad_cliente') not in (None, v):
            E.append(f"11c · '{cid}' con vis {v!r} pero la librería dice "
                     f"{ref.get('visibilidad_cliente')!r}: la propuesta no reescribe la librería")
        j = c.get('journey')
        if not isinstance(j, int) or isinstance(j, bool):
            E.append(f"11b · '{cid}' con journey {j!r}: se espera un entero — en la "
                     "librería ese campo se llama 'posicion_journey'")
        elif ref and ref.get('posicion_journey') not in (None, j):
            E.append(f"11d · '{cid}' con journey {j!r} pero la librería dice "
                     f"{ref.get('posicion_journey')!r}: la propuesta no reescribe la librería")
        if not str(c.get('nombre_cliente', '')).strip():
            W.append(f"11e · '{cid}' sin nombre_cliente: el lienzo dibujaría una pieza sin título")

    return E, W

if __name__ == '__main__':
    p = json.load(open(sys.argv[1]))
    lib = json.load(open(sys.argv[2]))
    diag = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
    E, W = validar(p, lib, diag)
    for e in E: print("✖", e)
    for w in W: print("⚠", w)
    hist = " (histórica)" if any(w.startswith("0h ·") for w in W) else ""
    print((f"✔ propuesta válida{hist}" + (f" · {len(W)} advertencias" if W else " sin observaciones"))
          if not E else f"✖ {len(E)} errores")
    sys.exit(1 if E else 0)
