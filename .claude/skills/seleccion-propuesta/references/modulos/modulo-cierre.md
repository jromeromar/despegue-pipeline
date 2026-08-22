# Módulo Cierre — Librería de componentes v0.1

15 componentes conforme al schema v0.2.1 — 14 dentro de planes y 1 en el carril
de integraciones. Cierre tiene **dos formas** que no se mezclan: el **ciclo
largo** (de la propuesta formal a la firma y el pago) y el **ciclo corto**, donde
el cierre y el primer contacto son el mismo momento y duran minutos. Cada
componente declara en su `aplica_si` a cuál pertenece, y por eso los dos juegos
se excluyen solos. **Fronteras**: el seguimiento del interesado sin propuesta es
Nutrición; lo que pasa después de la firma o de la entrega (onboarding, recompra)
es Fidelización; los tableros de cierre viven en Tableros.

---

## A. Componentes

### Propuesta formal (journeys 70, 72, 74)

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
aplica_si: "linea.mecanismo_de_cierre in [venta_directa, contrato_recurrente] and linea.ciclo_dias != 0"
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
aplica_si: "linea.ciclo_dias != 0"   # no_capturado NO excluye: solo excluye si se sabe que el ciclo es de cero días
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

### Ejecución del cierre formal (journeys 78, 79, 80)

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
aplica_si: "linea.ciclo_dias != 0"   # no_capturado NO excluye: solo excluye si se sabe que el ciclo es de cero días
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

### Señales de decisión (journeys 85, 86, 87)

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
aplica_si: "linea.ciclo_dias != 0"   # no_capturado NO excluye: solo excluye si se sabe que el ciclo es de cero días
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
habilidad: negociador
posicion_journey: 86
plan_minimo: inteligente
mecanismo_entrega: contenido_a_medida
se_instancia_por: [linea_negocio]
aplica_si: "linea.ciclo_dias != 0"   # no_capturado NO excluye: solo excluye si se sabe que el ciclo es de cero días
depende_de: [cierre-secuencia-propuesta, gestion-precalificador]
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

### Ciclo corto (el cierre es el primer contacto) — journeys 71, 73, 75, 77, 81, 83

En un negocio de ciclo corto —una casa de comidas, un domicilio, una venta de
mostrador— **el cierre y el primer contacto son el mismo momento y duran
minutos**: no hay cotización, ni aprobación interna, ni contrato, ni firma. Todo
lo anterior de este módulo no aplica, y lo que sí hace falta —confirmar el
pedido, mover sus estados, despachar la comanda al sector, avisar el despacho—
no existía: se cubría estirando `fidelizacion-onboarding-postfirma`, que es otra
cosa.

Los journeys se **intercalan** con los de las otras subsecciones a propósito: el
ciclo corto ocurre en las mismas posiciones del tramo Cierre, no después. Por eso
los títulos de las subsecciones enumeran sus journeys en vez de declarar rangos
—los rangos se pisarían— y por eso los cinco comparten un `aplica_si` que los
excluye solos donde el ciclo no es corto, mientras las otras subsecciones ganaron
el complemento (ver §Validaciones).

Verificado contra la documentación de la plataforma (19-ago-2026): salvo la
impresión térmica, **todo esto es nativo** — pipeline de Oportunidades con el
trigger de cambio de etapa, `Create/Update Opportunity`, WhatsApp con botones y
listas, notificación interna a usuarios o equipos, trigger de oportunidades
estancadas y formulario público para terceros sin asiento. No es desarrollo, es
empaquetado.

```yaml
id: cierre-confirmacion-pedido
nombre_interno: "Plantilla de confirmación de pedido con detalle, demora estimada y confirmación interactiva de dirección"
nombre_cliente: "El cliente recibe su pedido confirmado y cuánto va a demorar, sin que nadie escriba el mensaje"
tipo: plantilla_mensaje
visibilidad_cliente: front
posicion_journey: 71
plan_minimo: fundamental
mecanismo_entrega: contenido_a_medida      # el texto final lo aprueba el cliente (regla global del copy)
se_instancia_por: [linea_negocio]
aplica_si: "linea.ciclo_dias == 0 and linea.mecanismo_de_cierre == venta_directa"
depende_de: [gestion-whatsapp-api, nutricion-plantillas-whatsapp]
cierra_fugas: []
mitiga_fugas: [F-19]                       # reduce el error de toma; la causa la elimina el pipeline de estados
metrica_que_habilita: [pedidos_confirmados, tiempo_a_confirmacion]
esfuerzo_base: 2                           # a calibrar
esfuerzo_por_instancia: 1                  # a calibrar
detalle:
  canal: whatsapp
  proposito: "confirmar el pedido tomado: qué lleva, cuánto es, cuánto demora y a dónde va"
  variables: [nombre_contacto, detalle_pedido, total, demora_estimada, direccion_de_entrega]
  tono: cercano_y_breve
  requiere_aprobacion_meta: false          # el cliente acaba de escribir: la conversación está dentro de la ventana de 24 h
  nota: "Cuando hay que confirmar un dato con opciones se envía como mensaje interactivo — hasta 3 botones de respuesta rápida, o mensaje de lista si son más. El caso real es la dirección: «¿a tu casa, a la de tu mamá, o a otra?». El schema de plantilla_mensaje no tiene campo para la interactividad: se declara aquí y se especifica en la etapa 4."
```

