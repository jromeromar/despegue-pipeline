#!/usr/bin/env python3
"""
validar_prospecto.py — validador del contrato prospecto.json (Etapa 0, v0.1)

Uso:
    python3 validar_prospecto.py prospecto-<cliente>.json [--catalogo catalogo-precios.json]

Salida: lista de ERRORES (bloquean la entrega) y ADVERTENCIAS (revisar a mano).
Exit 0 si no hay errores, 1 si hay al menos uno.

El validador implementa las reglas P1–P18 y A1–A4 de references/schema-prospecto.md.
Lo que no puede ver (si la cita es fiel, si el arquetipo del dolor es el correcto,
si la pregunta sugerida está bien redactada) queda para la auto-revisión humana.
"""

import json
import re
import sys

# ---------------------------------------------------------------- catálogo base
# Valores de catálogo vigentes según el guion. Cuando exista catalogo-precios.json
# versionado, se pasa con --catalogo y estos quedan solo como respaldo.
CATALOGO = {
    "implementacion_min": 499,
    "despegue_precio": 24,
    "despegue_dias": 14,
    "atp_precio": 97,
}

FUENTES = {
    "cliente_declaro", "cliente_confirmo", "cliente_asintio",
    "cliente_forzado_por_menu", "ejecutivo_afirmo_sin_confirmar",
    "ejecutivo_supuso_para_cotizar", "formulario_previo", "bot_ia_ropofy",
    "crm_precall", "audio_ambiente", "inferido_de_transcripcion", "n/a",
}

AUSENCIAS = {
    "no_preguntado", "preguntado_sin_respuesta", "cliente_no_lo_sabe",
    "dato_no_existe_en_el_negocio", "no_aplica",
}

CONFIANZAS = {"alta", "media", "baja", "asr_dudoso"}

# Fuentes que convierten el dato en hipótesis (regla P7).
FUENTES_HIPOTESIS = {
    "cliente_asintio", "cliente_forzado_por_menu",
    "ejecutivo_afirmo_sin_confirmar", "ejecutivo_supuso_para_cotizar",
}

# Fuentes que exigen cita textual cuando hay valor (regla P3).
FUENTES_CON_CITA = {
    "cliente_declaro", "cliente_confirmo", "cliente_asintio",
    "cliente_forzado_por_menu", "ejecutivo_afirmo_sin_confirmar",
    "ejecutivo_supuso_para_cotizar", "audio_ambiente",
}

# Campos marcados ⚑agenda en el contrato: un `no_preguntado` aquí obliga a
# registrar el vacío y a generar una pregunta para el diagnóstico (regla P4).
# Se comparan como sufijos de la ruta completa del dato.
CAMPOS_AGENDA = [
    "empresa.nombre_comercial",
    "empresa.razon_social",
    "decisor.fecha_de_su_revision",
    "economia.ticket_promedio",
    "economia.margen",
    "economia.ad_spend_mensual",
    "economia.comision",
    "economia.tasa_de_cierre",
    "economia.facturacion",
    "economia.presupuesto_declarado",
    "economia.costo_de_personal_sustituible",
    "economia.benchmark_de_sustitucion",
    "equipo_comercial.personas_que_atienden_leads",
    "equipo_comercial.horarios",
    "equipo_comercial.quien_responde_fuera_de_horario",
    "respuesta_y_seguimiento.canales_de_entrada_confirmados",
    "respuesta_y_seguimiento.que_pasa_cuando_no_se_responde",
    "respuesta_y_seguimiento.frecuencia_de_no_respuesta",
    "respuesta_y_seguimiento.seguimiento_sistematizado",
    "respuesta_y_seguimiento.medicion_de_leads_perdidos",
    "respuesta_y_seguimiento.punto_de_quiebre_al_duplicar_volumen",
    "respuesta_y_seguimiento.tiempo_de_respuesta_actual",
    "respuesta_y_seguimiento.exito_60_90_dias",
    "habilitacion_meta.business_manager",
    "habilitacion_meta.admin_del_bm",
    "habilitacion_meta.fanpage",
    "habilitacion_meta.cuenta_publicitaria",
    "habilitacion_meta.bloqueos_o_restricciones",
    "habilitacion_meta.categoria_permitida",
    "habilitacion_meta.accesos_en_manos_de_terceros",
    "restricciones.base_legal_de_contacto",
]
RE_TICKET_LINEA = re.compile(r"lineas_negocio\[\d+\]\.ticket$")

