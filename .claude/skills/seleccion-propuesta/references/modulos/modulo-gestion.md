# Módulo Gestión — Librería de componentes v0.1

20 componentes conforme al schema v0.2.3. Validados contra el piloto Activos
por Colombia (§B). Incluye la primera versión del diccionario de métricas (§C).
v0.2 (ago-2026, aprendizajes AYC): entran telefonía y pipeline operativo —
producto que Ropofy ya vendía y la librería no modelaba — y se aplican las
primeras `cuotas_por_plan`.

Convención de esfuerzo: 1 punto ≈ media jornada de implementación.

---

## A. Componentes

### Cimiento (posicion_journey 10–19)

```yaml
id: gestion-whatsapp-api
nombre_interno: "Línea WhatsApp Business API verificada"
nombre_cliente: "WhatsApp oficial que no se bloquea y atiende a todo el equipo"
tipo: integracion
visibilidad_cliente: ambos
posicion_journey: 10
plan_minimo: fundamental
mecanismo_entrega: configuracion_cuenta
se_instancia_por: [linea_negocio]     # una línea de WA por línea de negocio si ya operan separadas
aplica_si: ""
bloqueado_por_tercero: ""
depende_de: []
cierra_fugas: []                      # es prerrequisito, no cierre: resuelve R-01..R-04
mitiga_fugas: []
metrica_que_habilita: [conversaciones_entrantes_mes]
esfuerzo_base: 3
esfuerzo_por_instancia: 2
prerequisito_plataforma: ["Verificación de negocio en Meta", "Gestión de expectativa: historial previo no migra completo (R-04)"]
detalle:
  sistema: WhatsApp Cloud API
  tipo_sistema: whatsapp_api
  direccion: bidireccional
  objetos_sincronizados: [conversaciones, contactos]
  mecanismo: nativa
  credenciales_requeridas: [Meta Business Manager]
```

```yaml
id: gestion-canales-unificados
nombre_interno: "Bandeja omnicanal: WA, FB/IG Messenger, comentarios, webchat, email"
nombre_cliente: "Todas las conversaciones en una sola bandeja, ninguna se pierde"
tipo: integracion
visibilidad_cliente: ambos
posicion_journey: 12
plan_minimo: fundamental
mecanismo_entrega: configuracion_cuenta
se_instancia_por: [unico]
depende_de: [gestion-whatsapp-api]
cierra_fugas: []
mitiga_fugas: []                      # ataca C-03 junto con base-contactos
metrica_que_habilita: [conversaciones_por_canal, tiempo_primera_respuesta]
esfuerzo_base: 3
esfuerzo_por_instancia: 0
detalle:
  sistema: "Meta (páginas), webchat propio, buzón email"
  direccion: bidireccional
  mecanismo: nativa
```

```yaml
id: gestion-base-contactos
nombre_interno: "Base de contactos única con deduplicación y consentimiento"
nombre_cliente: "Un solo lugar donde vive cada cliente con todo su historial"
tipo: campos_personalizados
visibilidad_cliente: back
posicion_journey: 14
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [unico]             # la base es una aunque haya varias líneas (comparte_base_contactos)
depende_de: []
cierra_fugas: []                      # cierra C-03 junto con canales-unificados
metrica_que_habilita: [contactos_totales, contactos_nuevos_mes]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  campos:
    - { nombre: linea_de_interes, tipo: opcion_multiple, objeto: contacto, obligatorio: false, es_para_reporte: true }
    - { nombre: consentimiento_datos, tipo: booleano, objeto: contacto, obligatorio: true, es_para_reporte: false }
    - { nombre: territorio, tipo: opcion_unica, objeto: contacto, obligatorio: false, es_para_reporte: true }
```

```yaml
id: gestion-campos-atribucion
nombre_interno: "Campos de atribución primera y última fuente + UTM"
nombre_cliente: "Saber de qué campaña o canal vino cada cliente"
tipo: campos_personalizados
visibilidad_cliente: back
posicion_journey: 15
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [gestion-base-contactos]
cierra_fugas: []
mitiga_fugas: []                      # es EL componente que resuelve C-02
metrica_que_habilita: [leads_por_fuente, atribucion_primera_fuente, atribucion_ultima_fuente]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  campos:
    - { nombre: primera_fuente, tipo: opcion_unica, objeto: contacto, obligatorio: true, es_para_reporte: true }
    - { nombre: ultima_fuente, tipo: opcion_unica, objeto: contacto, obligatorio: true, es_para_reporte: true }
    - { nombre: utm_campaign_primera, tipo: texto, objeto: contacto, obligatorio: false, es_para_reporte: true }
```

```yaml
id: gestion-campos-calificacion
nombre_interno: "Campos de calificación por línea de negocio"
nombre_cliente: "Los datos que tu equipo necesita preguntar siempre, sin olvidos"
tipo: campos_personalizados
visibilidad_cliente: back
posicion_journey: 18
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio, sujeto_del_embudo]   # el oferente califica distinto: su activo, no su presupuesto
depende_de: [gestion-base-contactos]
cierra_fugas: []
metrica_que_habilita: [leads_calificados_mes, tasa_calificacion]
esfuerzo_base: 2
esfuerzo_por_instancia: 1
detalle:
  campos:
    - { nombre: presupuesto_rango, tipo: opcion_unica, objeto: oportunidad, obligatorio: false, es_para_reporte: true }
    - { nombre: forma_de_pago, tipo: opcion_unica, objeto: oportunidad, obligatorio: false, es_para_reporte: true }
    # instancia oferente: caracteristicas_del_activo, expectativa_precio, exclusividad
```

### Primer contacto (20–29)

```yaml
id: gestion-ruteo-intencion
nombre_interno: "Ruteo de entrada por intención y línea de negocio"
nombre_cliente: "Cada mensaje llega directo al equipo correcto desde el primer minuto"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 20
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [unico]             # un solo ruteador con una rama por línea
depende_de: [gestion-canales-unificados, gestion-base-contactos]
cierra_fugas: [F-06]
mitiga_fugas: [FO-03]                 # el oferente deja de hacer cola con los compradores
metrica_que_habilita: [leads_por_linea, tiempo_hasta_ruteo]
esfuerzo_base: 3
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: conversacion_entrante, condicion: "sin asignar" }
  acciones:
    - { orden: 1, tipo: clasificar, canal: whatsapp, plantilla_ref: menu-intencion }
    - { orden: 2, tipo: etiquetar_linea }
    - { orden: 3, tipo: asignar_a_funcion, asigna_a_funcion: segun_linea }
  ramas:
    - { condicion: "intencion == ofrecer_activo", acciones: [{ tipo: asignar_a_funcion, asigna_a_funcion: captador }] }
```

