#!/usr/bin/env python3
"""Materializa propuesta.json desde un borrador de selección + la librería compilada.

Uso:
    python3 construir_propuesta.py borrador.json libreria/componentes.json propuesta.json

POR QUÉ EXISTE
--------------
La librería compilada y el contrato de la propuesta llaman distinto a los mismos
campos. Hasta ago-2026 esa traducción no vivía en ningún lado: la tenía que recordar
quien armaba la propuesta a mano, corrida por corrida. En la corrida v4 de Bifteki se
leyó la clave equivocada, los 56 componentes salieron con 'vis' y 'journey' en null,
el validador dio exit 0 (no los miraba) y el renderizador rechazó el archivo entero.

Este script es el único lugar donde esa traducción está escrita. Si la librería gana
o renombra un campo, se toca MAPA_LIBRERIA y nada más.

REPARTO DE RESPONSABILIDADES (regla de la casa)
-----------------------------------------------
- El MODELO decide QUÉ: qué componentes aplican, con qué razón se excluyen los demás,
  qué instancias fija el consultor, el titular, el as-is, las advertencias. Todo eso
  entra por el borrador.
- ESTE SCRIPT decide la FORMA: copia de la librería los campos que el renderizador
  exige, con los nombres que el contrato pide, sin inventar ninguno.
- calcular_condicion.py decide CUÁNTO: instancias, multiplicador y precios. Este
  script NO escribe cifras — deja 'instancias' en su valor de partida y espera que
  calcular_condicion.py corra después.

FORMATO DEL BORRADOR
--------------------
Todo lo que el modelo decide, tal cual va a la propuesta, más dos bloques propios:

    "seleccion":   { "<id-componente>": null | <int> }
                   null  = las instancias las calcula calcular_condicion.py
                   <int> = el consultor las fija (se marca instancias_fijadas_por_consultor)
    "exclusiones": { "<id-componente>": "razón en lenguaje del cliente" }
    "cuotas":      { "<id-componente>": "hasta 3 formularios embebibles" }   (opcional)

El resto de las claves del borrador (cliente, titular, resumen, as_is, fugas, madurez,
integraciones, advertencias, plan_recomendado, condicion_comercial…) se copian sin tocar.
"""
import json
import sys

# --- La traducción. Es el motivo de este archivo: un solo lugar, comentado. ---
# contrato de la propuesta  <-  columna de la librería compilada
MAPA_LIBRERIA = {
    'nombre_cliente': 'nombre_cliente',
    'tipo':           'tipo',
    'vis':            'visibilidad_cliente',   # ← el que costó la carga fallida
    'journey':        'posicion_journey',      # ← el otro
    'inst_por':       'se_instancia_por',
    'aplica_si':      'aplica_si',
    'modulo_archivo': '_archivo',
    'cierra':         'cierra_fugas',
}

VIS_OK = {'front', 'back', 'ambos'}


def construir(borrador, lib):
    comps_lib = lib.get('componentes', lib)
    seleccion = borrador.pop('seleccion', {})
    exclusiones = borrador.pop('exclusiones', {})
    cuotas = borrador.pop('cuotas', {})

    desconocidos = [c for c in list(seleccion) + list(exclusiones) if c not in comps_lib]
    if desconocidos:
        raise SystemExit(f"✖ ids que no existen en la librería: {desconocidos}\n"
                         "  La selección no inventa componentes: se corrige el borrador "
                         "o se recompila la librería.")

    componentes = {}
    for cid, fijadas in seleccion.items():
        ref = comps_lib[cid]
        plan = ref.get('plan_minimo')
        if plan is None:
            raise SystemExit(f"✖ '{cid}' tiene plan_minimo null en la librería (V11): "
                             "va al carril de integraciones, no dentro de un plan.")
        c = {'id': cid}
        for destino, origen in MAPA_LIBRERIA.items():
            c[destino] = ref.get(origen)
        c['plan'] = plan
        c['cuota'] = cuotas.get(cid)
        # Valor de partida. calcular_condicion.py lo sobrescribe salvo que esté fijado.
        c['instancias'] = 1
        if fijadas is not None:
            c['instancias'] = int(fijadas)
            c['instancias_fijadas_por_consultor'] = True
        componentes[cid] = c

    # Compuerta local: si la librería no trae el dato, el renderizador no lo va a
    # inventar. Mejor fallar aquí que en la carga, delante del cliente.
    rotos = [(cid, k, c[k]) for cid, c in componentes.items()
             for k in ('vis', 'journey')
             if (k == 'vis' and c[k] not in VIS_OK)
             or (k == 'journey' and not isinstance(c[k], int))]
    if rotos:
        raise SystemExit("✖ campos que el renderizador exige y la librería no entregó:\n" +
                         "\n".join(f"    {cid}.{k} = {v!r}" for cid, k, v in rotos) +
                         "\n  Revisar la librería compilada o MAPA_LIBRERIA.")

    borrador['componentes'] = componentes
    borrador['no_aplican'] = [[comps_lib[cid]['nombre_cliente'], razon]
                              for cid, razon in exclusiones.items()]
    return borrador


if __name__ == '__main__':
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    borrador = json.load(open(sys.argv[1]))
    lib = json.load(open(sys.argv[2]))
    prop = construir(borrador, lib)
    json.dump(prop, open(sys.argv[3], 'w'), ensure_ascii=False, indent=1)

    from collections import Counter
    por_plan = dict(Counter(c['plan'] for c in prop['componentes'].values()))
    fijadas = sum(1 for c in prop['componentes'].values()
                  if c.get('instancias_fijadas_por_consultor'))
    print(f"✔ {len(prop['componentes'])} componentes · {len(prop['no_aplican'])} exclusiones "
          f"· {len(prop.get('integraciones', []))} en el carril")
    print(f"  por plan: {por_plan} · instancias fijadas por el consultor: {fijadas}")
    print(f"✔ escrito en {sys.argv[3]}")
    print("  SIGUIENTE: calcular_condicion.py (instancias, multiplicador y precios) "
          "y después validar_propuesta.py.")