```yaml
id: cierre-estados-del-pedido
nombre_interno: "Pipeline de pedido de ciclo corto: recibido → en preparación → despachado → entregado"
nombre_cliente: "Cada pedido con su estado visible: quién lo tiene, desde cuándo y qué falta"
tipo: pipeline
visibilidad_cliente: ambos
posicion_journey: 73
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [unico]                  # un solo tablero de pedidos: el eje no es la línea, es el pedido
aplica_si: "linea.ciclo_dias == 0 and linea.mecanismo_de_cierre == venta_directa"
depende_de: [gestion-pipeline-demandante]
cierra_fugas: [F-19]                       # elimina la causa: el pedido pasa a ser objeto con estado, dueño y reloj
metrica_que_habilita: [pedidos_por_estado, ciclo_pedido_a_entrega, pedidos_cancelados_por_motivo]
esfuerzo_base: 4                           # a calibrar
esfuerzo_por_instancia: 0
detalle:
  objeto_base: oportunidad
  etapas:
    - nombre: "Pedido recibido"
      criterio_entrada: "pedido tomado por WhatsApp, mostrador o domicilio"
      criterio_salida: "detalle, total y dirección confirmados con el cliente"
      sla_dias: 5
      es_perdida: false
    - nombre: "En preparación"
      criterio_entrada: "confirmado y despachado a los sectores de preparación"
      criterio_salida: "todos los sectores marcaron su parte lista"
      sla_dias: 20
      es_perdida: false
    - nombre: "Despachado"
      criterio_entrada: "salió del local con el repartidor o el cliente lo retiró"
      criterio_salida: "entrega confirmada"
      sla_dias: 30
      es_perdida: false
    - nombre: "Entregado"
      criterio_entrada: "el cliente recibió el pedido"
      criterio_salida: null
      sla_dias: null
      es_perdida: false
  motivos_perdida: ["Canceló antes de preparar", "Fuera de zona de cobertura", "Sin existencias del ítem"]
  sla_unidad: minutos                      # los números de sla_dias están en minutos (schema v0.2.8)
  nota: "Las cuatro etapas son las que el cliente aceptó textualmente en la sesión. El SLA de este negocio se mide en minutos y la unidad se declara en `sla_unidad`, no en una nota: antes de v0.2.8 del schema un `sla_dias: 5` que significaba cinco minutos se leía como cinco días."
```

```yaml
id: cierre-despacho-a-sector
nombre_interno: "Despacho de la comanda por sector de preparación vía notificación interna"
nombre_cliente: "Cada sector ve solo su parte del pedido, en el momento en que entra a preparación"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 75
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [funcion]                # el eje real son los sectores (parrilla, plancha, pizzas, despacho), no las líneas
aplica_si: "linea.ciclo_dias == 0 and linea.mecanismo_de_cierre == venta_directa"
depende_de: [cierre-estados-del-pedido, gestion-permisos-roles]
cierra_fugas: []
mitiga_fugas: [F-15, F-19]                 # F-15: la preparación física no la controla Ropofy · F-19: parte el pedido y lo hace visible por sector
metrica_que_habilita: [comandas_despachadas_por_sector, tiempo_preparacion_por_sector]
esfuerzo_base: 3                           # a calibrar
esfuerzo_por_instancia: 2                  # a calibrar
prerequisito_plataforma: ["Las notificaciones internas de la plataforma llegan SOLO a usuarios del sistema: cada sector de preparación necesita su propio asiento de usuario (o pertenecer a un equipo que lo tenga). Sin asiento no hay a quién notificar."]
detalle:
  disparador: { tipo: cambio_etapa, condicion: "entra a En preparación" }
  acciones:
    - { orden: 1, tipo: notificar_interno, asigna_a_funcion: sector_de_preparacion, canal: whatsapp }
    - { orden: 2, tipo: notificar_interno, asigna_a_funcion: sector_de_preparacion, canal: in_app }
    - { orden: 3, tipo: crear_tarea, asigna_a_funcion: despacho, espera_min: 0 }
  ramas:
    - { condicion: "el pedido toca un solo sector", acciones: [{ tipo: notificar_interno, asigna_a_funcion: sector_de_preparacion }] }
  nota: "Una instancia por sector: el pedido se parte y cada sector recibe su parte, no el pedido completo. Es la pieza que hoy se resuelve gritando."
```