```yaml
id: gestion-respuesta-inmediata
nombre_interno: "Primera respuesta automática inmediata, 24/7 (auto-reply de entrada por canal)"
nombre_cliente: "Nadie espera: respuesta al instante, de día, de noche y en festivos"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 21
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
depende_de: [gestion-ruteo-intencion]
cierra_fugas: [F-02, F-03]
metrica_que_habilita: [tiempo_primera_respuesta, pct_respondidos_5min, leads_fuera_horario]
esfuerzo_base: 2
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: conversacion_entrante, condicion: "sin respuesta humana" }
  acciones:
    - { orden: 1, tipo: mensaje, canal: whatsapp, plantilla_ref: bienvenida-linea, espera_min: 0 }
    - { orden: 2, tipo: crear_tarea, asigna_a_funcion: asesor, espera_min: 5 }
  ramas:
    - { condicion: "fuera_de_horario", acciones: [{ tipo: mensaje, plantilla_ref: fuera-horario }, { tipo: agendar_seguimiento_apertura }] }
```

```yaml
id: gestion-asignacion-leads
nombre_interno: "Asignación automática con reglas: round-robin, territorio, carga"
nombre_cliente: "Cada lead tiene un dueño desde el primer segundo"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 24
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio, territorio]
depende_de: [gestion-ruteo-intencion]
cierra_fugas: [F-06, F-07]
metrica_que_habilita: [leads_asignados_por_asesor, distribucion_carga]
cuotas_por_plan: { fundamental: 1, avanzado: 3, inteligente: 3 }
unidad_de_cuota: reglas_de_asignacion    # "hasta N reglas" — calibrado con el deck AYC
esfuerzo_base: 2
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: lead_ruteado }
  acciones:
    - { orden: 1, tipo: asignar, condicion: "round_robin dentro de la función/territorio" }
    - { orden: 2, tipo: reasignar, condicion: "sin gestión en SLA", espera_min: 120 }
```

```yaml
id: gestion-telefonia-llamadas
nombre_interno: "Canal telefónico en el CRM: registro, grabación y llamada perdida como lead"
nombre_cliente: "Cada llamada queda registrada con su grabación — y la perdida se convierte en tarea, no en silencio"
tipo: telefonia
visibilidad_cliente: ambos
posicion_journey: 14
plan_minimo: fundamental
mecanismo_entrega: configuracion_cuenta
se_instancia_por: [unico]
aplica_si: "el teléfono es canal de entrada relevante (call center, avisos con número, línea fija)"
depende_de: [gestion-base-contactos]
cierra_fugas: [C-04]                      # se acaba el conteo a mano de llamadas
mitiga_fugas: [F-02]                      # la llamada fuera de horario deja de evaporarse
metrica_que_habilita: [llamadas_recibidas, llamadas_perdidas, tasa_atencion_llamadas, grabaciones_disponibles, duracion_promedio_llamada, llamadas_por_asesor]
esfuerzo_base: 3
esfuerzo_por_instancia: 0
prerequisito_plataforma: ["Número portado o provisionado en la plataforma; los números históricos impresos (avisos, ventanas) se redireccionan, no se abandonan"]
detalle:
  proveedor: lc_phone
  numeros:
    - { uso: principal, tipo: movil }
    - { uso: por_area, tipo: fijo }
  enrutamiento: { mecanismo: menu_ivr, destinos_por_funcion: [asesor, postventa_administracion, cumplimiento] }
  grabacion: { activa: true, base_legal_declarada: true, retencion_dias: 180 }
  registro: { entrantes: true, salientes: true, perdidas: true, duracion: true }
  click_to_call: true
  nota: "El dolor #1 declarado de AYC: 'muchas líneas, sin métricas de llamadas perdidas'. Cimiento del canal: sin esto, la mitad de la operación telefónica es invisible para todos los tableros."
```

```yaml
id: gestion-llamadas-whatsapp
nombre_interno: "Llamadas de voz dentro del hilo de WhatsApp (Cloud API): entrantes gratis, salientes con permiso"
nombre_cliente: "Tu cliente te llama por WhatsApp y la llamada queda en la misma conversación, con su grabación de resultado"
tipo: telefonia
visibilidad_cliente: ambos
posicion_journey: 15
plan_minimo: fundamental
mecanismo_entrega: configuracion_cuenta
se_instancia_por: [unico]
aplica_si: "el WhatsApp del cliente está en API (no en coexistencia con la app de WhatsApp Business)"
depende_de: [gestion-whatsapp-api, gestion-base-contactos]
cierra_fugas: []
mitiga_fugas: [F-18]                      # la llamada entrante queda registrada y con callback
metrica_que_habilita: [llamadas_wa_entrantes, llamadas_wa_salientes, permisos_llamada_activos, disposiciones_por_resultado]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
prerequisito_plataforma:
  - "Beta con solicitud de acceso: habilitación ~24 h — afecta cronograma"
  - "Número en API, NO en coexistencia: si el cliente sigue usando la app de WhatsApp Business en ese número, no puede llamar"
  - "Límite de mensajería de la WABA de 2.000 conversaciones/24 h o superior"
  - "App móvil 4.18+ para atender desde el celular"
  - "R-08: las salientes exigen permiso del contacto — la plantilla de solicitud con botón es parte de la configuración de este componente, no un entregable aparte. Topes: 1 solicitud/24 h, máx 2 en 7 días"
  - "R-09: coexistencia bloquea el canal"
detalle:
  proveedor: whatsapp_cloud_api
  numeros:
    - { uso: principal, tipo: movil }
  enrutamiento: { mecanismo: directo, destinos_por_funcion: [asesor] }   # usuario primario + respaldos
  grabacion: { activa: false, base_legal_declarada: false, retencion_dias: 0 }
  registro: { entrantes: true, salientes: true, perdidas: true, duracion: true }
  click_to_call: true
  disposiciones: [resuelto, requiere_seguimiento, no_contesto, no_interesado]
  nota: "Dos asimetrías que la propuesta debe decir: (1) la entrante es GRATIS y no pide permiso — el ahorro real frente a Twilio; (2) la saliente cuesta centavos por minuto (CO ~US$0,0117) pero vive del permiso del contacto. Las disposiciones disparan automatizaciones: es el gancho entre voz y embudo."
```

