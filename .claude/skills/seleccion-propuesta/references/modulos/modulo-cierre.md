# Módulo Cierre — Librería de componentes v0.1

9 componentes conforme al schema v0.2.1. Cierre = de la propuesta formal a la
firma y el pago. **Fronteras**: el seguimiento del interesado sin propuesta es
Nutrición; lo que pasa después de la firma (onboarding, recompra) es
Fidelización; los tableros de cierre viven en Tableros.

---

## A. Componentes

### Propuesta (posicion_journey 70–76)

```yaml
id: cierre-cotizador
nombre_interno: "Generador de propuestas/cotizaciones desde el CRM con historial"
nombre_cliente: "Propuestas profesionales en minutos, con registro de cada versión enviada"
tipo: propuesta_comercial
visibilidad_cliente: front
posicion_journey: 70
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "linea.mecanismo_de_cierre in [venta_directa, contrato_recurrente]"
depende_de: [gestion-pipeline-demandante, gestion-campos-calificacion]
cierra_fugas: []                          # habilita F-04: sin propuesta rastreada no hay retoma posible
metrica_que_habilita: [propuestas_enviadas, valor_propuesto_mes]
esfuerzo_base: 3
esfuerzo_por_instancia: 2
detalle:
  plantilla_ref: propuesta-por-linea
  vigencia_dias: 15
  datos_requeridos:
    - { campo: item_de_interes, fuente: crm }
    - { campo: precio_y_condiciones, fuente: catalogo }
  seguimiento: { rastrea_apertura: true, automatizacion_ref: cierre-secuencia-propuesta }
  aceptacion: { mecanismo: aceptacion_en_linea, cambia_etapa_a: aceptada }
```

```yaml
id: cierre-secuencia-propuesta
nombre_interno: "Secuencia de retoma post-propuesta (D+1, D+3, D+7) con expiración"
nombre_cliente: "Ninguna cotización vuelve a morir en visto"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 72
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
depende_de: [cierre-cotizador, nutricion-plantillas-whatsapp]
cierra_fugas: [F-04]                      # la fuga más rentable: intención ya demostrada
metrica_que_habilita: [propuestas_sin_respuesta, recuperadas_post_propuesta, ciclo_propuesta_decision]
esfuerzo_base: 2
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: propuesta_enviada, condicion: "sin respuesta" }
  acciones:
    - { orden: 1, tipo: mensaje, canal: whatsapp, plantilla_ref: propuesta-d1, espera_min: 1440 }
    - { orden: 2, tipo: mensaje, canal: whatsapp, plantilla_ref: propuesta-d3-dudas, espera_min: 4320 }
    - { orden: 3, tipo: crear_tarea, asigna_a_funcion: closer, espera_min: 10080 }
    - { orden: 4, tipo: mensaje, plantilla_ref: propuesta-vence, condicion: "vigencia - 2 días" }
  condiciones_salida: [acepto, rechazo_con_motivo, renegociacion]
  ramas:
    - { condicion: "expiró sin respuesta", acciones: [{ tipo: mover_a_etapa, condicion: perdida }, { tipo: registrar_motivo, condicion: sin_respuesta }, { tipo: etiquetar, condicion: candidato_reactivacion }] }
```

```yaml
id: cierre-aprobaciones-internas
nombre_interno: "Flujo de aprobación con SLA: descuentos, condiciones, revisión legal"
nombre_cliente: "La aprobación que hoy se pide por pasillo queda pedida, medida y respondida"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 74
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [unico]                 # un flujo con ramas por punto de aprobación
aplica_si: "existe estructura.puntos_de_aprobacion"
depende_de: [gestion-pipeline-demandante, gestion-permisos-roles]
cierra_fugas: []
metrica_que_habilita: [aprobaciones_solicitadas, ciclo_aprobacion_interna, aprobaciones_vencidas]
esfuerzo_base: 3
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: cambio_etapa, condicion: "requiere aprobación (descuento > umbral, contrato no estándar)" }
  acciones:
    - { orden: 1, tipo: crear_tarea, asigna_a_funcion: aprobador_comercial_o_revisor_legal }
    - { orden: 2, tipo: notificar, canal: whatsapp }
    - { orden: 3, tipo: escalar, asigna_a_funcion: coordinador, espera_min: 1440 }
  nota: "Cada punto de aprobación de la ficha B es una rama. El pipeline no avanza sin resolución registrada."
```