```yaml
id: cierre-aviso-de-avance
nombre_interno: "Avisos al cliente en las transiciones a Despachado y Entregado, con confirmación de entrega por tercero"
nombre_cliente: "El cliente se entera de que su pedido salió y de que llegó, sin preguntar"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 81
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "linea.ciclo_dias == 0 and linea.mecanismo_de_cierre == venta_directa"
depende_de: [cierre-estados-del-pedido]
cierra_fugas: []
metrica_que_habilita: [avisos_de_avance_enviados, entregas_confirmadas_por_tercero]
esfuerzo_base: 3                           # a calibrar
esfuerzo_por_instancia: 1                  # a calibrar
detalle:
  disparador: { tipo: cambio_etapa, condicion: "entra a Despachado o a Entregado" }
  acciones:
    - { orden: 1, tipo: mensaje, canal: whatsapp, plantilla_ref: pedido-despachado, espera_min: 0 }
    - { orden: 2, tipo: mensaje, canal: whatsapp, plantilla_ref: pedido-entregado, espera_min: 0 }
  ramas:
    - { condicion: "el reparto lo hace una empresa tercerizada sin asiento de usuario", acciones: [{ tipo: recibir_confirmacion_externa, condicion: "formulario público de entrega: el repartidor marca entregado y el envío mueve la etapa" }] }
  nota: "La variante del tercero sin asiento resuelve un límite real de la plataforma: la notificación interna exige usuario, el formulario público no. El repartidor no entra al CRM — envía un formulario y el envío dispara el cambio de etapa."
```

```yaml
id: cierre-alerta-pedido-estancado
nombre_interno: "Alerta al coordinador por pedido que excede el SLA de su etapa"
nombre_cliente: "El pedido que se quedó quieto lo descubre el sistema, no el cliente reclamando"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 83
plan_minimo: inteligente                   # prueba de la matriz: actúa cuando NADIE actúa
mecanismo_entrega: snapshot
se_instancia_por: [unico]
aplica_si: "linea.ciclo_dias == 0 and linea.mecanismo_de_cierre == venta_directa"
depende_de: [cierre-estados-del-pedido, gestion-tareas-sla]
cierra_fugas: []                           # nunca cierra: el tiempo del tercero no se cierra, se mide
mitiga_fugas: [F-15, F-19]                 # F-15: se acorta el tramo propio · F-19: descubre el pedido que nadie movió
metrica_que_habilita: [pedidos_estancados, tiempo_excedido_por_etapa]
esfuerzo_base: 2                           # a calibrar
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: oportunidad_estancada, condicion: "supera el SLA declarado de su etapa (en minutos)" }
  acciones:
    - { orden: 1, tipo: notificar_interno, asigna_a_funcion: coordinador, canal: whatsapp }
    - { orden: 2, tipo: crear_tarea, asigna_a_funcion: coordinador }
  nota: "Es el único de los cinco que se dispara por AUSENCIA de acción, y por eso es Inteligente: nadie tocó el pedido y el sistema se da cuenta. Con reparto tercerizado el tiempo total no es de Ropofy — se mitiga F-15 acortando el tramo propio y haciéndolo visible, nunca se promete cierre."
```

