# Módulo Reactivación — Librería de componentes v0.1

8 componentes conforme al schema v0.2.2. Reactivación = volver a poner en juego
contactos que ya existieron: bases antiguas, leads desatendidos, dormidos que
Nutrición y Cierre etiquetaron. **Fronteras**: mantener vivo al interesado
activo es Nutrición; el ex-cliente que recompra es Fidelización.

Dos poblaciones distintas que este módulo trata igual en mecánica y distinto en
mensaje: la **base histórica** (meses o años, F-10) y el **represamiento
reciente** (leads que entraron y nadie atendió — las 3.900 del piloto). La
segunda es más valiosa y más urgente: su intención aún respira.

---

## A. Componentes

### Preparación (posicion_journey 90–93)

```yaml
id: reactivacion-importacion-depuracion
nombre_interno: "Importación, deduplicación y verificación de consentimiento de bases existentes"
nombre_cliente: "Todo contacto que alguna vez llegó, limpio y listo para volver a trabajarse"
tipo: migracion_datos
visibilidad_cliente: back
posicion_journey: 90
plan_minimo: avanzado
mecanismo_entrega: configuracion_cuenta
se_instancia_por: [unico]                 # una operación que consume N fuentes
depende_de: [gestion-base-contactos]
cierra_fugas: []                          # habilita F-10; sin esto la campaña dispara a ciegas
metrica_que_habilita: [base_importada, contactos_utilizables_pct]
esfuerzo_base: 3
esfuerzo_por_instancia: 0
prerequisito_plataforma: ["Base legal de contacto verificable (consentimiento o relación previa); sin ella, la reactivación expone al cliente y quema la línea"]
detalle:
  fuentes:
    - { sistema: exportes_whatsapp_y_excel, formato: csv, volumen_estimado: por_ficha }
    - { sistema: crm_abandonado, formato: api_o_export, volumen_estimado: por_ficha }
    - { sistema: bandejas_de_portales_y_email, formato: manual_asistido, volumen_estimado: por_ficha }
  operaciones: [deduplicar, normalizar_telefonos, verificar_consentimiento, etiquetar_origen]
  destino: { objeto: contacto, segmento_ref: reactivacion-segmentos-dormidos }
  es_recurrente: false
```

```yaml
id: reactivacion-segmentos-dormidos
nombre_interno: "Segmentación de dormidos por origen, antigüedad, línea e interés conocido"
nombre_cliente: "No es una bolsa de 4.000 números: son grupos con historia, y cada uno recibe lo suyo"
tipo: segmento
visibilidad_cliente: back
posicion_journey: 92
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [reactivacion-importacion-depuracion, nutricion-segmentos]
cierra_fugas: []
metrica_que_habilita: [dormidos_por_segmento, antiguedad_promedio_base]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  mecanismo: smart_list
  criterios: [origen(base_historica | represado_reciente | etiqueta_nutricion | etiqueta_cierre), antiguedad, linea_de_interes, ultimo_estado_conocido]
  uso: [reactivacion-campana-oleadas, reactivacion-disparadores-evento]
  nota: "Los dormidos de Nutrición y las propuestas expiradas de Cierre entran aquí solos — el módulo se autoalimenta (anti F-17)."
```

### Campaña (94–97)

```yaml
id: reactivacion-campana-oleadas
nombre_interno: "Campaña masiva WhatsApp por oleadas con throttling y monitoreo de calidad de línea"
nombre_cliente: "La base se despierta por tandas, sin arriesgar el número que está impreso en todas partes"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 94
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [unico]                 # un motor de oleadas que consume segmentos
depende_de: [reactivacion-segmentos-dormidos, nutricion-plantillas-whatsapp]
cierra_fugas: [F-10]
metrica_que_habilita: [enviados_por_oleada, tasa_entrega_masiva, tasa_respuesta_reactivacion, calidad_linea_whatsapp]
esfuerzo_base: 3
esfuerzo_por_instancia: 0
prerequisito_plataforma: ["Plantillas de reactivación aprobadas por Meta", "R-02: límites de escalamiento de Meta por calidad — el volumen diario se gana, no se decreta"]
detalle:
  disparador: { tipo: oleada_programada, condicion: "segmento priorizado" }
  acciones:
    - { orden: 1, tipo: mensaje, canal: whatsapp, plantilla_ref: reactivacion-por-segmento }
    - { orden: 2, tipo: monitorear_calidad, condicion: "pausa automática si el rating de la línea baja" }
  ramas:
    - { condicion: respondio, acciones: [{ tipo: derivar_a, condicion: reactivacion-absorcion-oleadas }] }
    - { condicion: opt_out, acciones: [{ tipo: marcar_no_contactar }] }
    - { condicion: sin_respuesta_2_oleadas, acciones: [{ tipo: mover_a, condicion: archivo_frio }] }
  nota: "Prioridad de oleadas: represado_reciente primero (intención viva), base histórica después. Nunca big-bang: la primera oleada calibra plantilla y tasa de respuesta."
```

