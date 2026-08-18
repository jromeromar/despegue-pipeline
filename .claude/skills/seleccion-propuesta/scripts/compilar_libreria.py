#!/usr/bin/env python3
"""Compila la librería (modulo-*.md) a componentes.json.
Uso: python3 compilar_libreria.py <carpeta-con-modulos> [salida.json]
Se corre una vez por versión de librería; el JSON resultante es el que
consumen la selección y el renderizador (y el que se sube a Orion)."""
import json, re, sys, glob, os, hashlib

def txt(v):
    return re.sub(r'\s+#.*$', '', (v or '')).strip().strip('"')

def compilar(carpeta):
    comps, errores = {}, []
    archivos = sorted(glob.glob(os.path.join(carpeta, 'modulo-*.md')))
    if not archivos:
        errores.append(f"cero archivos modulo-*.md en {carpeta}")
    for f in archivos:
        contenido = open(f, encoding='utf-8').read()
        for blk in re.findall(r'```yaml\n(.*?)\n```', contenido, re.S):
            d = dict(re.findall(r'^([a-z_]+): (.*)$', blk, re.M))
            if 'id' not in d:
                continue
            cid = txt(d['id'])
            if cid in comps:
                errores.append(f"id duplicado: {cid} ({f} y {comps[cid]['_archivo']})")
            plan = txt(d.get('plan_minimo'))
            comps[cid] = {
                'id': cid,
                'nombre_interno': txt(d.get('nombre_interno')),
                'nombre_cliente': txt(d.get('nombre_cliente')),
                'tipo': txt(d.get('tipo')),
                'plan_minimo': None if plan in ('null', '', 'None') else plan,
                'visibilidad_cliente': txt(d.get('visibilidad_cliente')),
                'posicion_journey': int(txt(d.get('posicion_journey')) or 0),
                'se_instancia_por': txt(d.get('se_instancia_por')),
                'aplica_si': txt(d.get('aplica_si')) or 'siempre',
                'cierra_fugas': re.findall(r'[A-Z]+-\d+', d.get('cierra_fugas', '')),
                'mecanismo_entrega': txt(d.get('mecanismo_entrega')),
                'costo_externo': txt(d.get('costo_externo')) or None,
                '_archivo': os.path.basename(f),
            }
            # validaciones de compilación (subset de V1-V11 verificable aquí)
            c = comps[cid]
            if not c['nombre_cliente']:
                errores.append(f"{cid}: sin nombre_cliente")
            if c['plan_minimo'] not in (None, 'fundamental', 'avanzado', 'inteligente'):
                errores.append(f"{cid}: plan_minimo inválido '{c['plan_minimo']}'")
            if not c['visibilidad_cliente'] and c['tipo'] not in ('integracion',):
                errores.append(f"{cid}: sin visibilidad_cliente (V10 la necesita)")
            # V11: integración no nativa no puede tener plan
            if c['tipo'] == 'integracion':
                blk_low = blk.lower()
                nativa = 'mecanismo: nativa' in blk_low or 'mecanismo: "nativa"' in blk_low
                if not nativa and c['plan_minimo'] is not None:
                    errores.append(f"{cid}: V11 — integración no nativa con plan_minimo={c['plan_minimo']}")
    version = hashlib.sha1(json.dumps(comps, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:10]
    return {'_meta': {'total': len(comps), 'version': version, 'fuente': carpeta},
            'componentes': comps}, errores

if __name__ == '__main__':
    carpeta = sys.argv[1]
    salida = sys.argv[2] if len(sys.argv) > 2 else 'componentes.json'
    lib, errs = compilar(carpeta)
    for e in errs: print('✖', e)
    if errs: sys.exit(1)
    json.dump(lib, open(salida, 'w'), ensure_ascii=False, indent=1)
    planes = {}
    for c in lib['componentes'].values():
        planes[c['plan_minimo']] = planes.get(c['plan_minimo'], 0) + 1
    print(f"✔ {lib['_meta']['total']} componentes → {salida} · versión {lib['_meta']['version']}")
    print('  por plan:', planes)