### Ejecución del cierre (78–84)

```yaml
id: cierre-contrato-firma
nombre_interno: "Contrato con firma electrónica y disparo de post-firma"
nombre_cliente: "Del sí a la firma sin imprimir, escanear ni perseguir a nadie"
tipo: documento_firmable
visibilidad_cliente: front
posicion_journey: 78
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
depende_de: [cierre-cotizador]
cierra_fugas: []
metrica_que_habilita: [contratos_enviados, tasa_firma_contrato, ciclo_aceptacion_firma]
esfuerzo_base: 3
esfuerzo_por_instancia: 1
prerequisito_plataforma: ["Minutas por línea aprobadas por el cliente (y su revisor legal si existe)"]
detalle:
  proposito: contrato
  datos_requeridos:
    - { campo: datos_completos_cliente, fuente: crm }
    - { campo: condiciones_aceptadas, fuente: crm }
  mecanismo_firma: firma_electronica
  accion_post_firma: { cambia_etapa_a: cerrada_ganada, notifica_a_funcion: postventa_administracion }
```

```yaml
id: cierre-pago-enlace
nombre_interno: "Enlace de pago para anticipo/separación con conciliación al CRM"
nombre_cliente: "El cliente decide y paga en el mismo momento, desde el mismo chat"
tipo: integracion
visibilidad_cliente: front
posicion_journey: 80
plan_minimo: avanzado
mecanismo_entrega: configuracion_cuenta
se_instancia_por: [unico]
aplica_si: "el cierre incluye anticipo, separación o matrícula cobrable en línea"
depende_de: [cierre-contrato-firma]
cierra_fugas: []
metrica_que_habilita: [pagos_generados, tasa_pago_enlace, ciclo_firma_pago]
esfuerzo_base: 3
esfuerzo_por_instancia: 0
prerequisito_plataforma: ["Pasarela habilitada (credenciales no viajan en snapshot)"]
detalle:
  sistema: pasarela_de_pago
  direccion: bidireccional
  objetos_sincronizados: [pagos, estado_oportunidad]
  mecanismo: nativa
```

```yaml
id: cierre-acompanamiento-subasta
nombre_interno: "Secuencia de acompañamiento al cronograma de subasta/licitación"
nombre_cliente: "El interesado llega a la subasta con documentos listos y fechas claras"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 79
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "linea.mecanismo_de_cierre in [subasta, licitacion]"
depende_de: [gestion-pipeline-demandante, nutricion-plantillas-whatsapp]
cierra_fugas: []
mitiga_fugas: [F-05]                      # el no-show de subasta: inscrito que no puja
metrica_que_habilita: [inscritos_por_evento, tasa_participacion_subasta, documentos_completos_pct]
esfuerzo_base: 4
esfuerzo_por_instancia: 2
detalle:
  disparador: { tipo: entrada_a_etapa, condicion: "interes_formalizado con evento fechado" }
  acciones:
    - { orden: 1, tipo: mensaje, plantilla_ref: checklist-documentos, espera_min: 0 }
    - { orden: 2, tipo: mensaje, plantilla_ref: recordatorio-cierre-inscripcion, condicion: "D-5 del evento" }
    - { orden: 3, tipo: mensaje, plantilla_ref: recordatorio-evento, condicion: "D-1" }
    - { orden: 4, tipo: crear_tarea, asigna_a_funcion: asesor, condicion: "documentos incompletos a D-3" }
  nota: "El cronograma es del proceso, no del asesor: sin esta secuencia el cliente depende de que alguien se acuerde."
```