```yaml
id: gestion-llamada-ia-fuera-horario
nombre_interno: "Agente IA de voz inbound: contesta fuera de horario, recepciona y radica"
nombre_cliente: "La llamada de las 9 pm la contesta un asistente que toma el caso completo — tu equipo llega y ya está radicado"
tipo: chatbot_ia
visibilidad_cliente: front
habilidad: recepcionista_voz
posicion_journey: 27
plan_minimo: inteligente
mecanismo_entrega: contenido_a_medida
se_instancia_por: [unico]
aplica_si: "gestion-telefonia-llamadas en el plan"
depende_de: [gestion-telefonia-llamadas, gestion-ruteo-intencion]
cierra_fugas: []
mitiga_fugas: [F-02, F-08]
metrica_que_habilita: [llamadas_fuera_horario_atendidas, casos_radicados_por_ia]
esfuerzo_base: 4
esfuerzo_por_instancia: 0
prerequisito_plataforma: ["O-01: tono y límites aprobados; guion de recepción por motivo de contacto"]
detalle:
  alcance: [identificar_motivo, tomar_datos_del_caso, radicar_o_agendar_retorno]
  criterio_escalamiento: "urgencia declarada o intención comercial caliente"
  handoff_a_funcion: asesor
  horario_activo: fuera_de_horario
  nota: "Es recepcionista, no closer: toma la información para que el humano regrese con el caso creado — el framing exacto que Cristina (AYC) validó en vivo."
```

```yaml
id: gestion-pipeline-operativo
nombre_interno: "Pipeline de solicitudes no comerciales: mantenimiento, administración, casos"
nombre_cliente: "Lo que no es venta deja de estorbar la venta — y también deja de perderse"
tipo: pipeline
visibilidad_cliente: back
posicion_journey: 28
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [unico]
aplica_si: "existe volumen operativo entrante por los mismos canales comerciales (mantenimiento, posesiones, administración)"
depende_de: [gestion-ruteo-intencion]
cierra_fugas: []
mitiga_fugas: [F-06]                      # el ruteo necesita destino: derivar sin pipeline es perder con más pasos
metrica_que_habilita: [solicitudes_operativas_mes, ciclo_resolucion_operativa, solicitudes_vencidas_operativas]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  sujeto: solicitud
  etapas:
    - { nombre: Radicada, sla_dias: 1 }
    - { nombre: Asignada, sla_dias: 2 }
    - { nombre: En atención, sla_dias: 5 }
    - { nombre: Resuelta, sla_dias: null }
  motivos_perdida: [duplicada, no_procede, resuelta_por_tercero]
  nota: "El destino que faltaba: ruteo-intencion clasifica y esto recibe. AYC lo vendió como 'Pipeline Administrativo/Operativo' porque el canal comercial se contaminaba con mantenimiento y ocupaciones. No es alcance comercial de Ropofy gestionar la operación — es proteger el embudo comercial dándole cauce a lo demás."
```

```yaml
id: gestion-asistente-informativo
nombre_interno: "Asistente IA informativo: FAQ de proceso, requisitos y estado del catálogo, con escalamiento a humano"
nombre_cliente: "Un asistente que sabe del negocio y responde al instante lo que tu equipo repite todo el día"
tipo: chatbot_ia
visibilidad_cliente: front
habilidad: informativo
posicion_journey: 26
plan_minimo: avanzado
mecanismo_entrega: contenido_a_medida     # la base de conocimiento es del cliente
se_instancia_por: [linea_negocio]
depende_de: [gestion-ruteo-intencion]
cierra_fugas: [F-08, F-14]
mitiga_fugas: [F-02]
metrica_que_habilita: [conversaciones_atendidas_por_ia, tasa_escalamiento]
esfuerzo_base: 5
esfuerzo_por_instancia: 3
prerequisito_plataforma: ["Base de conocimiento aprobada por el cliente", "O-01: definir tono y límites con el cliente antes de activar"]
detalle:
  alcance: [faq_proceso, requisitos, estado_catalogo]
  base_conocimiento: [portafolio, requisitos_por_linea, proceso_por_mecanismo_de_cierre]
  criterio_escalamiento: "intencion_transaccional confirmada o solicitud explícita de humano"
  handoff_a_funcion: asesor
  horario_activo: 24_7
  nota: "Mitad informativa de la división de gestion-chatbot-precalificacion (catálogo de habilidades §5 · C2). Habilidad `informativo`: responde con el contexto del contacto y registra la duda (N2). No infiere interés ni etiqueta temperatura — eso es el precalificador, y vive en Inteligente."
```

```yaml
id: gestion-precalificador
nombre_interno: "Agente IA de precalificación: triage por línea, temperatura y entrega del lead desmenuzado"
nombre_cliente: "Tu equipo solo habla con quien sí va a comprar"
tipo: chatbot_ia
visibilidad_cliente: front
habilidad: precalificador
posicion_journey: 26
plan_minimo: inteligente
mecanismo_entrega: contenido_a_medida
se_instancia_por: [linea_negocio]
depende_de: [gestion-ruteo-intencion, gestion-campos-calificacion]
cierra_fugas: []                          # TODO reparto sin decidir — ver la nota de la división
mitiga_fugas: []                          # TODO reparto sin decidir — ver la nota de la división
metrica_que_habilita: [leads_precalificados_ia]
esfuerzo_base: 4
esfuerzo_por_instancia: 2
prerequisito_plataforma: ["scoring configurado (gestion-scoring-contacto)", "O-01: definir tono y límites con el cliente antes de activar"]
detalle:
  alcance: [precalificacion]
  criterio_escalamiento: "umbral alto de score: alerta + llamada del asesor en <= 5 min"
  handoff_a_funcion: asesor
  horario_activo: 24_7
  nota: "Mitad precalificadora de la división (catálogo §3.5 · C2). Habilidad `precalificador`, exclusiva de Inteligente: hace el triage del vertical, aplica descalificadoras con salida digna, verifica leads de terceros al ingreso y entrega el lead desmenuzado. Empieza donde la regla dura termina: filtrar por cobertura u oferta es el recepcionista N2 (frontera del catálogo §3.1)."
```

