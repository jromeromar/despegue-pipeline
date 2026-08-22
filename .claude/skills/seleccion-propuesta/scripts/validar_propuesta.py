#!/usr/bin/env python3
"""Validador de propuesta.json — criterios automáticos de la skill seleccion-propuesta.
Uso: python3 validar_propuesta.py propuesta.json componentes.json [diagnostico.json]
Exit 0 = pasa. Es también la compuerta de entrada del renderizador.
Las propuestas con _contrato anterior a v0.5 se validan con las reglas de su
versión (el contrato no se reescribe hacia atrás)."""
import json, sys, re, unicodedata

ORDEN = {'fundamental': 1, 'avanzado': 2, 'inteligente': 3}
MODULOS = ["Gestión","Atracción","Nutrición","Cierre","Reactivación","Referidos y Fidelización","Tableros"]
FRONTERAS = {   # invariantes — matriz-fronteras.md v1.1, filas «Frase» y «El sistema actúa…»
    '1': "Nada se pierde: el sistema actúa cuando alguien del equipo actúa.",
    '2': "El sistema trabaja: actúa cuando el cliente final actúa.",
    '3': "El sistema persigue y decide: actúa cuando nadie actúa.",
}
STOP = {'para','como','cada','este','esta','estos','estas','donde','entre','hacia',
        'sobre','desde','hasta','pero','porque','cuando','todo','toda','todos','todas',
        'solo','sola','con','sin','por','que','una','uno','unos','unas','los','las',
        'del','sus','mas','más','muy','aqui','aquí','hoy'}

