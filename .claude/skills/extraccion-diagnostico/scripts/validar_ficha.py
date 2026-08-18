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