**TODO abierto por la división (C2) — no decidir sin producto.**

1. **Reparto de fugas.** `gestion-asistente-informativo` conserva
   `cierra_fugas: [F-08, F-14]` y `mitiga_fugas: [F-02]`, y
   `gestion-precalificador` queda **sin fugas asignadas**. No es un olvido: es
   que el reparto que C2 supone no es inequívoco contra el catálogo de fugas.
   F-08 es *"el volumen desborda la capacidad y se responde a medias"* y F-14
   es *"el inventario sin precio genera consultas que nadie puede responder"* —
   ambas son atención de volumen y de conocimiento, ninguna es inferir cuánto
   vale un lead. Ninguna parte de F-08 ni de F-14 depende de *precalificar*.
   El candidato natural para el precalificador es **F-13** (*el costo de los
   leads descalificados se paga en tiempo del asesor*), pero hoy la cierra
   `atraccion-formularios-precalificacion` "donde es más barato" y duplicarla
   sería una decisión de producto, no una corrección. El propio catálogo lo
   deja pendiente: §7 v1.2, *"verificar los ids de fugas citados en C2 contra
   el catálogo de fugas al ejecutar la corrección"*. **Se deja abierto.**
2. **`depende_de` repuntados.** Tres componentes apuntaban al id que ya no
   existe. `cierre-recuperacion-ia` y `nutricion-reinyeccion-ia` dependen ahora
   de **`gestion-precalificador`**: las dos actualizan calificación o
   temperatura, que es semántica N3, y siendo Inteligente V1 lo permite.
   `reactivacion-absorcion-oleadas` —que C2 no nombra y también dependía—
   depende de **`gestion-asistente-informativo`**, y ahí la elección es
   forzada: es Avanzado y no puede depender de un componente Inteligente (V1).

   *El reparto de esfuerzo de la división ya está decidido:*
   `gestion-asistente-informativo` 5 + 3 por instancia,
   `gestion-precalificador` 4 + 2.

### Pipeline y agenda (30–49)

```yaml
id: gestion-pipeline-demandante
nombre_interno: "Pipeline de oportunidades con SLA por etapa (comprador/arrendatario)"
nombre_cliente: "Embudo de ventas visible con alertas de estancamiento"
tipo: pipeline
visibilidad_cliente: back
posicion_journey: 30
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio, mecanismo_de_cierre]  # subasta y venta directa NO comparten pipeline
aplica_si: "linea.sujeto_del_embudo == demandante"
depende_de: [gestion-campos-calificacion]
cierra_fugas: [F-09]
metrica_que_habilita: [conversion_por_etapa, dias_en_etapa, oportunidades_abiertas_valor, motivos_perdida]
esfuerzo_base: 5
esfuerzo_por_instancia: 3
detalle:
  objeto_base: oportunidad
  etapas: "se definen con las etapas reales de la ficha (A.etapas), nunca con las del guión"
  motivos_perdida: [sin_presupuesto, eligio_competencia, no_contactable, desistido]
```

```yaml
id: gestion-pipeline-oferente
nombre_interno: "Pipeline de captación: precaptación → contacto → visita de estimación → contrato"
nombre_cliente: "El embudo de consecución de inventario, tan visible como el de ventas"
tipo: pipeline
visibilidad_cliente: back
posicion_journey: 30
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "existe linea con sujeto_del_embudo == oferente"
depende_de: [gestion-campos-calificacion]
cierra_fugas: [FO-01, FO-02]
metrica_que_habilita: [captaciones_mes, conversion_precaptacion_contrato, inventario_captado_valor]
esfuerzo_base: 5
esfuerzo_por_instancia: 3
detalle:
  objeto_base: oportunidad
  etapas:
    - { nombre: Precaptación, criterio_entrada: "activo detectado en campo o entrante", criterio_salida: "propietario contactado", sla_dias: 3 }
    - { nombre: Visita de estimación, sla_dias: 7 }
    - { nombre: Negociación de contrato, sla_dias: 10 }
  motivos_perdida: [eligio_otra_inmobiliaria, expectativa_precio, desistio]
```

```yaml
id: gestion-precaptacion-movil
nombre_interno: "Formulario móvil de precaptación en campo con foto y geolocalización"
nombre_cliente: "Cada letrero que tu ejecutivo ve en la calle entra al sistema al instante"
tipo: formulario
visibilidad_cliente: back
posicion_journey: 29
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [unico]
aplica_si: "existe linea oferente con prospeccion_en_campo"
depende_de: [gestion-pipeline-oferente]
cierra_fugas: [FO-01]
metrica_que_habilita: [precaptaciones_mes_por_ejecutivo]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  campos:
    - { etiqueta: Dirección, campo_destino: direccion_activo, obligatorio: true }
    - { etiqueta: Foto del letrero, campo_destino: evidencia, obligatorio: true }
    - { etiqueta: Teléfono del letrero, campo_destino: telefono_propietario, obligatorio: false }
  destino: { pipeline_ref: gestion-pipeline-oferente, etapa: Precaptación }
```

```yaml
id: gestion-llamada-perdida
nombre_interno: "Rescate de llamada perdida: tarea inmediata + WhatsApp automático de retorno"
nombre_cliente: "La llamada que nadie alcanzó a contestar recibe un mensaje en el minuto y queda como pendiente de alguien"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 13
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [gestion-telefonia-llamadas, nutricion-plantillas-whatsapp]
cierra_fugas: [F-18]
metrica_que_habilita: [perdidas_rescatadas, tiempo_perdida_a_contacto]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: llamada_perdida }
  acciones:
    - { orden: 1, tipo: mensaje, canal: whatsapp, plantilla_ref: llamada-perdida-retorno, espera_min: 1 }
    - { orden: 2, tipo: crear_tarea, asigna_a_funcion: asesor }
    - { orden: 3, tipo: escalar, asigna_a_funcion: coordinador, espera_min: 240 }
  nota: "Fuera de horario el mensaje es la única respuesta posible y ya evita la fuga: el que llamó sabe que existe y por dónde seguir."
```

