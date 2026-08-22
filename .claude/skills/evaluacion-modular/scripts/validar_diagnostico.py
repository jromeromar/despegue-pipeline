#!/usr/bin/env python3
"""Validador de diagnostico.json — criterios automáticos de la skill evaluacion-modular.
Uso: python3 validar_diagnostico.py diagnostico.json catalogo-fugas.md [ficha.json]
Exit 0 = pasa. Sirve también como compuerta de entrada de la etapa 3."""
import json, sys, re

MODULOS = ["Gestión","Atracción","Nutrición","Cierre","Reactivación","Referidos y Fidelización","Tableros"]
LETRA = lambda p: 'A' if p>=85 else 'B' if p>=70 else 'C' if p>=55 else 'D' if p>=40 else 'E' if p>=25 else 'F'

def validar(d, catalogo_md, ficha=None):
    E, W = [], []
    ver = tuple(int(n) for n in re.findall(r'\d+', str(d.get('_contrato', '')))[:2])
    v02 = ver >= (0, 2)   # diagnósticos sin _contrato son anteriores: se advierte, no se bloquea
    NUEVA = E if v02 else W   # reglas v0.2 (C11/C12) — el contrato no se reescribe hacia atrás
    ids_catalogo = set(re.findall(r'\*\*([A-Z]+-\d+)', catalogo_md)) \
                 | set(re.findall(r'^\|\s*([A-Z]+-\d+)', catalogo_md, re.M)) \
                 | set(re.findall(r'^#{2,4}\s+([A-Z]+-\d+)', catalogo_md, re.M))

    # ---------- 1. IDs contra el catálogo (la falla capital) ----------
    fugas = d.get('fugas',[])
    if not fugas: E.append("1a · cero fugas: una evaluación vacía no es una evaluación")
    for f in fugas:
        if f.get('id') not in ids_catalogo:
            E.append(f"1b · id '{f.get('id')}' NO existe en el catálogo: prohibido inventar categorías")

    # ---------- 1c-1g. Consolidación y título protagonista (C11, contrato v0.2) ----------
    solo_fugas = [f for f in fugas if f.get('categoria') == 'fuga']
    if len(solo_fugas) > 5:
        NUEVA.append(f"1c · {len(solo_fugas)} elementos con categoria 'fuga' (tope duro: 5) — se consolidan "
                     "en una fuga más general registrando los ids absorbidos en 'absorbe'; "
                     "cegueras y restricciones NO se consolidan ni se recortan")
    ids_presentes = {f.get('id') for f in fugas}
    for f in fugas:
        t = str(f.get('titulo', ''))
        if 'fuga' in t.lower():
            NUEVA.append(f"1d · título de {f.get('id')} contiene la palabra 'fuga' — el encabezado de "
                         f"sección ya la dice: «{t}»")
        if len(t) > 60:
            NUEVA.append(f"1e · título de {f.get('id')} con {len(t)} caracteres (máx 60 — es la frase "
                         f"protagonista, corta y en lenguaje del cliente): «{t[:70]}»")
        ab = f.get('absorbe')
        if ab is None:
            continue
        if f.get('categoria') != 'fuga':
            E.append(f"1f · {f.get('id')} declara 'absorbe' pero no es categoria 'fuga': solo las fugas se consolidan")
        if not isinstance(ab, list) or not ab:
            E.append(f"1f · 'absorbe' de {f.get('id')} debe ser una lista no vacía de ids del catálogo: {ab!r}")
            continue
        for aid in ab:
            if aid not in ids_catalogo:
                E.append(f"1f · {f.get('id')} absorbe '{aid}', que no existe en el catálogo")
            if aid in ids_presentes:
                E.append(f"1g · {f.get('id')} absorbe '{aid}' pero '{aid}' sigue como entrada propia: "
                         "una fuga absorbida no se cuenta dos veces (anti-doble-conteo extendido)")

    # ---------- 2. Dominante única ----------
    doms = [f['id'] for f in fugas if f.get('dominante')]
    if len(doms)!=1: E.append(f"2 · dominantes: {doms or 'ninguna'} — debe ser exactamente una")

    # ---------- 3. Trazabilidad ----------
    for f in fugas:
        if not f.get('evidencia_ficha'): E.append(f"3a · {f.get('id')} sin evidencia_ficha (campo de origen)")
        if not f.get('evidencia_textual') or '«' not in str(f.get('evidencia_textual','')):
            E.append(f"3b · {f.get('id')} sin cita textual «…»")
        if f.get('estado')=='mitigable' and not f.get('depende_de_tercero'):
            E.append(f"3c · {f.get('id')} mitigable sin declarar de quién depende")
    if ficha:
        ftxt = json.dumps(ficha, ensure_ascii=False)
        for f in fugas:
            cita = re.sub(r'\s+',' ', str(f.get('evidencia_textual',''))[1:40].lower())
            if cita and cita not in re.sub(r'\s+',' ', ftxt.lower()):
                W.append(f"3d · cita de {f['id']} no hallada literal en la ficha — verificar a mano")

    # ---------- 4. Anti-doble-conteo ----------
    duenas = [f['id'] for f in fugas if f.get('cuantificacion',{}).get('vive_aqui')]
    sin_dueno = [f['id'] for f in fugas if 'vive_aqui' not in f.get('cuantificacion',{})]
    if sin_dueno: E.append(f"4a · sin vive_aqui: {sin_dueno}")
    # cifras numéricas repetidas en dos fugas dueñas
    import collections
    cifras = collections.defaultdict(list)
    for f in fugas:
        if f.get('cuantificacion',{}).get('vive_aqui'):
            for n in re.findall(r'\d[\d\.]{2,}', f['cuantificacion'].get('valor','')):
                cifras[n].append(f['id'])
    for n, quien in cifras.items():
        if len(quien)>1: E.append(f"4b · la cifra {n} vive en {quien}: doble conteo")

    # ---------- 5. Modo y unidades ----------
    modo = d.get('modo')
    if modo not in ('A','B'): E.append(f"5a · modo inválido: {modo}")
    if modo=='B':
        con_dinero=[f['id'] for f in fugas if f.get('cuantificacion',{}).get('unidad')=='dinero']
        if con_dinero: E.append(f"5b · modo B con cuantificación en dinero: {con_dinero}")
        if not d.get('datos_que_faltan_para_modo_A'):
            W.append("5c · modo B sin lista de datos que faltan para pasar a A")

    # ---------- 6. Madurez completa y justificada ----------
    mad = d.get('madurez',[])
    presentes=[m.get('m') for m in mad]
    for m in MODULOS:
        if m not in presentes: E.append(f"6a · falta madurez de {m}")
    for m in mad:
        if m.get('hoy') not in (0,1,2,3,4): E.append(f"6b · nivel inválido en {m.get('m')}: {m.get('hoy')}")
        pq = str(m.get('por_que') or '')
        if not pq or len(pq) < 15:
            E.append(f"6c · {m.get('m')} sin por_que sustantivo: cada nivel cita su hecho")
        else:
            # C12 (contrato v0.2): 2–3 frases — el hecho de la ficha, qué nivel implica
            # y qué falta para el siguiente. En diagnósticos históricos solo advierte.
            segmentos = [s for s in re.split(r'[.;·]', pq) if len(s.split()) >= 3]
            if len(pq) < 80 or len(segmentos) < 2:
                NUEVA.append(f"6d · por_que de {m.get('m')} corto para el contrato v0.2 ({len(pq)} car., "
                             f"{len(segmentos)} frase(s)): debe traer el hecho de la ficha, qué nivel "
                             f"implica y qué falta para el siguiente — «{pq[:60]}…»")

    # ---------- 7. Nota aritméticamente correcta ----------
    niveles_ok = mad and all(m.get('hoy') in (0,1,2,3,4) for m in mad) and len(mad)==len(MODULOS)
    if niveles_ok:
        pts=round(sum(m['hoy'] for m in mad)/(len(MODULOS)*4)*100)
        nd=d.get('nota',{})
        if nd.get('puntos')!=pts: E.append(f"7a · nota dice {nd.get('puntos')}, la suma da {pts}")
        if nd.get('letra')!=LETRA(pts): E.append(f"7b · letra dice {nd.get('letra')}, corresponde {LETRA(pts)}")

    # ---------- 8. Pureza de etapa ----------
    txt=json.dumps(d, ensure_ascii=False).lower()
    for p in ['plan_minimo','fundamental','avanzado','inteligente','componente','precio','usd','snapshot','gohighlevel']:
        if p in txt:
            # 'avanzado' puede aparecer en silencios legítimamente: solo error si acompaña recomendación
            if p in ('avanzado','fundamental','inteligente') and 'recomend' not in txt and 'plan '+p not in txt:
                continue
            E.append(f"8 · el diagnóstico contiene '{p}': planes, componentes y precios son etapa 3")
            break

    return E, W

if __name__=='__main__':
    d=json.load(open(sys.argv[1]))
    cat=open(sys.argv[2]).read()
    ficha=json.load(open(sys.argv[3])) if len(sys.argv)>3 else None
    E,W=validar(d,cat,ficha)
    for e in E: print("✖",e)
    for w in W: print("⚠",w)
    print("✔ diagnóstico válido" + (f" · {len(W)} advertencias" if W else " sin observaciones") if not E else f"✖ {len(E)} errores")
    sys.exit(1 if E else 0)