```yaml
id: reactivacion-absorcion-oleadas
nombre_interno: "IA que absorbe la oleada de respuestas: clasifica, actualiza la línea de interés y rutea"
nombre_cliente: "Cuando 400 dormidos contestan el mismo día, nadie del equipo se ahoga"
tipo: chatbot_ia
visibilidad_cliente: front
habilidad: reactivador
posicion_journey: 95
plan_minimo: avanzado
mecanismo_entrega: contenido_a_medida
se_instancia_por: [linea_negocio]
depende_de: [reactivacion-campana-oleadas, gestion-asistente-informativo, gestion-ruteo-intencion]
cierra_fugas: []
mitiga_fugas: [F-08]                      # la campaña genera su propio pico de volumen
metrica_que_habilita: [respuestas_atendidas_ia, reactivados_a_pipeline, descartados_con_motivo]
esfuerzo_base: 4
esfuerzo_por_instancia: 2
detalle:
  alcance: [confirmar_interes_vigente, clasificar_respuesta, actualizar_linea_de_interes, agendar_o_rutear]
  criterio_escalamiento: "interes transaccional confirmado"
  handoff_a_funcion: asesor
  horario_activo: 24_7
  nota: "Sin este componente, la campaña masiva reproduce el represamiento que vino a resolver. Campaña sin capacidad de respuesta es F-08 autoinfligida."
```

```yaml
id: reactivacion-oferta-reenganche
nombre_interno: "Piezas de reenganche por segmento: motivo real para volver"
nombre_cliente: "El mensaje no es '¿sigues interesado?' — es 'esto cambió desde la última vez'"
tipo: contenido
visibilidad_cliente: front
posicion_journey: 93
plan_minimo: avanzado
mecanismo_entrega: contenido_a_medida
se_instancia_por: [linea_negocio]
depende_de: []
cierra_fugas: []
mitiga_fugas: [F-10]
metrica_que_habilita: []
esfuerzo_base: 3
esfuerzo_por_instancia: 2
detalle:
  piezas:
    - { tipo: plantilla_reenganche_por_segmento, cantidad: 3, quien_produce: ropofy_con_insumos_cliente }
  nota: "Qué cambió: catálogo nuevo, condiciones nuevas, proceso más simple. El reenganche genérico rinde una fracción del específico y gasta la misma calidad de línea."
```

### Motor permanente (98+)

```yaml
id: reactivacion-disparadores-evento
nombre_interno: "Reactivación disparada por eventos del negocio hacia dormidos compatibles"
nombre_cliente: "Entró inventario nuevo o bajó un precio: los dormidos que encajan se enteran solos"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 98
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "catalogo.catalogo_estructurado in [si, parcial]"
depende_de: [reactivacion-segmentos-dormidos, nutricion-nueva-oportunidad-catalogo]
cierra_fugas: []
mitiga_fugas: [F-10]
metrica_que_habilita: [reactivaciones_por_evento, conversion_reactivacion_evento]
esfuerzo_base: 3
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: evento_negocio, filtros: [nuevo_lote_catalogo, baja_de_precio, nuevo_evento_de_cierre] }
  acciones:
    - { orden: 1, tipo: match, condicion: "atributos del evento vs interés conocido del dormido" }
    - { orden: 2, tipo: mensaje, plantilla_ref: reenganche-por-evento }
```

```yaml
id: reactivacion-ciclo-permanente
nombre_interno: "Motor cíclico: cada N días evalúa el archivo de dormidos y decide a quién despertar"
nombre_cliente: "La reactivación deja de ser una campaña que alguien recuerda hacer: corre sola"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 99
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [reactivacion-campana-oleadas, gestion-scoring-contacto]
cierra_fugas: []
mitiga_fugas: [F-10]
metrica_que_habilita: [dormidos_evaluados_ciclo, tasa_despertar_ciclo]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: programado, condicion: "cada 30 días" }
  acciones:
    - { orden: 1, tipo: evaluar, condicion: "score + antigüedad + señales desde el último intento" }
    - { orden: 2, tipo: encolar_en_oleada, condicion: "candidatos sobre umbral" }
  nota: "Cierra el ciclo de vida completo: Gestión captura → Nutrición sostiene → Cierre convierte → lo que cae vuelve por aquí. Nada sale del sistema sin decisión."
```

```yaml
id: reactivacion-tablero-campana
nombre_interno: "Vista operativa de la campaña: oleadas, respuesta, calidad de línea, pipeline generado"
nombre_cliente: "Ver en vivo cuánta plata dormida está despertando"
tipo: tablero
visibilidad_cliente: back
posicion_journey: 97
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [reactivacion-campana-oleadas]
cierra_fugas: []
metrica_que_habilita: []                  # consume métricas del módulo, no crea
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  audiencia_funcion: [coordinador]
  widgets:
    - { metrica: tasa_respuesta_reactivacion, fuente: reactivacion-campana-oleadas, visualizacion: serie }
    - { metrica: calidad_linea_whatsapp, fuente: reactivacion-campana-oleadas, visualizacion: semaforo }
    - { metrica: reactivados_a_pipeline, fuente: reactivacion-absorcion-oleadas, visualizacion: contador }
  frecuencia_revision: diaria_durante_campana
  nota: "Excepción consciente a la frontera con Tableros: la campaña necesita su vista operativa el día uno. V3 ✔: todas sus métricas nacen en este mismo módulo y plan (Avanzado)."
```