```yaml
id: gestion-calendario-visitas
nombre_interno: "Calendario de visitas/citas con confirmación y recordatorios"
nombre_cliente: "El interesado agenda solo, confirma solo, y tu equipo llega a citas que sí ocurren"
tipo: calendario
visibilidad_cliente: ambos
posicion_journey: 40
plan_minimo: avanzado
mecanismo_entrega: configuracion_cuenta
se_instancia_por: [control_del_activo, territorio]
aplica_si: "linea.control_del_activo in [propio, tercero_privado]"
bloqueado_por_tercero: "linea.control_del_activo == tercero_institucional"   # F-15: no hay disponibilidad que exponer
depende_de: [gestion-pipeline-demandante]
cierra_fugas: [F-05]
metrica_que_habilita: [citas_agendadas, tasa_show_up, citas_por_territorio]
cuotas_por_plan: { avanzado: 5, inteligente: 10 }
unidad_de_cuota: calendarios
esfuerzo_base: 3
esfuerzo_por_instancia: 1
detalle:
  modalidad: round_robin
  asignacion_por: territorio
  recordatorios:
    - { canal: whatsapp, anticipacion: 24h }
    - { canal: whatsapp, anticipacion: 2h, confirmacion_interactiva: [asistire, reagendar, cancelar] }
  ramas:
    - { condicion: no_show, acciones: [{ tipo: mensaje, plantilla_ref: reagendamiento-1, espera_min: 120 }, { tipo: mensaje, plantilla_ref: reagendamiento-2, espera_min: 2880 }, { tipo: etiquetar, condicion: "sin respuesta → candidato_reactivacion" }] }
  nota: "La rama no-show cierra el hueco que AYC destapó: la cita fallida tenía recordatorios antes y nada después."
```

```yaml
id: gestion-solicitud-habilitador
nombre_interno: "Solicitud automática al habilitador del activo, disparada por evento"
nombre_cliente: "La solicitud de llaves/alistamiento sale en el momento, no en el lote del viernes"
tipo: automatizacion
visibilidad_cliente: ambos
posicion_journey: 42
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "existe dependencias_externas_del_proceso en etapa de visita"
depende_de: [gestion-pipeline-demandante]
cierra_fugas: []
mitiga_fugas: [F-15]                  # NUNCA prometer cierre: el ciclo del tercero no es nuestro
metrica_que_habilita: [ciclo_solicitud_a_visita, solicitudes_enviadas, solicitudes_sin_respuesta_tercero]
esfuerzo_base: 3
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: cambio_etapa, condicion: "etapa == visita_solicitada" }
  acciones:
    - { orden: 1, tipo: email, plantilla_ref: solicitud-llaves, asigna_a_funcion: habilitador_de_activo }
    - { orden: 2, tipo: copiar_a, asigna_a_funcion: coordinador }
    - { orden: 3, tipo: crear_tarea_seguimiento, espera_min: 2880 }
  nota: "El correo sale a nombre del responsable interno; medir el ciclo es el argumento para renegociar con el tercero (F-17)."
```

```yaml
id: gestion-tareas-sla
nombre_interno: "Tareas automáticas y alertas de estancamiento por SLA de etapa"
nombre_cliente: "El sistema le recuerda a cada asesor qué sigue, y avisa cuando algo se estanca"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 45
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [unico]             # una automatización que lee el SLA de cada etapa
depende_de: [gestion-pipeline-demandante]
cierra_fugas: [F-09]
mitiga_fugas: [F-01]                  # el seguimiento sistemático completo vive en Nutrición
metrica_que_habilita: [tareas_vencidas, oportunidades_estancadas]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: sla_vencido }
  acciones:
    - { orden: 1, tipo: crear_tarea, asigna_a_funcion: asesor }
    - { orden: 2, tipo: notificar, asigna_a_funcion: coordinador, espera_min: 1440 }
```

### Calificación avanzada e integraciones (35, 50+)

```yaml
id: gestion-scoring-contacto
nombre_interno: "Contact score 0-100 con señales internas y externas"
nombre_cliente: "Abrir el contacto y saber al instante a quién darle atención VIP"
tipo: scoring
visibilidad_cliente: back
posicion_journey: 35
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
depende_de: [gestion-campos-calificacion, gestion-base-contactos]
cierra_fugas: [F-16, F-13]
mitiga_fugas: [F-17]                  # scoring documentado = evidencia para renegociar el indicador externo
metrica_que_habilita: [distribucion_score, conversion_por_banda_score]
cuotas_por_plan: { inteligente: 3 }
unidad_de_cuota: reglas_de_scoring
esfuerzo_base: 4
esfuerzo_por_instancia: 2
detalle:
  sujeto: contacto
  escala: { min: 0, max: 100 }
  variables:
    - { señal: registro_en_plataforma_propia, puntos: 50, fuente_del_dato: gestion-integracion-plataforma, es_descalificadora: false }
    - { señal: documento_interes_firmado, puntos: 20, fuente_del_dato: gestion-documento-interes, es_descalificadora: false }
    - { señal: preaprobacion_o_recursos, puntos: 20, fuente_del_dato: conversacion, es_descalificadora: false }
    - { señal: datos_falsos, puntos: 0, fuente_del_dato: conversacion, es_descalificadora: true }
  umbrales:
    - { nombre: VIP, min: 70, accion: notificar_asesor_inmediato }
    - { nombre: nutrir, min: 30, accion: secuencia_nutricion }
```

