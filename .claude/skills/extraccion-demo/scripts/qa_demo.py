#!/usr/bin/env python3
"""
qa_demo.py — deriva qa-demo.json desde un prospecto.json (Etapa 0, v0.1)

Uso:
    python3 qa_demo.py prospecto-<cliente>.json [-o qa-demo-<cliente>.json]

No re-lee la transcripción: todo sale de los bloques G (lo_que_dijo_ropofy),
H (cierres_y_resultado) e I (ejecucion_del_guion) del prospecto, más los datos
de calificación de A y B. Una sola extracción, dos outputs — el prospecto viaja
al diagnóstico, el QA viaja a coaching y benchmarks, y nunca se desincronizan.

La rúbrica es determinista y está documentada en cada dimensión. Score 0-100
por dimensión, global ponderado, semáforo y acciones de coaching derivadas.
Exit siempre 0 (el QA reporta, no bloquea; quien bloquea es validar_prospecto).
"""

import json
import sys


# --------------------------------------------------------------- utilidades
def mmss_a_min(m):
    if isinstance(m, (int, float)):
        return float(m)
    if isinstance(m, str) and ":" in m:
        try:
            a, b = m.split(":")
            return int(a) + int(b) / 60
        except ValueError:
            return None
    return None


def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, round(x)))


ACCIONES = {
    # codigo de error → acción de coaching accionable
    "descubrimiento_omitido_o_minimo": "Correr las 5 preguntas de la ruta (F o A) antes de tocar la pantalla. Son 8 minutos y son el insumo de todo lo demás.",
    "preguntas_apiladas": "Una pregunta a la vez (R1): cada pregunta apilada pierde un dato para siempre.",
    "pregunta_de_configuracion_en_lugar_de_dolor": "Separar las preguntas de cotización (usuarios, líneas) de las de dolor: las primeras van en el bloque 10, no en el 2.",
    "demo_sin_encuadre": "No compartir pantalla sin el bloque 4: anunciar los 3 ejes y esperar el «sí».",
    "monologo_prolongado_sin_checkpoint": "Regla de ritmo: +60-90 s hablando → parar y preguntar. Mínimo una pregunta por acto.",
    "demo_conducida_por_el_cliente": "Cuando el cliente toma el control, anotar sus preguntas y devolver la narrativa al acto correspondiente.",
    "modulos_irrelevantes_mostrados": "Mostrar solo los 3 ejes del encuadre. Planeador, email y dashboards solo si el cliente los trae.",
    "pantalla_rota_o_dashboards_vacios": "Checklist del bloque 0: verificar el entorno de demo antes de conectarse.",
    "fallo_tecnico_en_vivo": "Checklist del bloque 0: ensayar el flujo exacto que se va a mostrar.",
    "precio_antes_de_cierre_1": "Aplazar el precio con la variante del bloque 1 («los vemos completos hoy mismo») y llegar a él después del cierre #1.",
    "precio_inconsistente_con_catalogo": "R2: solo cifras del catálogo vigente, leídas. Ninguna cifra de memoria.",
    "inconsistencia_interna_de_precio": "R2: una sola versión de cada número por llamada. Ensayar los 6 números clave antes de conectarse.",
    "cotizacion_sobre_volumen_supuesto": "R3: declarar el supuesto («es un ejemplo, no tu caso») y corregirlo en la Arquitectura con el dato real.",
    "descuento_o_downgrade_no_solicitado": "No rebajar plan ni anclar el paquete barato sin que nadie lo pida: deja dinero y credibilidad en la mesa.",
    "dolor_no_cuantificado": "Tras cada dolor, la repregunta de número: «¿cuántos al día? ¿cuánto vale uno?». Sin número no hay ROI.",
    "sin_validacion_del_entendimiento": "Bloque 3 completo: hecho → problema → impacto → número + «¿voy bien hasta ahí?» + silencio.",
    "avance_sin_validacion_explicita": "No pasar de bloque sin el «sí» explícito del micro-check.",
    "autoridad_no_calificada": "Calificar autoridad en el bloque 1, antes de invertir la llamada. Si hay tercero, sembrar la reunión conjunta desde ahí.",
    "identidad_del_interlocutor_no_confirmada": "Confirmar nombre y rol en el bloque 1: el nombre de la agenda suele no ser quien conecta.",
    "cargos_y_stakeholders_no_capturados": "Preguntar cargo y quién más operará el sistema: cada ausente es un proceso diseñado a ciegas.",
    "filtro_tecnico_omitido": "R5: el bloque 12 nunca se omite. Sin filtro no hay link de pago.",
    "atp_no_ofrecido": "Si el filtro falla, la ruta es ATP (USD 97), no «eso se arregla rápido».",
    "objecion_minimizada": "Una objeción no se minimiza («es muy intuitiva»): se convierte en argumento (implementación llave en mano) o se agenda su respuesta.",
    "objecion_sembrada_por_el_ejecutivo": "No introducir objeciones que el cliente no formuló (permanencias, cláusulas).",
    "pregunta_del_cliente_sin_responder": "R8: toda pregunta sin respuesta sale con fecha («lo confirmo y te lo envío el [día]»).",
    "respuesta_tecnica_insegura": "R8: nunca «creo que…». Anotar, confirmar con el equipo, enviar con fecha.",
    "claim_sin_sustento": "Cifras de resultado solo desde casos aprobados y citables.",
    "promesa_de_plazo_sin_alcance": "No prometer plazos de implementación antes del diagnóstico: el plazo sale del alcance.",
    "informacion_de_terceros_revelada": "R4: nunca nombrar clientes ni comentar su configuración. Prueba social = casos aprobados.",
    "jerga_no_entendida_no_aclarada": "Si el cliente no entiende un término, parar y aclararlo con sus palabras antes de seguir.",
    "cierre_pasivo_sin_pedir_decision": "El cierre #2 es una pregunta con silencio, no un «así quedamos».",
    "next_step_sin_fecha": "R6: nada sale de la llamada sin fecha — sesión, reunión con decisor o fecha de check.",
    "senal_de_compra_no_capitalizada": "R7: señal de compra explícita → dejar de mostrar y cerrar ahí.",
    "grabacion_dejada_corriendo": "R9: detener la grabación al colgar.",
}