### Señales de decisión (85+)

```yaml
id: cierre-señales-decision
nombre_interno: "Alertas por comportamiento sobre la propuesta: aperturas, relecturas, reenvíos"
nombre_cliente: "Tu closer llama exactamente cuando el cliente está mirando la propuesta"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 85
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [cierre-cotizador, gestion-scoring-contacto]
cierra_fugas: []
mitiga_fugas: [F-04]
metrica_que_habilita: [aperturas_propuesta, tiempo_señal_a_llamada]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: señal_comportamiento, filtros: [apertura_propuesta, relectura, clic_condiciones] }
  acciones:
    - { orden: 1, tipo: sumar_score }
    - { orden: 2, tipo: notificar, asigna_a_funcion: closer, condicion: "2+ aperturas en 24h" }
```

```yaml
id: cierre-recuperacion-ia
nombre_interno: "IA de retoma sobre propuestas frías: resuelve dudas y renegocia condiciones simples"
nombre_cliente: "Las propuestas que nadie retomaría las retoma un asistente que sí sabe qué ofrecer"
tipo: chatbot_ia
visibilidad_cliente: front
posicion_journey: 86
plan_minimo: inteligente
mecanismo_entrega: contenido_a_medida
se_instancia_por: [linea_negocio]
depende_de: [cierre-secuencia-propuesta, gestion-chatbot-precalificacion]
cierra_fugas: []
mitiga_fugas: [F-04]
metrica_que_habilita: [propuestas_retomadas_ia, cierres_asistidos_ia]
esfuerzo_base: 4
esfuerzo_por_instancia: 2
prerequisito_plataforma: ["Reglas de negociación aprobadas: qué puede ofrecer la IA y qué escala (O-01)"]
detalle:
  alcance: [dudas_de_propuesta, vigencia, condiciones_estandar]
  criterio_escalamiento: "solicitud de descuento fuera de regla o intención de cierre"
  handoff_a_funcion: closer
```

```yaml
id: cierre-aprobacion-por-umbral
nombre_interno: "Auto-aprobación por umbrales: lo estándar no espera a nadie"
nombre_cliente: "Los descuentos dentro de política se aprueban solos; el aprobador solo ve excepciones"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 87
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [unico]
aplica_si: "existe estructura.puntos_de_aprobacion"
depende_de: [cierre-aprobaciones-internas]
cierra_fugas: []
metrica_que_habilita: [pct_autoaprobado, excepciones_mes]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: solicitud_aprobacion }
  ramas:
    - { condicion: "dentro de política (descuento <= umbral, contrato estándar)", acciones: [{ tipo: aprobar_y_avanzar }, { tipo: registrar_en_log }] }
    - { condicion: "fuera de política", acciones: [{ tipo: derivar_a, asigna_a_funcion: aprobador_comercial }] }
  nota: "Requiere que el cliente formalice su política. Si la política no existe, este componente la fuerza a existir — y eso es parte del valor."
```

### Validaciones del módulo

- **V1** ✔ señales-decision y recuperacion-ia (inteligente) dependen de
  componentes fundamental/avanzado/inteligente coherentes; aprobacion-por-umbral
  (inteligente) sobre aprobaciones-internas (fundamental).
- **V2** ✔ Referencias a Gestión y Nutrición existen en sus archivos.
- **V6** ✔ F-04 cerrada por secuencia-propuesta; mitigada además por señales y
  recuperación IA. F-05 en contexto subasta solo mitigada (la participación
  final no la controla Ropofy).
- **V7** ✔ Journey 70–87, después de Nutrición (50–66).
- **Anti-F-17**: la propuesta expirada registra motivo y se etiqueta para
  Reactivación — misma disciplina que Nutrición: clasificar, nunca descartar.