```yaml
id: gestion-integracion-plataforma
nombre_interno: "Integración con plataforma propia del cliente (registro, KYC, estados) — A COTIZAR"
nombre_cliente: "Lo que el cliente ya hizo en tu plataforma, visible en cada conversación"
tipo: integracion
visibilidad_cliente: back
posicion_journey: 33
plan_minimo: null                      # V11: no pertenece a ningún plan
costo_externo: { tipo: desarrollo_a_cotizar, quien_paga: cliente, detalle: "vía n8n o API; depende del sistema del cliente" }
mecanismo_entrega: integracion_externa
se_instancia_por: [unico]
depende_de: [gestion-base-contactos]
cierra_fugas: [F-16]
metrica_que_habilita: [registros_detectados, kyc_aprobados_visibles]
esfuerzo_base: 0                       # el esfuerzo real sale de la evaluación técnica, nunca de la librería
esfuerzo_por_instancia: 0
prerequisito_plataforma: ["Evaluación técnica con el proveedor del cliente (esta SÍ viaja en el plan: es trabajo acotado)", "Cotización aprobada antes de comprometer fecha"]
detalle:
  sistema: plataforma_del_cliente
  direccion: entrada
  objetos_sincronizados: [registro, estado_kyc, eventos_comerciales]
  mecanismo: n8n_o_api
  nota: "V11: lo no nativo no viaja dentro del plan. En el lienzo aparece en el carril de integraciones con 'se cotiza aparte'. F-16 queda mitigada (no cerrada) mientras la integración no exista: el lienzo debe decirlo."
```

```yaml
id: gestion-documento-interes
nombre_interno: "Expresión de interés con firma electrónica y cambio de etapa automático"
nombre_cliente: "La carta de interés se pide, se firma y mueve el proceso sin que nadie la persiga"
tipo: documento_firmable
visibilidad_cliente: front
posicion_journey: 38
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "linea.estado_del_catalogo.items_publicados_sin_precio o proceso requiere manifestacion formal"
depende_de: [gestion-pipeline-demandante]
cierra_fugas: [F-14]
metrica_que_habilita: [documentos_enviados, tasa_firma, ciclo_solicitud_firma]
esfuerzo_base: 3
esfuerzo_por_instancia: 1
detalle:
  proposito: expresion_de_interes
  datos_requeridos:
    - { campo: nombre_completo, fuente: crm }
    - { campo: cedula, fuente: conversacion }
    - { campo: activo_de_interes, fuente: crm }
  mecanismo_firma: firma_electronica
  accion_post_firma: { cambia_etapa_a: interes_formalizado, notifica_a_funcion: aprobador_comercial }
```

```yaml
id: gestion-permisos-roles
nombre_interno: "Roles y alcances de datos por función, territorio y afiliados"
nombre_cliente: "Cada quien ve lo suyo: asesores, coordinadores, territoriales y aliados"
tipo: permisos_usuarios
visibilidad_cliente: back
posicion_journey: 16
plan_minimo: fundamental
mecanismo_entrega: configuracion_cuenta
se_instancia_por: [unico]
depende_de: [gestion-base-contactos]
cierra_fugas: []
metrica_que_habilita: []
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  roles:
    - { funcion: asesor, alcance_datos: propios, puede_ver_todo: false, puede_aprobar: false }
    - { funcion: coordinador, alcance_datos: equipo, puede_ver_todo: false, puede_aprobar: true }
    - { funcion: habilitador_de_activo, alcance_datos: territorio, puede_ver_todo: false, puede_aprobar: false }
    - { funcion: externo_afiliado, alcance_datos: externo_afiliado, puede_ver_todo: false, puede_aprobar: false }
  nota: "Los alcances territorio y externo_afiliado se configuran solo si la ficha los declara (fundamental cubre asesor/coordinador)."
```

### Validaciones del módulo (corridas sobre esta versión)

- **V1** ✔ Ningún componente fundamental depende de uno superior. `scoring`
  (inteligente) usa señales de `integracion-plataforma` (inteligente) y
  `documento-interes` (inteligente): coherente. Si el cliente compra Avanzado,
  el scoring simplemente no está — las señales no quedan huérfanas.
- **V2** ✔ Todas las referencias existen en este archivo.
- **V6** ✔ F-15 y F-17 solo aparecen en `mitiga_fugas`. F-01 aparece como
  mitigada aquí y su cierre pertenece a Nutrición (frontera de módulo declarada).
- **V7** ✔ posicion_journey del dependiente ≥ dependencia en todos los casos.
- **Frontera con otros módulos**: F-04 (propuestas sin retomar) → Cierre.
  F-01 completo y FO-02 → Nutrición. F-10 → Reactivación. C-01/C-02 se
  *habilitan* aquí (atribución, pipeline) pero sus tableros → Tableros.

---

## B. Validación contra el piloto (Activos por Colombia)

Resolución de instancias con la ficha del piloto:

| Componente | Instancias | Detalle |
|---|---|---|
| whatsapp-api | 2 | Líneas ventas y arriendos ya separadas en Meta |
| pipeline-demandante | 4 | venta×subasta (SAE/entidades) · venta×directa (privados+societarios) · arriendo · administración |
| pipeline-oferente | 1 | captación (Steven) |
| chatbot-precalificacion | 3 | ventas, arriendos, captación — bases de conocimiento distintas |
| calendario-visitas | parcial | ✔ societarios y privados · **✘ SAE: bloqueado_por_tercero** |
| solicitud-habilitador | 2 | ventas y arriendos hacia territoriales/SAE (mitiga F-15) |
| scoring-contacto | 1–2 | señal principal: registro en Activit (50 pts) — requiere integracion-plataforma |
| integracion-plataforma | 1 | Activit (registro + Sagrilaft + expresiones) — R-06, fase condicionada |
| documento-interes | 1 | expresión de interés (F-14), diseñada en vivo en la sesión |
| telefonia-llamadas | por validar | la sesión no exploró el canal telefónico de Activos — pregunta pendiente del guión. Si aplica: +3 pts |
| llamada-ia-fuera-horario | por validar | condicionado al anterior |
| pipeline-operativo | por validar | posesiones y entregas podrían ser el caso de uso; no capturado en sesión |
| precaptacion-movil | 1 | recorridos de Steven |

Conteo de esfuerzo (solo Gestión, plan Inteligente): ~49 base + ~28 por
instancias ≈ **77 puntos ≈ 38 jornadas**. El multiplicador explica por qué este
cliente cuesta ~2.3× la primera instancia — exactamente lo que el modelo de
3 planes × complejidad debía capturar.

Exclusiones declaradas (V8): sincronización con sistemas SAE
(`integrable: no`, evidencia en transcripción); calendario para línea SAE.
Ambas van en la propuesta como limitaciones, no como promesas.