ESTADOS_BLOQUE = {
    "ejecutado", "ejecutado_debil", "parcial", "omitido",
    "fuera_de_orden", "iniciado_por_el_cliente",
}
FORMULADA = {"si", "no", "parcial", "reformulada_como_configuracion"}
MOMENTOS = {"brief_previo", "en_sesion", "evidencia_en_vivo", "asincrono_cliente"}
PRIORIDADES = {"bloqueante", "alta", "media"}

errores, advertencias = [], []


def err(regla, msg):
    errores.append(f"[{regla}] {msg}")


def adv(regla, msg):
    advertencias.append(f"[{regla}] {msg}")


# ------------------------------------------------------------------- recorrido
def es_dato(obj):
    return isinstance(obj, dict) and "fuente" in obj and "valor" in obj


def recorrer(nodo, ruta=""):
    """Devuelve [(ruta, dato)] de todos los objetos Dato del documento."""
    encontrados = []
    if es_dato(nodo):
        encontrados.append((ruta, nodo))
        return encontrados
    if isinstance(nodo, dict):
        for k, v in nodo.items():
            encontrados += recorrer(v, f"{ruta}.{k}" if ruta else k)
    elif isinstance(nodo, list):
        for i, v in enumerate(nodo):
            encontrados += recorrer(v, f"{ruta}[{i}]")
    return encontrados


def es_agenda(ruta):
    if RE_TICKET_LINEA.search(ruta):
        return True
    return any(ruta.endswith(c) for c in CAMPOS_AGENDA)