```yaml
id: cierre-impresion-comanda
nombre_interno: "Impresión de la comanda en impresora térmica de cocina"
nombre_cliente: "La comanda sale impresa en la cocina, como hoy, pero disparada por el sistema"
tipo: integracion
visibilidad_cliente: back
posicion_journey: 77
plan_minimo: null                          # V11: lo no nativo no viaja dentro del plan
mecanismo_entrega: integracion_externa
se_instancia_por: [unico]
aplica_si: "linea.ciclo_dias == 0 and linea.mecanismo_de_cierre == venta_directa"
depende_de: [cierre-estados-del-pedido]
integraciones_requeridas: []
cierra_fugas: []
metrica_que_habilita: []                   # fuera del plan: ningún tablero del plan puede apoyarse en esto (V9)
esfuerzo_base: 2                           # a calibrar — es la evaluación técnica, lo único que sí viaja en el plan (V11)
esfuerzo_por_instancia: 0
costo_externo:
  tipo: desarrollo_a_cotizar
  detalle: "puente entre la plataforma y la impresora térmica local: no existe como función nativa"
  quien_paga: cliente
prerequisito_plataforma: ["Impresora térmica con conexión de red y un equipo local que reciba el webhook"]
detalle:
  sistema: impresora_termica_de_cocina
  tipo_sistema: hardware_local
  direccion: salida
  objetos_sincronizados: [comanda]
  mecanismo: api_directa
  frecuencia: por_evento
  credenciales_requeridas: [endpoint_local, token_del_puente]
  nota: "Lo ÚNICO de esta subsección que la plataforma no hace. La alternativa nativa existe y puede ser mejor: que el sector reciba la comanda en pantalla por notificación interna (cierre-despacho-a-sector), sin papel y sin desarrollo. Pero no es un reemplazo transparente — es un cambio de hábito en la cocina, y eso es conversación con el cliente, no decisión técnica."
```

### Validaciones del módulo

- **V1** ✔ señales-decision y recuperacion-ia (inteligente) dependen de
  componentes fundamental/avanzado/inteligente coherentes; aprobacion-por-umbral
  (inteligente) sobre aprobaciones-internas (fundamental). En ciclo corto:
  despacho-a-sector y aviso-de-avance (avanzado) dependen de estados-del-pedido
  (fundamental), permisos-roles (fundamental) y nada superior;
  alerta-pedido-estancado (inteligente) sobre estados-del-pedido (fundamental) y
  tareas-sla (fundamental). Ninguna dependencia tiene plan superior al de su
  dependiente.
- **V2** ✔ Referencias a Gestión y Nutrición existen en sus archivos. Las cinco
  piezas de ciclo corto apuntan a gestion-whatsapp-api, gestion-permisos-roles,
  gestion-pipeline-demandante, gestion-tareas-sla y nutricion-plantillas-whatsapp.
- **V6** ✔ F-04 cerrada por secuencia-propuesta; mitigada además por señales y
  recuperación IA. F-05 en contexto subasta solo mitigada (la participación
  final no la controla Ropofy). F-15 mitigada —nunca cerrada— por
  despacho-a-sector y alerta-pedido-estancado: cuando el reparto es de un
  tercero, el tiempo de entrega no se cierra, se mide y se acorta en el tramo
  propio. **F-19 cerrada** por estados-del-pedido (elimina la causa: el pedido
  pasa a ser objeto con estado) y mitigada por confirmacion-pedido,
  despacho-a-sector y alerta-pedido-estancado.
- **V7** ✔ Journey 70–87, después de Nutrición (50–66). Ciclo corto: 71 ≥ 10 y
  ≥ 50 (whatsapp-api, plantillas) · 73 ≥ 30 (pipeline) · 75 y 77 y 81 y 83 ≥ 73
  (estados-del-pedido) · 75 ≥ 16 (permisos) · 83 ≥ 45 (tareas-sla). Todos los
  dependientes van después de sus dependencias.
- **V10** ✔ El módulo aporta `back` en las dos formas: aprobaciones-internas,
  señales-decision y aprobacion-por-umbral en ciclo largo; **despacho-a-sector y
  alerta-pedido-estancado en ciclo corto** (más impresion-comanda, que no cuenta
  porque no viaja en plan). Antes de esta versión, un cliente de ciclo corto se
  quedaba sin ningún componente del módulo — ni front ni back.
- **V11** ✔ impresion-comanda es `integracion` con `mecanismo: api_directa` y
  **sin `plan_minimo`**: va al carril con etiqueta `desarrollo_a_cotizar`. Lo
  único que viaja en el plan es su evaluación técnica.