def _plano(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')

def brecha_esperada(mad, plan):
    """Misma aritmética de calcular_brecha.py: déficit×100/28, resto mayor."""
    p = {m['m']: m.get('p', {}).get(str(plan)) for m in mad}
    if any(v is None for v in p.values()) or set(p) != set(MODULOS): return None
    techo = round(sum(p.values()) / (len(MODULOS) * 4) * 100)
    defi = {m: 4 - p[m] for m in MODULOS if 4 - p[m] > 0}
    total = 100 - techo
    raw = {m: d * 100 / 28 for m, d in defi.items()}
    pts = {m: int(raw[m]) for m in raw}
    resto = total - sum(pts.values())
    for m in sorted(raw, key=lambda m: (-(raw[m] - int(raw[m])), MODULOS.index(m)))[:max(resto, 0)]:
        pts[m] += 1
    return techo, total, pts

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
    v05 = ver_c >= (0, 5)
    pi = p.get('panel_interno') if isinstance(p.get('panel_interno'), dict) else {}

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
    for cid, c in sel.items():
        if not isinstance(c.get('instancias'), int) or c['instancias'] < 1:
            E.append(f"1e · '{cid}' con instancias inválidas: {c.get('instancias')}")

    # ---------- 2. Exclusiones con razón (v0.5: viven en panel_interno) ----------
    na = pi.get('no_aplican', []) if v05 else p.get('no_aplican', [])
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

    # ---------- 4. Multiplicador aritmético (v0.5: vive en panel_interno) ----------
    mult = pi.get('multiplicador_calculado', {}) if v05 else p.get('multiplicador_calculado', {})
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

    # ---------- 8. Advertencias mínimas — y atomizadas (C10, v0.5) ----------
    advs_l = p.get('advertencias', [])
    advs = ' '.join(advs_l).lower()
    if 'copy' not in advs and 'texto' not in advs:
        W.append("8 · las advertencias no incluyen la regla global del copy (el cliente aprueba todo texto)")
    if v05:
        for a in advs_l:
            if not str(a).strip():
                E.append("8b · advertencia vacía")
            elif len(a) > 140:
                E.append(f"8c · advertencia de {len(a)} caracteres (máx 140, una sola idea — se parte): «{a[:60]}…»")

    # ---------- 9. as_is: la cifra tiene campo, no se escarba de la prosa ----------
    # Un rango unido por guion es UNA cifra ("20–30"); unido por palabras son dos.
    NUM = re.compile(r'\d+(?:[.,]\d+)*(?:\s*[-\u2013\u2014]\s*\d+(?:[.,]\d+)*)?')
    def _norm(x):
        return re.sub(r'\s+', '', str(x).replace('\u2013', '-').replace('\u2014', '-'))
    def _chequear_dato(carril, etiqueta, nota, dato):
        if not isinstance(dato, dict):
            E.append(f"9g · dato destacado de as_is.{carril} · «{etiqueta}» no es un objeto "
                     f'{{"cifra", "unidad"}}: {dato!r}')
            return
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
    def _chequear_nota(carril, etiqueta, nota, declara):
        tokens = NUM.findall(str(nota))
        if len(tokens) > 1:
            E.append(f"9e · nota de as_is.{carril} con {len(tokens)} cifras {tokens}: el lienzo no "
                     f"puede saber cuál destacar — dejar una sola en la nota (o partir la fila) y "
                     f"declararla en el dato destacado · «{nota}»")
        if not declara and tokens:
            W.append(f"9f · as_is.{carril} · «{nota}» trae la cifra {tokens[0]} en la prosa pero la "
                     f"fila no la declara: el lienzo no la destacará (agregar "
                     f'{{"cifra": "{tokens[0]}", "unidad": "…"}} como dato destacado)')
    a = p.get('as_is')
    if not isinstance(a, dict) or not a:
        E.append("9a · sin bloque as_is: la sección 1b del lienzo no tiene de dónde salir")
        a = {}
    for carril in ('de_donde_llegan', 'donde_queda'):
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
            _chequear_nota(carril, etiqueta, nota, len(fila) == 3)
            if len(fila) == 3:
                _chequear_dato(carril, etiqueta, nota, fila[2])
    # por_donde_pasan: jerárquico desde v0.5 (C2); lista de pares/tríos antes
    filas_pp = a.get('por_donde_pasan')
    if not isinstance(filas_pp, list) or not filas_pp:
        E.append("9b · as_is sin el carril 'por_donde_pasan' (o vacío)")
        filas_pp = []
    for fila in filas_pp:
        if v05:
            if not isinstance(fila, dict):
                E.append(f"9l · fila de as_is.por_donde_pasan mal formada (contrato v0.5) — se espera "
                         f"{{quien, nota, detalle[]}}: {fila}")
                continue
            sobra = sorted(set(fila) - {'quien', 'nota', 'detalle', 'dato_destacado'})
            if sobra:
                E.append(f"9m · fila de as_is.por_donde_pasan con campos no contratados: {sobra}")
            quien, nota = fila.get('quien'), fila.get('nota')
            if not str(quien or '').strip() or not str(nota or '').strip():
                E.append(f"9d · fila de as_is.por_donde_pasan con quien o nota vacíos: {fila}")
                continue
            det = fila.get('detalle')
            if not isinstance(det, list) or any(not str(x).strip() for x in det):
                E.append(f"9n · as_is.por_donde_pasan · «{quien}» sin 'detalle' como lista de textos "
                         f"([] si no hay subítems): {det!r}")
            _chequear_nota('por_donde_pasan', quien, nota, 'dato_destacado' in fila)
            if 'dato_destacado' in fila:
                _chequear_dato('por_donde_pasan', quien, nota, fila['dato_destacado'])
        else:
            if not isinstance(fila, list) or not 2 <= len(fila) <= 3:
                E.append(f"9c · fila de as_is.por_donde_pasan mal formada: {fila}")
                continue
            etiqueta, nota = fila[0], fila[1]
            if not str(etiqueta).strip() or not str(nota).strip():
                E.append(f"9d · fila de as_is.por_donde_pasan con etiqueta o nota vacía: {fila}")
                continue
            _chequear_nota('por_donde_pasan', etiqueta, nota, len(fila) == 3)
            if len(fila) == 3:
                _chequear_dato('por_donde_pasan', etiqueta, nota, fila[2])

    # ---------- 10. Estado de los nombres propios (heredado de la etapa 1) ----------
    # Que un nombre siga por confirmar NO invalida la propuesta: a veces se presenta
    # sabiendo que falta confirmar. Lo que no puede pasar es presentarla sin saberlo.
    v03_p = ver_c >= (0, 3)
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

    if not v05:
        return E, W   # lo que sigue es contrato v0.5; a las históricas no se les exige

    # ---------- 11. resumen: {parrafo, bullets} sin repetir el as-is (C1) ----------
    res = p.get('resumen')
    if not isinstance(res, dict):
        E.append("11a · resumen debe ser {parrafo, bullets} desde v0.5 — la prosa suelta ya no es contrato")
        res = {}
    parrafo, bullets = res.get('parrafo'), res.get('bullets')
    if not isinstance(parrafo, str) or not parrafo.strip():
        E.append("11b · resumen.parrafo vacío o ausente")
    else:
        frases = [s for s in re.split(r'(?<=[.!?])\s+', parrafo.strip()) if s]
        if len(frases) > 3:
            E.append(f"11c · resumen.parrafo con {len(frases)} frases (máximo 3)")
    if not isinstance(bullets, list) or not 3 <= len(bullets) <= 4 or any(not str(b).strip() for b in bullets):
        E.append(f"11d · resumen.bullets debe ser una lista de 3 o 4 textos no vacíos, nunca más: {bullets!r}")
    # anti-redundancia dura: ningún token del as_is reaparece literal en el resumen
    tokens = set()
    def _tok_etiqueta(et, cifra=None):
        et_p = _plano(et).strip()
        if et_p: tokens.add(et_p)
        for w in re.findall(r'[a-z0-9\u00f1]{4,}', et_p):
            if w not in STOP: tokens.add(w)
        if cifra: tokens.add(_plano(cifra))
    for carril in ('de_donde_llegan', 'donde_queda'):
        for fila in a.get(carril, []) or []:
            if isinstance(fila, list) and len(fila) >= 2:
                _tok_etiqueta(fila[0], fila[2].get('cifra') if len(fila) == 3 and isinstance(fila[2], dict) else None)
    for fila in filas_pp:
        if isinstance(fila, dict):
            dd = fila.get('dato_destacado') or {}
            _tok_etiqueta(fila.get('quien', ''), dd.get('cifra') if isinstance(dd, dict) else None)
    texto_resumen = _plano(str(parrafo or '') + ' ' + ' '.join(str(b) for b in (bullets or [])))
    repetidos = sorted(t for t in tokens
                       if (re.search(r'(?<![a-z0-9\u00f1])' + re.escape(t) + r'(?![a-z0-9\u00f1])', texto_resumen)))
    if repetidos:
        E.append(f"11e · el resumen repite tokens del as_is (regla anti-redundancia C1): {repetidos} — "
                 "el resumen dice quiénes son y qué les duele; el as-is dice por dónde entra, "
                 "quién lo gestiona y dónde queda")

    # ---------- 12. planes: frontera invariante + frase del negocio (C3) ----------
    planes = p.get('planes')
    if not isinstance(planes, dict) or set(planes) != {'1', '2', '3'}:
        E.append(f"12a · bloque planes ausente o sin los tres planes: {sorted(planes) if isinstance(planes, dict) else planes!r}")
    else:
        for n, bloque in planes.items():
            fr, fx = (bloque or {}).get('frontera'), (bloque or {}).get('frase')
            if fr != FRONTERAS[n]:
                E.append(f"12b · frontera del plan {n} alterada — se copia textual de la matriz: "
                         f"«{FRONTERAS[n]}» (llegó: {fr!r})")
            if not isinstance(fx, str) or not fx.strip():
                E.append(f"12c · plan {n} sin frase al negocio (la frontera dicha en el lenguaje de ESTE cliente)")
            elif _plano(fx) == _plano(fr or ''):
                E.append(f"12d · la frase del plan {n} es la frontera repetida, no su traducción al negocio")

    # ---------- 13. sintesis y conecta_con por componente (C4, C5) ----------
    for cid, c in sel.items():
        s = c.get('sintesis')
        if not isinstance(s, str) or not s.strip():
            E.append(f"13a · '{cid}' sin sintesis (≤ 90 caracteres, una sola idea)")
        elif len(s) > 90:
            E.append(f"13b · sintesis de '{cid}' con {len(s)} caracteres (máx 90): «{s[:60]}…»")
        cx = c.get('conecta_con')
        if not isinstance(cx, list):
            E.append(f"13c · '{cid}' sin conecta_con como lista ([] si no engrana con nada)")
            continue
        for otro in cx:
            if otro == cid:
                E.append(f"13d · '{cid}' se conecta consigo mismo")
            elif otro not in sel:
                E.append(f"13e · '{cid}' conecta con '{otro}', que no está en los componentes de esta propuesta")
    for cid, c in sel.items():
        for otro in (c.get('conecta_con') or []):
            if otro in sel and cid in (sel[otro].get('conecta_con') or []):
                E.append(f"13f · ciclo de longitud 2 entre '{cid}' y '{otro}': la relación funcional tiene dirección")

    # ---------- 14. brecha_fuera_de_alcance (C6) ----------
    plan_rec = (p.get('plan_recomendado') or {}).get('plan')
    calc = brecha_esperada(p.get('madurez', []), plan_rec) if plan_rec else None
    br = p.get('brecha_fuera_de_alcance')
    if calc:
        techo, total, pts = calc
        if techo >= 100 and br is not None:
            E.append("14a · el plan recomendado llega a 100: brecha_fuera_de_alcance se omite entera")
        if techo < 100:
            if br is None:
                E.append(f"14b · techo del plan recomendado = {techo} < 100 y no hay brecha_fuera_de_alcance: "
                         "el cliente se quedaría con un techo inexplicado")
            else:
                g = (br.get('global') or {})
                if g.get('puntos') != total:
                    E.append(f"14c · brecha global dice {g.get('puntos')} puntos, madurez[].p del plan "
                             f"{plan_rec} da {total} (los escribe calcular_brecha.py, no la mano)")
                if not str(g.get('por_que', '')).strip():
                    E.append("14d · brecha global sin por_que")
                pm = br.get('por_modulo') or []
                vistos = {}
                for fila in pm:
                    m = fila.get('m')
                    if m not in MODULOS:
                        E.append(f"14e · brecha con módulo desconocido: {m!r}")
                        continue
                    vistos[m] = fila.get('puntos')
                    if fila.get('responsable') not in ('cliente', 'tercero', 'regulatorio'):
                        E.append(f"14f · brecha de {m} con responsable inválido: {fila.get('responsable')!r}")
                    for campo in ('por_que', 'que_puede_hacer'):
                        if not str(fila.get(campo, '')).strip():
                            E.append(f"14g · brecha de {m} sin {campo}")
                if vistos != pts:
                    E.append(f"14h · brecha por módulo dice {vistos}, madurez[].p del plan {plan_rec} da {pts} "
                             "(déficit × 100/28, redondeo por resto mayor — calcular_brecha.py)")
                suma = sum(v for v in vistos.values() if isinstance(v, int))
                if suma != g.get('puntos'):
                    E.append(f"14i · la suma de por_modulo ({suma}) no cuadra con global.puntos ({g.get('puntos')})")
    elif br is not None:
        W.append("14j · hay brecha_fuera_de_alcance pero madurez[].p o plan_recomendado no permiten verificarla")

    # ---------- 15. panel_interno: lo interno vive junto y solo ahí (C7, C9) ----------
    if not pi:
        E.append("15a · sin panel_interno: preguntas_para_el_consultor, no_aplican, multiplicador_calculado, "
                 "desglose_interno y sesiones viven ahí desde v0.5")
    else:
        pre = pi.get('preguntas_para_el_consultor')
        if not isinstance(pre, list):
            E.append("15b · panel_interno sin preguntas_para_el_consultor como lista ([] si no falta nada)")
        else:
            for q in pre:
                if not isinstance(q, dict) or any(not str(q.get(k, '')).strip()
                                                  for k in ('pregunta', 'por_que_importa', 'campo_ficha')):
                    E.append(f"15c · pregunta para el consultor incompleta — se espera "
                             f"{{pregunta, por_que_importa, campo_ficha}}: {q}")
            if p.get('modo') == 'B' and not pre:
                W.append("15d · modo B sin preguntas para el consultor: los datos económicos que faltan son la agenda")
        if not str(pi.get('desglose_interno', '')).strip():
            E.append("15e · panel_interno sin desglose_interno (antes vivía en condicion_comercial)")
        ses = pi.get('sesiones')
        if not isinstance(ses, list) or any(not str(s).strip() for s in (ses or [])):
            E.append("15f · panel_interno.sesiones debe ser una lista de textos (C9: salió del lienzo, no del expediente)")
    for campo in ('no_aplican', 'datos_que_faltan', 'multiplicador_calculado', 'sesiones'):
        if campo in p:
            E.append(f"15g · '{campo}' duplicado fuera de panel_interno: nada interno queda al alcance del lienzo")
    if 'desglose_interno' in cc:
        E.append("15h · desglose_interno sigue dentro de condicion_comercial: se muda a panel_interno")

    # ---------- 16. benchmark sin muestra (C8 + reconciliación) ----------
    bm = p.get('benchmark')
    if not isinstance(bm, dict):
        E.append("16a · sin bloque benchmark {por_modulo, fuente}")
    else:
        fu = bm.get('fuente')
        if not isinstance(fu, str) or not fu.strip():
            E.append("16b · benchmark sin fuente — redacción acordada: "
                     "«diagnósticos de PYMES en Colombia y Argentina, antes de implementar Ropofy»")
        elif re.search(r'\d', fu):
            E.append(f"16c · benchmark.fuente expone dígitos (prohibido exponer el n): «{fu}»")
        pm_bm = bm.get('por_modulo')
        if not isinstance(pm_bm, dict) or set(pm_bm) != set(MODULOS) \
           or any(not isinstance(v, (int, float)) for v in (pm_bm or {}).values()):
            E.append("16d · benchmark.por_modulo debe traer los 7 módulos con valor numérico")

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