def numerico(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


# ------------------------------------------------------------------ validación
def validar(p):
    # ---- P18 estructura mínima
    meta = p.get("_meta")
    if not isinstance(meta, dict):
        err("P18", "falta el bloque _meta")
        meta = {}
    for c in ("id_prospecto", "version_schema", "version_guion", "fuentes",
              "fecha_demo", "ejecutivo", "duracion_demo_efectiva_min",
              "calidad_transcripcion"):
        if c not in meta:
            err("P18", f"_meta sin campo obligatorio '{c}'")

    bloques_raiz = ("identidad", "origen_y_detonante", "negocio",
                    "operacion_actual", "dolores_y_requisitos",
                    "reaccion_a_la_demo", "lo_que_dijo_ropofy",
                    "cierres_y_resultado", "ejecucion_del_guion",
                    "calidad_y_agenda")
    for b in bloques_raiz:
        if b not in p:
            err("P18", f"falta el bloque raíz '{b}'")

    cal = p.get("calidad_y_agenda", {}) or {}
    vacios = cal.get("vacios", []) or []
    agenda = cal.get("agenda_diagnostico", []) or []
    hipotesis = cal.get("hipotesis_a_verificar", []) or []
    dolores = (p.get("dolores_y_requisitos", {}) or {}).get("dolores", []) or []
    objeciones = (p.get("reaccion_a_la_demo", {}) or {}).get("objeciones", []) or []

    ids_vacios = {v.get("id") for v in vacios if v.get("id")}
    ids_hipotesis = {h.get("id") for h in hipotesis if h.get("id")}
    ids_dolores = [d.get("id") for d in dolores if d.get("id")]

    # ---- P1, P2, P3, P9 sobre cada Dato
    datos = recorrer(p)
    for ruta, d in datos:
        valor, ausencia, fuente = d.get("valor"), d.get("ausencia"), d.get("fuente")
        sin_dato = valor == "no_capturado"

        if sin_dato and not ausencia:
            err("P1", f"{ruta}: valor 'no_capturado' sin motivo de ausencia")
        if not sin_dato and ausencia:
            err("P1", f"{ruta}: tiene valor y además ausencia '{ausencia}'")
        if ausencia and ausencia not in AUSENCIAS:
            err("P1", f"{ruta}: ausencia '{ausencia}' fuera del enum")

        if fuente not in FUENTES:
            err("P2", f"{ruta}: fuente '{fuente}' fuera del enum")
        if fuente and (fuente.startswith("cliente_") or fuente.startswith("ejecutivo_")):
            if not d.get("hablante"):
                err("P2", f"{ruta}: fuente '{fuente}' exige 'hablante'")
        if sin_dato and fuente != "n/a":
            adv("P2", f"{ruta}: sin dato pero fuente '{fuente}' (se espera 'n/a')")

        conf = d.get("confianza")
        if conf and conf not in CONFIANZAS:
            err("P2", f"{ruta}: confianza '{conf}' fuera del enum")
        if fuente == "cliente_forzado_por_menu" and conf != "baja":
            err("P2", f"{ruta}: 'cliente_forzado_por_menu' exige confianza 'baja'")

        if not sin_dato and fuente in FUENTES_CON_CITA:
            ev = d.get("evidencia")
            if not ev:
                err("P3", f"{ruta}: fuente '{fuente}' exige evidencia textual")
            else:
                if len(ev) > 200:
                    err("P3", f"{ruta}: evidencia de {len(ev)} caracteres (máximo 200)")
                if "«" not in ev or "»" not in ev:
                    err("P3", f"{ruta}: la evidencia debe ir en comillas españolas «»")
        if not sin_dato and fuente == "inferido_de_transcripcion" and not d.get("nota_de_inferencia"):
            err("P3", f"{ruta}: inferencia sin 'nota_de_inferencia'")

        if numerico(valor) and not d.get("unidad"):
            err("P9", f"{ruta}: cifra {valor} sin 'unidad'")

        # ---- P7 hipótesis obligatoria
        if not sin_dato and fuente in FUENTES_HIPOTESIS and not hipotesis:
            err("P7", f"{ruta}: fuente '{fuente}' y no hay hipotesis_a_verificar")

        # ---- P4 vacío + agenda
        if ausencia == "no_preguntado" and es_agenda(ruta):
            cubiertos = [v for v in vacios
                         if v.get("campo") and ruta.endswith(v["campo"])]
            if not cubiertos:
                err("P4", f"{ruta}: 'no_preguntado' en campo ⚑agenda y no está en vacios[]")
            else:
                vids = {v.get("id") for v in cubiertos}
                if not any(_deriva_toca(a, vids) for a in agenda):
                    err("P4", f"{ruta}: vacío {sorted(v for v in vids if v)} sin entrada en agenda_diagnostico")

    # ---- P9 bis: volumen_leads
    eco = (p.get("negocio", {}) or {}).get("economia", {}) or {}
    vol = eco.get("volumen_leads")
    if isinstance(vol, dict) and vol.get("valor") != "no_capturado":
        for c in ("unidad", "periodo", "tipo", "precision"):
            if not vol.get(c):
                err("P9", f"economia.volumen_leads sin '{c}'")

    # ---- P8 modo de propuesta
    duros = ("ticket_promedio", "margen", "comision", "ad_spend_mensual")
    faltan = all((eco.get(c) or {}).get("valor") == "no_capturado" for c in duros)
    modo = (eco.get("datos_economicos_capturados") or {}).get("modo_propuesta_previsto")
    modo_j = cal.get("modo_propuesta_previsto")
    if modo not in ("A", "B"):
        err("P8", f"modo_propuesta_previsto inválido en economia: {modo!r}")
    if modo_j and modo and modo_j != modo:
        err("P8", f"modo_propuesta_previsto inconsistente: economia={modo}, calidad_y_agenda={modo_j}")
    if faltan and modo != "B":
        err("P8", "sin ticket, margen, comisión ni ad spend el modo debe ser 'B'")
    if not faltan and modo == "A":
        pass  # correcto: hay al menos un dato duro
    if faltan and modo_j == "A":
        err("P8", "calidad_y_agenda.modo_propuesta_previsto='A' sin ningún dato económico")

    # ---- P5 habilitación Meta vs ruta
    hab = (p.get("operacion_actual", {}) or {}).get("habilitacion_meta", {}) or {}
    cierres = p.get("cierres_y_resultado", {}) or {}
    bloqueos = cal.get("bloqueos_para_avanzar", []) or []
    meta_incompleta = [k for k, v in hab.items()
                       if isinstance(v, dict) and v.get("ausencia") == "no_preguntado"]
    if meta_incompleta and cierres.get("ruta_definida") == "activacion_arquitectura" and not bloqueos:
        err("P5", f"ruta 'activacion_arquitectura' con habilitación Meta sin verificar "
                  f"({len(meta_incompleta)} campos) y sin bloqueos_para_avanzar")

    # ---- P6 decisor ausente
    dec = (p.get("identidad", {}) or {}).get("decisor", {}) or {}
    if dec.get("presente_en_demo") not in ("si", "no", "ambiguo"):
        err("P6", f"decisor.presente_en_demo inválido: {dec.get('presente_en_demo')!r}")
    if dec.get("presente_en_demo") != "si" and not bloqueos:
        err("P6", "decisor no presente y sin entradas en bloqueos_para_avanzar")

    # ---- P7 bis: supuesto de cotización
    cot = (p.get("lo_que_dijo_ropofy", {}) or {}).get("cotizacion_dicha", {}) or {}
    sup = cot.get("supuesto_de_volumen_usado") or {}
    if sup.get("origen") == "ejecutivo_supuso_para_cotizar" and not hipotesis:
        err("P7", "la cotización usó un volumen supuesto por el ejecutivo y no hay hipótesis que lo registre")

    # ---- P10 conflictos
    for i, c in enumerate(cal.get("datos_en_conflicto", []) or []):
        if c.get("objeto_a") != c.get("objeto_b"):
            err("P10", f"datos_en_conflicto[{i}] '{c.get('tema')}': objeto_a != objeto_b "
                       "(no es conflicto: son dos datos y van registrados por separado)")

    # ---- P11 / P12 dolores
    for i, d in enumerate(dolores):
        did = d.get("id") or f"dolores[{i}]"
        if d.get("quien_lo_verbalizo") == "cliente" and not (d.get("citas") or []):
            err("P11", f"dolor '{did}': verbalizado por el cliente y sin cita textual")
        if d.get("cuantificado") is False:
            if not any(_deriva_toca_dolor(a, did) for a in agenda):
                err("P12", f"dolor '{did}' sin cuantificar y sin pregunta de cuantificación en la agenda")
        if d.get("cuantificado") is True and not (d.get("magnitud") or {}).get("valor"):
            err("P12", f"dolor '{did}': cuantificado=true sin 'magnitud'")

    # ---- P13 ejecución
    eje = p.get("ejecucion_del_guion", {}) or {}
    bl = eje.get("bloques", []) or []
    if len(bl) != 13:
        err("P13", f"bloques[] tiene {len(bl)} entradas (deben ser 13)")
    for b in bl:
        if b.get("estado") not in ESTADOS_BLOQUE:
            err("P13", f"bloque {b.get('id')}: estado '{b.get('estado')}' fuera del enum")
    pf = eje.get("preguntas_fijas_descubrimiento", []) or []
    if len(pf) != 5:
        err("P13", f"preguntas_fijas_descubrimiento[] tiene {len(pf)} entradas (deben ser 5)")
    for q in pf:
        if q.get("formulada") not in FORMULADA:
            err("P13", f"pregunta fija {q.get('n')}: formulada '{q.get('formulada')}' fuera del enum")

    # ---- P14 desviaciones de catálogo
    desv = (p.get("lo_que_dijo_ropofy", {}) or {}).get("desviaciones_de_catalogo", []) or []
    texto_desv = json.dumps(desv, ensure_ascii=False).lower()
    imp = cot.get("implementacion_min_dicho")
    if numerico(imp) and imp != CATALOGO["implementacion_min"]:
        if "implementaci" not in texto_desv:
            err("P14", f"implementación mínima dicha ({imp}) != catálogo "
                       f"({CATALOGO['implementacion_min']}) y no está en desviaciones_de_catalogo[]")
    dias = cot.get("despegue_dias_dicho")
    if isinstance(dias, (int, float)) and dias != CATALOGO["despegue_dias"]:
        if "despegue" not in texto_desv and "duraci" not in texto_desv:
            err("P14", f"duración del despegue dicha ({dias}) != catálogo y no está registrada como desviación")
    prec = cot.get("despegue_precio_dicho")
    if numerico(prec) and prec != CATALOGO["despegue_precio"] and "despegue" not in texto_desv:
        err("P14", f"precio del despegue dicho ({prec}) != catálogo ({CATALOGO['despegue_precio']})")

    # ---- P15 / P17 agenda
    if not agenda:
        err("P15", "agenda_diagnostico[] vacía: el prospecto no produce insumo para el diagnóstico")
    for i, a in enumerate(agenda):
        aid = a.get("id") or f"agenda[{i}]"
        for c in ("pregunta_sugerida", "campo_destino", "por_que_importa",
                  "quien_debe_responder", "prioridad", "momento", "deriva_de"):
            if not a.get(c):
                err("P15", f"agenda '{aid}': falta '{c}'")
        if a.get("prioridad") not in PRIORIDADES:
            err("P15", f"agenda '{aid}': prioridad '{a.get('prioridad')}' fuera del enum")
        if a.get("momento") not in MOMENTOS:
            err("P15", f"agenda '{aid}': momento '{a.get('momento')}' fuera del enum")
        for tok in _tokens(a.get("deriva_de")):
            if tok.startswith(("objecion:", "pregunta_sin_responder:", "requisito:")):
                continue
            if tok in ids_vacios or tok in ids_hipotesis:
                continue
            if any(_igual_dolor(did, tok) for did in ids_dolores):
                continue
            err("P15", f"agenda '{aid}': deriva_de '{tok}' no resuelve a ningún vacío, hipótesis, dolor u objeción")
        cd = a.get("campo_destino") or ""
        if cd.startswith("habilitacion_meta") and a.get("momento") != "evidencia_en_vivo":
            err("P17", f"agenda '{aid}': la habilitación Meta se verifica en pantalla "
                       f"(momento debe ser 'evidencia_en_vivo', es '{a.get('momento')}')")

    # ---- P16 no re-preguntar lo que ya se sabe (advertencia: el mapeo a ficha no es automático)
    conocidos = {ruta for ruta, d in datos
                 if d.get("fuente") in ("cliente_declaro", "cliente_confirmo")
                 and d.get("valor") != "no_capturado"}
    for a in agenda:
        cd = a.get("campo_destino") or ""
        if cd in ("no_aplica", "") or cd.endswith("*"):
            continue
        if any(r.endswith(cd) for r in conocidos):
            adv("P16", f"agenda '{a.get('id')}': campo_destino '{cd}' ya tiene dato declarado por el cliente "
                       "(debería confirmarse, no preguntarse)")

    # ---- advertencias
    dur = meta.get("duracion_demo_efectiva_min") or 0
    if dur > 20 and len(vacios) < 8:
        adv("A1", f"solo {len(vacios)} vacíos en una demo de {dur} min: revisar si la extracción inventó datos")
    if dolores and not any(d.get("citas") for d in dolores):
        adv("A2", "ningún dolor tiene cita textual")
    det = (p.get("origen_y_detonante", {}) or {}).get("detonante", []) or []
    if any(d.get("es_fecha_dura") for d in det):
        ns = cierres.get("next_step", {}) or {}
        if not ns.get("tiene_fecha"):
            adv("A3", "hay detonante con fecha dura y el next step quedó sin fecha (error comercial, no de extracción)")
    if dur > 15 and not ((p.get("reaccion_a_la_demo", {}) or {}).get("preguntas_del_cliente")):
        adv("A4", f"demo de {dur} min sin ninguna pregunta del cliente registrada")
    if objeciones:
        for i, o in enumerate(objeciones):
            if not o.get("cita"):
                adv("A2", f"objeciones[{i}] '{o.get('tipo')}' sin cita textual")


def _tokens(deriva):
    if not deriva:
        return []
    if isinstance(deriva, list):
        crudos = deriva
    else:
        crudos = str(deriva).split(",")
    return [t.strip() for t in crudos if t.strip()]


def _deriva_toca(a, ids):
    return bool(ids & set(_tokens(a.get("deriva_de"))))


def _igual_dolor(dolor_id, tok):
    return dolor_id == tok or dolor_id.startswith(tok + "-")


def _deriva_toca_dolor(a, dolor_id):
    return any(_igual_dolor(dolor_id, t) for t in _tokens(a.get("deriva_de")))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    ruta = args[0]
    if "--catalogo" in sys.argv:
        cat_path = sys.argv[sys.argv.index("--catalogo") + 1]
        with open(cat_path, encoding="utf-8") as f:
            CATALOGO.update(json.load(f))
    try:
        with open(ruta, encoding="utf-8") as f:
            p = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[P18] el JSON no parsea: {e}")
        return 1

    validar(p)

    print(f"== {ruta}")
    if errores:
        print(f"\nERRORES ({len(errores)}):")
        for e in errores:
            print(f"  ✗ {e}")
    if advertencias:
        print(f"\nADVERTENCIAS ({len(advertencias)}):")
        for a in advertencias:
            print(f"  ! {a}")
    if not errores and not advertencias:
        print("\nSin errores ni advertencias.")
    elif not errores:
        print(f"\nSin errores. {len(advertencias)} advertencia(s) para revisar a mano.")
    print()
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