---

## C. Diccionario de métricas — v0.1 (derivado de Gestión)

Toda métrica citada en `metrica_que_habilita` debe existir aquí. Regla V3/V9.

| id | Definición | Componente fuente |
|---|---|---|
| `conversaciones_entrantes_mes` | Conversaciones nuevas iniciadas por el contacto, por mes | whatsapp-api |
| `conversaciones_por_canal` | Lo anterior segmentado por canal de origen | canales-unificados |
| `tiempo_primera_respuesta` | Mediana de minutos entre primer mensaje del contacto y primera respuesta (humana o IA) | canales-unificados |
| `pct_respondidos_5min` | % de conversaciones con primera respuesta < 5 min | respuesta-inmediata |
| `leads_fuera_horario` | Conversaciones iniciadas fuera del horario declarado | respuesta-inmediata |
| `leads_por_fuente` / `atribucion_*` | Contactos nuevos por primera/última fuente | campos-atribucion |
| `leads_por_linea` | Contactos ruteados por línea de negocio | ruteo-intencion |
| `leads_asignados_por_asesor` / `distribucion_carga` | Asignaciones por persona; desviación contra el promedio | asignacion-leads |
| `conversaciones_atendidas_por_ia` | Conversaciones resueltas sin humano | chatbot |
| `tasa_escalamiento` | % de conversaciones IA que pasan a humano | chatbot |
| `leads_precalificados_ia` | Contactos con calificación completa capturada por IA | chatbot |
| `tasa_calificacion` | % de leads con campos de calificación completos | campos-calificacion |
| `conversion_por_etapa` | % que avanza de cada etapa a la siguiente, por pipeline e instancia | pipeline-demandante |
| `dias_en_etapa` | Mediana de días por etapa | pipeline-demandante |
| `oportunidades_abiertas_valor` | Conteo y valor monetario de oportunidades abiertas | pipeline-demandante |
| `motivos_perdida` | Distribución de motivos al marcar perdida | pipeline-demandante |
| `captaciones_mes` / `conversion_precaptacion_contrato` | Embudo oferente | pipeline-oferente |
| `precaptaciones_mes_por_ejecutivo` | Registros de campo por persona | precaptacion-movil |
| `citas_agendadas` / `tasa_show_up` | Citas creadas; % que ocurre | calendario-visitas |
| `ciclo_solicitud_a_visita` | Días entre solicitud al habilitador y visita realizada. **La métrica que arma la renegociación con el tercero (F-15/F-17)** | solicitud-habilitador |
| `tareas_vencidas` / `oportunidades_estancadas` | Tareas fuera de SLA; oportunidades sin movimiento sobre el SLA de su etapa | tareas-sla |
| `distribucion_score` / `conversion_por_banda_score` | Contactos por banda; conversión comparada entre bandas | scoring-contacto |
| `tasa_registro_leads` | % de leads que completa el registro externo | integracion-plataforma |
| `tasa_firma` / `ciclo_solicitud_firma` | % de documentos firmados; horas hasta la firma | documento-interes |
| `llamadas_recibidas` / `llamadas_perdidas` / `tasa_atencion_llamadas` / `grabaciones_disponibles` | El canal telefónico medido: entrantes, perdidas, % atendidas, respaldo en grabación | telefonia-llamadas |
| `llamadas_fuera_horario_atendidas` / `casos_radicados_por_ia` | Lo que antes sonaba y se perdía, ahora atendido y radicado | llamada-ia-fuera-horario |
| `solicitudes_operativas_mes` / `ciclo_resolucion_operativa` / `solicitudes_vencidas_operativas` | El embudo no comercial con SLA — protege al comercial y mide al operativo | pipeline-operativo |

Convenciones: períodos en mes calendario; medianas y no promedios para tiempos;
toda métrica declara su instancia (línea, territorio) cuando el componente se
multiplica.

---

## D. Pendientes que este módulo dejó

1. Las **plantillas de mensaje** referenciadas (bienvenida-linea, fuera-horario,
   menu-intencion, solicitud-llaves) son componentes tipo `plantilla_mensaje`
   que hay que poblar con el módulo — quedaron como referencias.
2. `mecanismo_de_cierre` se usó como eje de instanciación del pipeline
   demandante: confirmar que la ficha v0.2 lo captura por línea (lo hace) y que
   el guión lo pregunta (Bloque 4 ampliado).
3. La frontera Fundamental/Avanzado quedó implícita en este módulo:
   **Fundamental = ningún lead se pierde ni queda sin dueño; Avanzado = el
   sistema atiende y agenda por ti; Inteligente = el sistema sabe quién vale
   más.** Primera candidata a matriz de fronteras — validar contra los otros
   seis módulos.

---

---

## E. Adenda v0.2 — el canal de voz: dos vías, no una

Consolidado tras detectar duplicación. Componentes canónicos:

| Componente | Plan | Rol |
|---|---|---|
| `gestion-telefonia-llamadas` | fundamental | PSTN (Twilio/LC Phone) con tipo `telefonia`: numeración, IVR, grabación con base legal declarada, registro completo. Cierra C-04 |
| `gestion-llamadas-whatsapp` | fundamental | Voz dentro del hilo de WhatsApp: entrantes **gratis**, salientes con permiso y por minuto (CO ~US$0,0117) |
| `gestion-llamada-perdida` | fundamental | Rescate: mensaje al minuto + tarea + escalamiento. Cierra F-18 en ambas vías |
| `gestion-llamada-ia-fuera-horario` | **inteligente** | Habilidad `recepcionista_voz` N3 |
| `gestion-pipeline-operativo` | fundamental | El destino que el ruteo necesita |

**No son alternativas: resuelven cosas distintas.**

| Necesidad | Vía |
|---|---|
| El cliente ya tiene un número publicado en avisos, vitrinas, vallas | PSTN — hay que contestar donde ya llaman |
| Atribución por canal con número dedicado | PSTN — WhatsApp no da números por canal |
| Menú/IVR y grabación de la llamada | PSTN — WhatsApp Calling no graba audio, solo registra la llamada y su resultado |
| Recibir llamadas de voz sin costo por minuto | WhatsApp — la entrante es gratis y no pide permiso |
| Que la llamada quede en el mismo hilo del chat, con contexto | WhatsApp |
| Llamar al lead caliente que acaba de escribir | WhatsApp si hay permiso; PSTN si no |