---

## B. Validación contra el piloto

| Componente | Instancias | Detalle |
|---|---|---|
| cotizador | 2 | venta directa (privados/societarios) y arriendo. **No aplica a subasta**: allí la "propuesta" es el cronograma del evento |
| secuencia-propuesta | 2 | mismas líneas |
| acompanamiento-subasta | 1 | **el componente estrella del módulo para este cliente**: cronogramas de subasta, checklist de documentos financieros, recordatorios D-5/D-1. Hoy nada de eso existe y es su mecanismo de cierre dominante |
| aprobaciones-internas | 1 | semáforos de precio y validaciones que hoy se piden por pasillo |
| contrato-firma | 1–2 | contratos de arriendo; mandatos de administración |
| pago-enlace | por validar | depende de si separación/anticipo se cobra en línea — dato no capturado en la sesión |
| recuperacion-ia | 2 | venta directa y arriendo |

Esfuerzo Cierre plan Inteligente: ~26 base + ~11 instancias ≈ **37 puntos ≈ 18
jornadas**. Acumulado Gestión + Nutrición + Cierre: ~163 puntos.

Hallazgo del piloto aplicado: en subasta, `cierre-cotizador` no aplica y el eje
del cierre es el evento fechado. `mecanismo_de_cierre` volvió a demostrar que es
un eje estructural: cambia qué componentes existen, no solo cuántas instancias.

---

## C. Métricas agregadas al diccionario (v0.3)

| id | Definición | Fuente |
|---|---|---|
| `propuestas_enviadas` / `valor_propuesto_mes` | Propuestas emitidas y su valor total | cotizador |
| `propuestas_sin_respuesta` | Propuestas activas sin reacción del contacto a los N días | secuencia-propuesta |
| `recuperadas_post_propuesta` | Propuestas que avanzan tras entrar a la secuencia. **Medición real de `tasa_recuperacion_propuesta` de la fórmula F-04** | secuencia-propuesta |
| `ciclo_propuesta_decision` | Mediana de días entre envío y decisión (acepta/rechaza/expira) | secuencia-propuesta |
| `aprobaciones_solicitadas` / `ciclo_aprobacion_interna` / `aprobaciones_vencidas` | Volumen, latencia y mora de los gateways internos | aprobaciones-internas |
| `contratos_enviados` / `tasa_firma_contrato` / `ciclo_aceptacion_firma` | Embudo de firma | contrato-firma |
| `pagos_generados` / `tasa_pago_enlace` / `ciclo_firma_pago` | Embudo de pago | pago-enlace |
| `inscritos_por_evento` / `tasa_participacion_subasta` / `documentos_completos_pct` | Embudo del evento de cierre | acompanamiento-subasta |
| `aperturas_propuesta` / `tiempo_señal_a_llamada` | Señales de decisión y reacción del closer | señales-decision |
| `propuestas_retomadas_ia` / `cierres_asistidos_ia` | Retoma automática de propuestas frías | recuperacion-ia |
| `pct_autoaprobado` / `excepciones_mes` | Salud de la política de aprobación | aprobacion-por-umbral |

---

## D. Pendientes y frontera

1. Plantillas del módulo (propuesta-d1/d3/vence, checklist-documentos,
   recordatorios de evento): redacción por industria en los snapshots.
2. `cierre-pago-enlace` reveló un dato que el guión no pregunta directo: **si el
   anticipo/separación se cobra en línea hoy o podría cobrarse**. Candidato a
   repregunta del Bloque 7.
3. **La frontera se sostiene por tercera vez**: Fundamental = ninguna propuesta
   ni aprobación se pierde (cobertura); Avanzado = el cierre se ejecuta digital
   — contrato, pago, evento (sustancia); Inteligente = el sistema detecta la
   decisión y actúa solo (iniciativa). Patrón **cobertura → sustancia →
   iniciativa** confirmado en 3 de 7 módulos.
