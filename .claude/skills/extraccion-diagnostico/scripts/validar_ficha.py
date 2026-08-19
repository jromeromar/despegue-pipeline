#!/usr/bin/env python3
"""Validador de ficha.json — criterios automáticos de la skill extraccion-diagnostico.
Uso: python3 validar_ficha.py ficha-cliente.json [transcripcion.txt]
Sale con código 0 si pasa, 1 si falla. Diseñado para correr también como
compuerta de entrada de la etapa 2 (evaluación)."""
import json, sys, re

def validar(ficha, transcripcion=None):
    E = []   # errores (bloquean)
    W = []   # advertencias (se reportan, no bloquean)

    # ---------- A. VALIDEZ ESTRUCTURAL ----------
    for b in ['_meta','A_lineas_de_negocio','B_estructura','C_territorio',
              'D_stack','E_multiplicadores','F_calidad_del_diagnostico']:
        if b not in ficha: E.append(f"A1 · falta el bloque {b}")
    if not ficha.get('_meta',{}).get('fuentes'): E.append("A2 · _meta.fuentes vacío: la ficha no declara de qué sesión salió")
    if not ficha.get('_meta',{}).get('version_ficha'): E.append("A3 · sin version_ficha: la etapa 2 no sabe contra qué contrato validar")

    # ---------- B. LÍNEAS DE NEGOCIO ----------
    lineas = ficha.get('A_lineas_de_negocio',[])
    if not lineas: E.append("B1 · cero líneas de negocio: imposible en una sesión real")
    for l in lineas:
        for k in ['id','sujeto_del_embudo','control_del_activo','mecanismo_de_cierre']:
            if k not in l: E.append(f"B2 · línea {l.get('id','?')} sin {k}")
        if l.get('sujeto_del_embudo') not in ('demandante','oferente','no_aplica'):
            E.append(f"B3 · sujeto inválido en {l.get('id')}: {l.get('sujeto_del_embudo')}")
        if 'evidencia' not in l:
            E.append(f"B4 · línea {l.get('id')} sin evidencia textual")

    # ---------- C. FIDELIDAD (anti-inferencia) ----------
    txt = json.dumps(ficha, ensure_ascii=False)
    nc = txt.count('no_capturado')
    if nc == 0:
        E.append("C1 · CERO no_capturado: una sesión de ~60 min no cubre todo el contrato. "
                 "Señal de invención — la trampa #1 de la skill")
    elif nc < 5:
        W.append(f"C2 · solo {nc} no_capturado: revisar si se infirió (esperable: 8–20)")
    evid = txt.count('«')
    if evid < max(3, len(lineas)):
        E.append(f"C3 · solo {evid} evidencias textuales para {len(lineas)} líneas: "
                 "cada dato no obvio necesita su cita")
    # evidencias que no están en la transcripción (invención de citas)
    if transcripcion:
        plano = re.sub(r'\s+',' ', transcripcion.lower())
        for m in re.findall(r'«([^»]{15,60})', txt):
            frag = re.sub(r'\s+',' ', m.lower())[:40]
            if frag not in plano:
                W.append(f"C4 · evidencia no hallada literal en la transcripción: «{m[:50]}…» "
                         "(puede ser recorte legítimo — verificar a mano)")

    # ---------- D. CONFLICTOS ----------
    F = ficha.get('F_calidad_del_diagnostico',{})
    for c in F.get('datos_en_conflicto',[]):
        estado = str(c.get('estado','')).lower()
        if 'resuelto' in estado: continue
        oa, ob = c.get('objeto_a'), c.get('objeto_b')
        if not oa or not ob:
            E.append(f"D1 · conflicto '{c.get('tema')}' sin objeto_a/objeto_b: "
                     "no se puede afirmar que hablan de lo mismo (regla del falso conflicto)")
        elif oa != ob:
            E.append(f"D2 · conflicto '{c.get('tema')}' con objetos distintos "
                     f"({oa} vs {ob}): son dos datos, no un conflicto")
        if not c.get('impacto'): W.append(f"D3 · conflicto '{c.get('tema')}' sin impacto declarado")

    # ---------- E. MODO Y ECONOMÍA ----------
    modo = F.get('modo_propuesta')
    if modo not in ('A','B'): E.append(f"E1 · modo_propuesta inválido: {modo}")
    econ = str(F.get('datos_economicos_capturados','')).lower()
    if modo=='A' and econ=='no': E.append("E2 · modo A sin datos económicos: contradicción")
    if modo=='B' and econ=='si': W.append("E3 · modo B con datos económicos capturados: ¿debería ser A?")

    # ---------- F. BLOQUE D DE VOZ (campos v0.2.1) ----------
    D = ficha.get('D_stack',{})
    for k in ['whatsapp_estado','numeros_publicados','llamadas_medidas','decision_del_numero']:
        if k not in D: E.append(f"F1 · D_stack sin {k} (contrato v0.2.1): aunque sea no_capturado, debe existir")

    # ---------- G. ESTRUCTURA HUMANA ----------
    B = ficha.get('B_estructura',{})
    if not B.get('personas_declaradas'): E.append("G1 · sin personas declaradas")
    if 'funciones_sin_representacion' not in F:
        E.append("G2 · falta funciones_sin_representacion: el campo que protege del proceso diseñado sin su dueño")

    # ---------- H. PUREZA DE ETAPA ----------
    prohibidas = ['plan_minimo','componente','recomendamos','se recomienda','deberia implementar',
                  'fundamental','avanzado','inteligente','snapshot','gohighlevel']
    for p in prohibidas:
        if p in txt.lower():
            E.append(f"H1 · la ficha contiene '{p}': la etapa 1 registra, no evalúa ni propone")

    # ---------- I. NOMBRES PROPIOS: consistencia y completitud (contrato v0.3) ----------
    # Ningún chequeo de aquí juzga ortografía: eso no lo puede saber un script.
    # Verifican que la duda esté DECLARADA como manda el contrato; si el apellido
    # está bien escrito lo decide la compuerta de nombres y el criterio J2.
    M = ficha.get('_meta', {})
    ver = tuple(int(n) for n in re.findall(r'\d+', str(M.get('version_ficha','')))[:3])
    v03, v022 = ver >= (0,3), ver >= (0,2,2)
    ESTADOS = ('confirmada','por_confirmar')
    TITULO_DE_REUNION = re.compile(
        r'(t[ií]tulo|nombre|asunto)\s+de\s+(la\s+|el\s+)?(reuni|grabaci|invitaci|sesi|llamada|meeting)'
        r'|invitaci\w*\s+(de|del|en)\s+(teams|calendario|outlook)', re.I)
    pendientes = []

    def nombre_propio(donde, obj, campo_estado, campo_grafia, duro):
        """Revisa un bloque de nombre propio. duro=True bloquea; False solo advierte
        (ficha anterior al contrato que lo introdujo: histórica válida)."""
        S = E if duro else W
        viejo = '' if duro else 'ficha < v0.3 · '
        est, variantes = obj.get(campo_estado), obj.get('variantes_en_transcripcion')
        grafia = str(obj.get(campo_grafia,'')).strip()
        if est is None or variantes is None:
            S.append(f"I2 · {viejo}{donde} sin {campo_estado} o sin variantes_en_transcripcion "
                     "(v0.3 §Nombres propios): un nombre propio no declara su duda solo")
            return
        if est not in ESTADOS:
            S.append(f"I3 · {donde}: {campo_estado} inválido {est!r} — solo 'confirmada' o 'por_confirmar'")
        if not isinstance(variantes, list):
            S.append(f"I8 · {donde}: variantes_en_transcripcion no es una lista ({type(variantes).__name__})")
            return
        if est == 'por_confirmar':
            pendientes.append(donde)
            if not variantes and grafia != 'no_capturado':
                S.append(f"I4 · {donde}: por_confirmar con variantes_en_transcripcion vacío — si hay duda, "
                         "algo trajo la transcripción y esa es la prueba (vacío solo si la grafía es no_capturado)")
            if str(obj.get('fuente_escrita','')).strip():
                W.append(f"I7 · {donde}: declara fuente_escrita y sigue por_confirmar — "
                         "¿se corrió la compuerta de nombres y no se cerró el estado?")
        elif est == 'confirmada':
            fuente = str(obj.get('fuente_escrita','')).strip()
            if not fuente:
                S.append(f"I5 · {donde}: 'confirmada' sin fuente_escrita — oírla en la sesión no confirma "
                         "nada; se declara dónde se vio ESCRITA (correo, firma, factura, sitio, contrato)")
            elif TITULO_DE_REUNION.search(fuente):
                S.append(f"I6 · {donde}: 'confirmada' con el título de la reunión como fuente ({fuente!r}) — "
                         "eso lo escribió quien creó la reunión, casi siempre Ropofy: no confirma la grafía del cliente")

    # I1 · marca (contratada en v0.2.2) y su consistencia con _meta.cliente
    marca = M.get('marca')
    if isinstance(marca, dict):
        nombre_propio('_meta.marca', marca, 'estado', 'grafia', True)
        if str(marca.get('grafia','')).strip() != str(M.get('cliente','')).strip():
            E.append(f"I1 · _meta.cliente ({M.get('cliente')!r}) ≠ _meta.marca.grafia "
                     f"({marca.get('grafia')!r}): alguien corrigió una y olvidó la otra")
    elif v022:
        E.append("I2 · sin _meta.marca y la ficha se declara v0.2.2+: la grafía de la marca no tiene dónde vivir")
    else:
        W.append("I2 · ficha < v0.2.2 sin _meta.marca: histórica válida; al reprocesarla se agrega")

    # razón social (contratada en v0.3)
    rs = M.get('razon_social')
    if isinstance(rs, dict):
        nombre_propio('_meta.razon_social', rs, 'estado', 'grafia', True)
    elif v03:
        E.append("I2 · sin _meta.razon_social y la ficha se declara v0.3: la razón social es un dato distinto "
                 "de la marca y no se esconde dentro de ella")
    else:
        W.append("I2 · ficha < v0.3 sin _meta.razon_social: histórica válida; al reprocesarla se agrega")

    # personas y sistemas (contratados en v0.3): duros solo si la ficha se declara v0.3
    for per in B.get('personas_declaradas', []) or []:
        nombre_propio(f"persona «{per.get('nombre','?')}»", per, 'grafia_estado', 'nombre', v03)
    for sis in D.get('sistemas', []) or []:
        nombre_propio(f"sistema «{sis.get('nombre','?')}»", sis, 'grafia_estado', 'nombre', v03)

    # I9 · resumen: lo que sigue por confirmar es agenda, no defecto
    if pendientes:
        muestra = ', '.join(pendientes[:5]) + ('…' if len(pendientes) > 5 else '')
        W.append(f"I9 · {len(pendientes)} nombre(s) propio(s) en por_confirmar ({muestra}): corre la compuerta "
                 "de confirmación de nombres antes de la etapa 2; lo que el consultor no sepa va a la agenda "
                 "de la segunda llamada")

    return E, W

if __name__=='__main__':
    ficha=json.load(open(sys.argv[1]))
    trans=open(sys.argv[2]).read() if len(sys.argv)>2 else None
    E,W = validar(ficha, trans)
    for e in E: print("✖", e)
    for w in W: print("⚠", w)
    if not E and not W: print("✔ ficha válida sin observaciones")
    elif not E: print(f"✔ ficha válida · {len(W)} advertencias")
    sys.exit(1 if E else 0)