Regla para la propuesta: **PSTN es el canal del número público; WhatsApp Calling
es el canal de la conversación.** Un cliente con línea publicada y volumen de
chat necesita las dos, y son baratas por separado.

### El triángulo del número (nodo de decisión, va en la sesión)

El cliente casi nunca sabe que estas tres cosas no se pueden tener juntas:

| Opción | Gana | Pierde |
|---|---|---|
| Deja su número en la **app de WhatsApp Business** (coexistencia) | El equipo sigue usando la app como siempre | **No puede llamar por WhatsApp** (R-09) y la automatización queda a medias |
| **Migra su número a la API** | Canal completo: automatización, plantillas, llamadas | Ese número deja de usarse en la app del celular |
| Toma un **número nuevo Twilio/LC para WhatsApp** | Conserva intacto el número viejo en la app | Es un **fijo** y hay que publicarlo desde cero |

Esta decisión pertenece a la ficha, no al runbook: cambia lo que se puede
prometer y en qué orden se implementa. Sin ella, la propuesta promete llamadas a
un cliente que no puede hacerlas.

Tres advertencias de cronograma y expectativa:

1. **El número viejo no se apaga.** Está impreso en avisos, vitrinas y
   contratos: se conservan ambos con desvío por meses.
2. **Grabar exige aviso** en PSTN (`grabacion.base_legal_declarada` es campo
   obligatorio); en WhatsApp Calling **no hay grabación de audio** — prometerla
   es prometer lo que la plataforma no da.
3. **F-18 casi siempre nace en modo B.** Nadie sabe cuántas llamadas pierde
   antes de medirlas; el tablero produce el dato que la propuesta no pudo.

---

## F. Adenda v0.2 — dónde vive el filtrado y la calificación

Estaba repartido en cuatro capas sin un mapa, y eso lo volvía difícil de
encontrar y de vender. No se consolida en un componente: **son cuatro capas
deliberadas, en tres módulos y tres planes**, y cada una filtra algo que la
anterior no puede.

| # | Capa | Componente | Módulo · Plan | Qué filtra |
|---|---|---|---|---|
| 1 | **En origen** | `atraccion-formularios-precalificacion` | Atracción · Fundamental | El curioso no entra: preguntas descalificadoras antes del primer contacto. Cierra F-13 donde es más barato |
| 2 | **Estructura del dato** | `gestion-campos-calificacion` | Gestión · Fundamental | Nada: habilita. Sin campos, calificar es una opinión en una nota de voz |
| 3a | **Conversación · informar** | `gestion-asistente-informativo` (habilidad `informativo`) | Gestión · Avanzado | Al que llegó por chat: responde proceso, requisitos y estado del catálogo 24/7 |
| 3b | **Conversación · precalificar** | `gestion-precalificador` (habilidad `precalificador`) | Gestión · **Inteligente** | Al mismo, pero inferido: triage, temperatura y entrega del lead desmenuzado |
| 4 | **Aritmética** | `gestion-scoring-contacto` | Gestión · **Inteligente** | Prioriza entre los que sí pasan: pondera señales, aplica umbrales y descalificadores |

Refuerzos aguas abajo, mismo mecanismo: `nutricion-encuesta-recalificacion`
(el que cambió de situación se reclasifica), `cierre-señales-decision` (suma
score por comportamiento), `fidelizacion-tiers-valor` (scoring de clientes, no
de leads), `reactivacion-absorcion-oleadas` (clasifica al que despertó).

Tres reglas que este mapa hace explícitas:

- **Scoring es Inteligente, y está validado en campo**: en la propuesta real de
  AYC el scoring y la habilidad precalificadora fueron exactamente lo que se
  apagó al bajar de Inteligente a Avanzado. La frontera coincide con la práctica.
- **Filtrar no es descartar.** Ninguna capa borra: clasifican y etiquetan
  (`candidato_reactivacion`). Regla anti F-17, transversal a las cuatro.
- **El descalificador duro suele ser dato externo.** El caso canónico: "reportado
  en centrales de riesgo" — no lo sabe el CRM, lo sabe el sistema del cliente o
  un tercero. Por eso `scoring.variables[].fuente_del_dato` es obligatorio: si la
  señal no tiene fuente, el umbral es decorativo.

---

## G. Componentes por crear (C6 · catálogo de habilidades §5)

**No se crean todavía.** El catálogo v1.1 lista cinco habilidades sin componente
en la librería; esta es la lista pendiente, aquí para que no se pierda y para que
nadie la implemente por su cuenta. Crearlos exige decidir plan, esfuerzo, fugas y
`aplica_si`, y eso es decisión de producto.

| Por crear | Habilidad | Plan de entrada (catálogo) | Nota del catálogo |
|---|---|---|---|
| recepcionista de chat como `chatbot_ia` propio | `recepcionista` | fundamental (N1) | hoy solo existe `gestion-ruteo-intencion`, que lo cubre **parcialmente** (§3.1) |
| `agendador` conversacional | `agendador` | avanzado | el tipo `calendario` existe; la habilidad conversacional no (§3.3) |
| `asesor_recomendador` | `asesor_recomendador` | inteligente | la matriz la lista, la librería no la tiene (§3.6). Exige catálogo vivo con dueño (H5) |
| `gestion-preaprobacion-credito` | `preaprobador_credito` | inteligente, **condicionada** | `aplica_si` vertical con venta financiada; `costo_externo: consumo_variable`; su spec E4 corre `calculo_roi` obligatorio (§3.11) |
| `integracion` de consulta a buró | — (soporte del anterior) | — | componente `integracion` aparte; por V11 lo no nativo no viaja dentro del plan |

Dos cosas que estos componentes arrastran cuando se creen: **H3** (su
`plan_minimo` no puede ser menor que el `plan_entrada` de su habilidad) y **H6**
(el preaprobador no se activa sin variables de semáforo y habeas data aprobados y
versionados). La familia transaccional del Vendedor Virtual (§3.12) **no** entra
en esta lista: es producto aparte y no se repliega a los planes.