- **Anti-F-17**: la propuesta expirada registra motivo y se etiqueta para
  Reactivación — misma disciplina que Nutrición: clasificar, nunca descartar. En
  ciclo corto, el pedido cancelado registra su motivo de pérdida por la misma
  razón.

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
| `pedidos_confirmados` / `tiempo_a_confirmacion` | Pedidos con confirmación enviada, y cuánto tarda desde que entra el pedido | confirmacion-pedido |
| `pedidos_por_estado` | Cuántos pedidos hay en cada etapa ahora mismo | estados-del-pedido |
| `ciclo_pedido_a_entrega` | Mediana de **minutos** entre pedido recibido y entregado | estados-del-pedido |
| `pedidos_cancelados_por_motivo` | Pérdidas del ciclo corto con su causa | estados-del-pedido |
| `comandas_despachadas_por_sector` / `tiempo_preparacion_por_sector` | Carga y latencia por sector de preparación | despacho-a-sector |
| `avisos_de_avance_enviados` / `entregas_confirmadas_por_tercero` | Avisos de despacho y entrega, y cuántas entregas confirma el repartidor externo | aviso-de-avance |
| `pedidos_estancados` / `tiempo_excedido_por_etapa` | Pedidos que pasaron su SLA y por cuánto | alerta-pedido-estancado |

---

## D. Pendientes y frontera

1. Plantillas del módulo (propuesta-d1/d3/vence, checklist-documentos,
   recordatorios de evento): redacción por industria en los snapshots.
2. `cierre-pago-enlace` reveló un dato que el guión no pregunta directo: **si el
   anticipo/separación se cobra en línea hoy o podría cobrarse**. Candidato a
   repregunta del Bloque 7.
3. **Plantillas del ciclo corto**: redactadas como punto de partida en §E. Lo
   que queda pendiente es lo que no nos toca — que el cliente apruebe el texto
   final, y que decida tuteo, emojis y si el asistente se declara asistente.
4. **Pregunta nueva para el guión: ¿cobra en línea o contra entrega?** De eso
   depende la ruta de plataforma: la de comercio electrónico exige pago real
   registrado, y si el negocio cobra contra entrega esa ruta no sirve — hay que ir
   por Oportunidades, que es lo que hace `cierre-estados-del-pedido`. Sin este
   dato la etapa 3 elige a ciegas entre dos arquitecturas distintas.
5. **La discriminante `ciclo_dias` es un proxy.** Lo que de verdad separa las dos
   formas de cierre no es la duración sino si el negocio **emite un documento
   formal** antes de vender (cotización, contrato). Hoy la ficha no tiene ese
   campo y se usa `ciclo_dias` en su lugar. Candidato a campo propio de la ficha.
6. **La frontera se sostiene por tercera vez**: Fundamental = ninguna propuesta
   ni aprobación se pierde (cobertura); Avanzado = el cierre se ejecuta digital
   — contrato, pago, evento (sustancia); Inteligente = el sistema detecta la
   decisión y actúa solo (iniciativa). Patrón **cobertura → sustancia →
   iniciativa** confirmado en 3 de 7 módulos.

---

## E. Plantillas del ciclo corto — punto de partida

Redacción metodológica de Ropofy. **El texto final lo proporciona o aprueba el
cliente** antes de activarse (regla global del copy): la voz de la marca es
suya, la estructura y el método son nuestros. Las variables van entre `{{ }}` y
salen del contacto o del pedido; el tono y los modismos salen de la guía de voz
del cliente, no de aquí.

### `confirmacion-pedido` — al confirmarse el pedido

> Listo {{nombre_contacto}}, tu pedido quedó confirmado 🙌
> {{detalle_pedido}}
> Total: {{total}}
> Sale para {{direccion_de_entrega}} y demora aprox. {{demora_estimada}}.
> Cualquier cambio, escríbeme por acá.

**Variante interactiva — confirmar la dirección** (hasta 3 botones de respuesta
rápida; si son más opciones, mensaje de lista):

> {{nombre_contacto}}, ¿a dónde te lo enviamos?
> [ {{direccion_1}} ] [ {{direccion_2}} ] [ Otra dirección ]

Con «Otra dirección» el asistente pide la dirección en texto y la registra en el
contacto. La confirmación no se manda hasta que la dirección esté resuelta:
mandar el detalle a una dirección equivocada cuesta el pedido completo.

### `pedido-despachado` — al entrar a Despachado

> {{nombre_contacto}}, tu pedido ya salió 🛵
> Llega en aprox. {{demora_estimada}} a {{direccion_de_entrega}}.

### `pedido-entregado` — al entrar a Entregado

> ¡Entregado, {{nombre_contacto}}! Que lo disfrutes 😋
> Si algo no llegó como esperabas, cuéntame por acá y lo resolvemos.

**Tres decisiones que el cliente tiene que tomar sobre estos textos**, y que la
etapa 4 registra: si se tutea o se trata de usted, si se usan emojis y cuáles, y
si el asistente se declara asistente o habla como el negocio. Nada de eso se
decide aquí.