def evaluar(p):
    eje = p.get("ejecucion_del_guion", {}) or {}
    met = eje.get("metricas_ejecucion", {}) or {}
    bloques = {b.get("id"): b for b in (eje.get("bloques") or [])}
    errores = eje.get("errores_detectados", []) or []
    cod_err = {e.get("codigo") for e in errores}
    pf = eje.get("preguntas_fijas_descubrimiento", []) or []
    dolores = (p.get("dolores_y_requisitos", {}) or {}).get("dolores", []) or []
    reac = p.get("reaccion_a_la_demo", {}) or {}
    ropofy = p.get("lo_que_dijo_ropofy", {}) or {}
    cot = ropofy.get("cotizacion_dicha", {}) or {}
    cierres = p.get("cierres_y_resultado", {}) or {}
    momentos = cierres.get("momentos_de_cierre", {}) or {}
    ident = p.get("identidad", {}) or {}
    decisor = ident.get("decisor", {}) or {}
    interlocutores = ident.get("interlocutores", []) or []
    detonantes = (p.get("origen_y_detonante", {}) or {}).get("detonante", []) or []
    eco = (p.get("negocio", {}) or {}).get("economia", {}) or {}
    dur = mmss_a_min((p.get("_meta", {}) or {}).get("duracion_demo_efectiva_min")) or \
        mmss_a_min(met.get("duracion_efectiva_min")) or 0

    dims = {}

    # ---------------- 1. CALIFICACIÓN (identidad, autoridad, decisor, detonante)
    h = []
    s = 0
    if interlocutores and all(i.get("identidad_confirmada") for i in interlocutores):
        s += 25
    else:
        h.append("Identidad del interlocutor no confirmada.")
    if interlocutores and any(i.get("rol_en_decision") not in (None, "desconocido") for i in interlocutores):
        s += 20
    else:
        h.append("Autoridad no calificada (rol_en_decision desconocido).")
    pres = decisor.get("presente_en_demo")
    fecha_dec = decisor.get("fecha_de_su_revision")
    fecha_dec_ok = isinstance(fecha_dec, dict) and fecha_dec.get("valor") not in (None, "no_capturado")
    if pres == "si":
        s += 30
    elif pres == "no" and fecha_dec_ok:
        s += 20
        h.append("Decisor ausente pero con fecha de revisión capturada.")
    else:
        h.append("Decisor ausente/ambiguo y sin fecha de su revisión.")
    duros = [d for d in detonantes if d.get("es_fecha_dura")]
    if detonantes:
        s += 10
        if not duros or any(
            isinstance(d.get("ventana_temporal"), dict)
            and d["ventana_temporal"].get("valor") in (None, "no_capturado")
            for d in duros
        ):
            if duros:
                h.append("Detonante con fecha dura capturado pero su ventana temporal quedó sin preguntar.")
                s += 5
            else:
                s += 15
        else:
            s += 15
    else:
        h.append("Ningún detonante capturado: no se sabe por qué ahora.")
    dims["calificacion"] = {"score": clamp(s), "hallazgos": h}

    # ---------------- 2. DESCUBRIMIENTO
    h = []
    s = 0
    pts_pf = 0
    for q in pf:
        f = q.get("formulada")
        pts_pf += 10 if f == "si" else 5 if f in ("parcial", "reformulada_como_configuracion") else 0
    s += pts_pf
    if pts_pf < 50:
        formuladas = sum(1 for q in pf if q.get("formulada") == "si")
        h.append(f"Preguntas fijas formuladas: {formuladas}/5.")
    if dolores:
        cuant = sum(1 for d in dolores if d.get("cuantificado"))
        s += round(20 * cuant / len(dolores))
        if cuant == 0:
            h.append(f"0 de {len(dolores)} dolores cuantificados.")
        con_cita = sum(1 for d in dolores if d.get("citas"))
        s += round(10 * con_cita / len(dolores))
    else:
        h.append("Ningún dolor registrado.")
    if dolores and all(d.get("arquetipo") for d in dolores):
        s += 5
    n_eco = ((eco.get("datos_economicos_capturados") or {}).get("n")) or 0
    de_eco = ((eco.get("datos_economicos_capturados") or {}).get("de")) or 9
    s += round(15 * min(1, n_eco / 3))  # meta del guion v3: 3 números mínimo
    if n_eco < 3:
        h.append(f"Datos económicos capturados: {n_eco}/{de_eco} (meta mínima del guion v3: 3).")
    dims["descubrimiento"] = {"score": clamp(s), "hallazgos": h}

    # ---------------- 3. CONDUCCIÓN
    h = []
    s = 0
    b3 = (bloques.get(3) or {}).get("estado")
    b4 = (bloques.get(4) or {}).get("estado")
    if b3 in ("ejecutado", "ejecutado_debil", "parcial"):
        s += 15
    else:
        h.append("Validación del entendimiento (bloque 3) omitida.")
    if b4 in ("ejecutado", "ejecutado_debil", "parcial"):
        s += 15
    else:
        h.append("Encuadre del demo (bloque 4) omitido: pantalla sin permiso.")
    chk = met.get("n_checkpoints_en_demo") or 0
    s += min(15, chk * 5)
    if chk < 3:
        h.append(f"Solo {chk} checkpoint(s) durante el demo.")
    mono = met.get("monologo_mas_largo_min") or 0
    s += 15 if mono <= 3 else 8 if mono <= 6 else 0
    if mono > 3:
        h.append(f"Monólogo más largo: {mono} min (regla: preguntar cada 60-90 s).")
    pant = mmss_a_min(met.get("minuto_pantalla_compartida"))
    if pant is not None and dur:
        ratio = pant / dur
        s += 20 if ratio >= 0.15 else round(20 * ratio / 0.15)
        if ratio < 0.15:
            h.append(f"Pantalla compartida al minuto {pant:.0f} de {dur:.0f}: descubrimiento comprimido.")
    preguntas = reac.get("preguntas_del_cliente", []) or []
    if preguntas:
        resp = sum(1 for q in preguntas if q.get("respondida") == "si")
        s += round(20 * resp / len(preguntas))
        sin = [q for q in preguntas if q.get("respondida") in ("no", "prometio_averiguar", "parcial")]
        if sin:
            h.append(f"{len(sin)} pregunta(s) del cliente sin respuesta completa.")
    else:
        h.append("Cero preguntas del cliente registradas: revisar engagement.")
    dims["conduccion"] = {"score": clamp(s), "hallazgos": h}

    # ---------------- 4. PRECIO
    h = []
    s = 0
    mp = mmss_a_min(met.get("minuto_primer_precio")) or mmss_a_min(cot.get("minuto_del_primer_precio"))
    if mp is not None and dur:
        ratio = mp / dur
        s += 30 if ratio >= 0.6 else round(30 * ratio / 0.6)
        if ratio < 0.6:
            h.append(f"Primer precio al minuto {mp:.0f} de {dur:.0f} ({ratio:.0%} de la llamada): antes del valor.")
    else:
        s += 30  # no se dio precio: no penaliza esta parte
    desv = ropofy.get("desviaciones_de_catalogo", []) or []
    s += max(0, 30 - 15 * len(desv))
    if desv:
        h.append(f"{len(desv)} desviación(es) de catálogo: " +
                 "; ".join(f"{d.get('concepto')} ({d.get('valor_dicho')} vs {d.get('valor_de_catalogo')})" for d in desv[:3]))
    origen_sup = ((cot.get("supuesto_de_volumen_usado") or {}).get("origen")) or ""
    if "supuso" in str(origen_sup) or "cotizacion_sobre_volumen_supuesto" in cod_err:
        h.append("La cotización se construyó sobre un volumen supuesto por el ejecutivo.")
    else:
        s += 20
    if "inconsistencia_interna_de_precio" not in cod_err:
        s += 10
    if "descuento_o_downgrade_no_solicitado" not in cod_err:
        s += 10
    dims["precio"] = {"score": clamp(s), "hallazgos": h}

    # ---------------- 5. CIERRES
    h = []
    s = 0
    nombres = {"cierre_1_valor_y_encaje": "Cierre #1", "confirmacion_de_interes": "Confirmación de interés",
               "cierre_2_decision": "Cierre #2"}
    for k, nombre in nombres.items():
        m = momentos.get(k, {}) or {}
        if m.get("ocurrio") and m.get("quien_lo_inicio") == "ejecutivo":
            s += 25
        elif m.get("quien_lo_inicio") == "cliente":
            s += 10
            h.append(f"{nombre}: lo inició el cliente, no el ejecutivo.")
        else:
            h.append(f"{nombre}: no se pidió.")
    if "senal_de_compra_no_capitalizada" not in cod_err:
        s += 25
    else:
        h.append("Hubo señal de compra explícita y no se cerró ahí (R7).")
    dims["cierres"] = {"score": clamp(s), "hallazgos": h}

    # ---------------- 6. RIESGO Y CUMPLIMIENTO
    h = []
    s = 0
    filtro = (cierres.get("filtro_tecnico") or {}).get("estado")
    s += {"completo": 40, "parcial": 20, "tardio": 15}.get(filtro, 0)
    if filtro != "completo":
        h.append(f"Filtro técnico Meta: {filtro or 'sin registrar'} (R5: sin filtro no hay link de pago).")
    resultado = cierres.get("resultado_demo")
    if filtro in (None, "omitido") and resultado in ("link_enviado_pago_pendiente", "pagado_en_llamada"):
        s -= 20
        h.append("Se envió/cobró el link con el filtro técnico omitido: violación directa de R5.")
    promesas = [x for x in (ropofy.get("promesas") or []) if not x.get("tiene_sustento")]
    s += max(0, 25 - 10 * len(promesas))
    if promesas:
        h.append(f"{len(promesas)} promesa(s) sin sustento: " + "; ".join(x.get("promesa", "")[:60] for x in promesas[:2]))
    if ropofy.get("informacion_de_terceros_revelada"):
        h.append("Se reveló información de otros clientes (R4).")
    else:
        s += 15
    claims = ropofy.get("claims_sin_sustento") or []
    s += max(0, 10 - 5 * len(claims))
    if claims:
        h.append(f"{len(claims)} claim(s) numérico(s) sin fuente.")
    if "grabacion_dejada_corriendo" not in cod_err:
        s += 10
    else:
        h.append("La grabación siguió corriendo después de la llamada (R9).")
    dims["riesgo_y_cumplimiento"] = {"score": clamp(s), "hallazgos": h}

    # ---------------- 7. SIGUIENTE PASO
    h = []
    s = 0
    ns = cierres.get("next_step", {}) or {}
    if ns.get("tiene_fecha"):
        s += 50
    else:
        h.append("Next step sin fecha (R6)." + (" Había detonante con fecha dura." if duros else ""))
        if ns.get("condicion"):
            s += 15
            h.append("Hay condición registrada, pero sin fecha de check.")
    entregables = ropofy.get("entregables_prometidos", []) or []
    if entregables:
        con_fecha = sum(1 for e in entregables if e.get("fecha_comprometida"))
        s += round(30 * con_fecha / len(entregables))
        if con_fecha < len(entregables):
            h.append(f"Entregables sin fecha: {len(entregables) - con_fecha}/{len(entregables)}.")
    else:
        s += 15
    if resultado not in (None, "sin_next_step"):
        s += 20
    else:
        h.append("La llamada terminó sin next step definido.")
    dims["siguiente_paso"] = {"score": clamp(s), "hallazgos": h}

    # ---------------- global, semáforo, coaching
    pesos = {"calificacion": .15, "descubrimiento": .20, "conduccion": .10,
             "precio": .15, "cierres": .15, "riesgo_y_cumplimiento": .15, "siguiente_paso": .10}
    global_ = clamp(sum(dims[k]["score"] * w for k, w in pesos.items()) / sum(pesos.values()))
    semaforo = "verde" if global_ >= 75 else "amarillo" if global_ >= 50 else "rojo"

    graves = [e for e in errores if e.get("gravedad") == "alta"]
    acciones, vistos = [], set()
    for e in graves:
        c = e.get("codigo")
        if c in ACCIONES and c not in vistos:
            acciones.append({"error": c, "accion": ACCIONES[c]})
            vistos.add(c)
        if len(acciones) >= 5:
            break

    meta_p = p.get("_meta", {}) or {}
    return {
        "_meta": {
            "id_qa": f"qa-{meta_p.get('id_prospecto', 'sin-id')}",
            "derivado_de": meta_p.get("id_prospecto"),
            "version_qa": "0.1",
            "version_guion_auditado": meta_p.get("version_guion"),
            "fecha_demo": meta_p.get("fecha_demo"),
            "ejecutivo": meta_p.get("ejecutivo"),
            "duracion_demo_efectiva_min": meta_p.get("duracion_demo_efectiva_min"),
        },
        "score_global": global_,
        "semaforo": semaforo,
        "dimensiones": dims,
        "resultado_comercial": {
            "ruta_definida": cierres.get("ruta_definida"),
            "resultado_demo": resultado,
            "temperatura_derivada": (cierres.get("temperatura_derivada") or {}).get("valor"),
            "next_step_con_fecha": bool(ns.get("tiene_fecha")),
            "quien_inicio_los_cierres": {k: (momentos.get(k, {}) or {}).get("quien_lo_inicio") for k in nombres},
        },
        "adherencia": {
            "bloques": [{"id": b.get("id"), "nombre": b.get("nombre"), "estado": b.get("estado")}
                        for b in (eje.get("bloques") or [])],
            "adherencia_bloques": met.get("adherencia_bloques"),
            "preguntas_fijas_formuladas": met.get("preguntas_fijas_formuladas"),
            "dolores_cuantificados": met.get("dolores_cuantificados"),
            "minuto_primer_precio": met.get("minuto_primer_precio"),
            "minuto_pantalla_compartida": met.get("minuto_pantalla_compartida"),
            "monologo_mas_largo_min": met.get("monologo_mas_largo_min"),
        },
        "errores_graves": [{"codigo": e.get("codigo"), "minuto": e.get("minuto"), "cita": e.get("cita")}
                           for e in graves],
        "acciones_coaching": acciones,
    }


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    entrada = args[0]
    salida = None
    if "-o" in args:
        salida = args[args.index("-o") + 1]
    with open(entrada, encoding="utf-8") as f:
        p = json.load(f)
    qa = evaluar(p)
    if not salida:
        base = (qa["_meta"]["derivado_de"] or "prospecto").replace("demo-", "", 1)
        salida = f"qa-demo-{base}.json"
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(qa, f, ensure_ascii=False, indent=2)
    print(f"== {salida}")
    print(f"   global: {qa['score_global']}/100  [{qa['semaforo'].upper()}]")
    for k, v in qa["dimensiones"].items():
        print(f"   {k:24s} {v['score']:>3}/100")
    if qa["acciones_coaching"]:
        print("   coaching:")
        for a in qa["acciones_coaching"][:3]:
            print(f"     - {a['accion']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