### Validaciones del módulo

- **V1** ✔ Los inteligentes dependen de fundamental/avanzado o entre sí;
  disparadores-evento (inteligente) depende de nueva-oportunidad-catalogo
  (avanzado) ✔.
- **V2** ✔ Referencias cruzadas existen en Gestión y Nutrición.
- **V3** ✔ El tablero del módulo solo consume métricas del propio módulo, plan
  fundamental.
- **V6** ✔ F-10 cerrada por campana-oleadas; el resto la mitiga por capas.
- **V7** ✔ Journey 90–99, el último tramo del ciclo.
- **Nota R-02 estructural**: el throttling y el monitoreo de calidad no son
  opcionales — son la diferencia entre reactivar la base y perder el número.

---

## B. Validación contra el piloto

El caso de uso es literal: las 3.900 conversaciones represadas son
`represado_reciente`, la población prioritaria del módulo.

| Componente | Instancias | Detalle |
|---|---|---|
| importacion-depuracion | 1 | Actichat (apagado) + bandejas de portales + correos que Jesús quiere redireccionar. Solo nombre y teléfono, sin segmentar — confirmado en sesión |
| segmentos-dormidos | 1 | origen: represado_reciente (3.900) + histórico de Wasi/Domus |
| campana-oleadas | 1 | oleadas priorizando lo reciente; el número está "impreso en todos los buses" en el caso análogo — R-02 aquí es crítico |
| precalificacion-ia | 2 | ventas y arriendos. Es exactamente lo que el consultor propuso en vivo: "envío masivo y los llevamos a un bot para precalificar" |
| oferta-reenganche | 2 | reenganche con novedad real: entregas masivas de inmuebles nuevos |
| disparadores-evento | 2 | cada entrega masiva de inmuebles = ronda automática a dormidos compatibles |
| tablero-campana | 1 | |

Esfuerzo Reactivación plan Inteligente: ~22 base + ~9 instancias ≈ **31 puntos
≈ 15 jornadas**. Acumulado 4 módulos: ~194 puntos.

Advertencia de secuencia para la propuesta: la campaña **no puede lanzarse antes
que Gestión esté operativo** (ruteo + asignación + IA). Despertar 3.900
contactos contra un equipo de 10 que ya no da abasto es fabricar F-08. La
dependencia técnica ya lo fuerza (V2), pero el cronograma de la propuesta debe
decirlo en palabras.

---

## C. Métricas agregadas al diccionario (v0.4)

| id | Definición | Fuente |
|---|---|---|
| `base_importada` / `contactos_utilizables_pct` | Volumen importado; % que sobrevive depuración y consentimiento | importacion-depuracion |
| `dormidos_por_segmento` / `antiguedad_promedio_base` | Composición del archivo de dormidos | segmentos-dormidos |
| `enviados_por_oleada` / `tasa_entrega_masiva` | Volumen y entregabilidad por oleada | campana-oleadas |
| `tasa_respuesta_reactivacion` | % de enviados que responde. **Medición real de `tasa_reactivacion` de la fórmula F-10 — el supuesto muere en la primera oleada** | campana-oleadas |
| `calidad_linea_whatsapp` | Rating de calidad de la línea en Meta. La métrica de supervivencia del canal | campana-oleadas |
| `respuestas_atendidas_ia` / `reactivados_a_pipeline` / `descartados_con_motivo` | Qué pasó con cada respuesta | precalificacion-ia |
| `reactivaciones_por_evento` / `conversion_reactivacion_evento` | Rendimiento del motor por eventos | disparadores-evento |
| `dormidos_evaluados_ciclo` / `tasa_despertar_ciclo` | Rendimiento del motor permanente | ciclo-permanente |

---

## D. Pendientes y frontera

1. Plantillas de reactivación por segmento e industria: con los snapshots.
2. La ficha no captura **base legal de contacto** de las bases históricas
   (consentimiento, relación previa). Candidato a campo en bloque D o F —
   decisión de negocio con implicación legal, mejor validarla con el cliente.
3. **Frontera ajustada por decisión de producto (ago-2026): el módulo completo
   arranca en Avanzado.** La reactivación es técnicamente sencilla pero exige
   trabajo real de limpieza y segmentación que no cabe en Fundamental. La
   promesa Fundamental de "nada sale del sistema sin decisión" se cumple igual:
   Gestión, Nutrición y Cierre etiquetan a los caídos como
   `candidato_reactivacion` — en Fundamental los caídos quedan **clasificados y
   en espera**; en Avanzado se despiertan (limpieza, oleadas, IA de respuesta);
   en Inteligente el despertar corre solo, por eventos y ciclos.
