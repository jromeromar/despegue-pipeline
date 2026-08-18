# Módulo Nutrición — Librería de componentes v0.1

10 componentes conforme al schema v0.2. Nutrición = mantener vivo al lead
interesado que aún no compra. **Fronteras**: la base antigua dormida es
Reactivación (F-10); la propuesta enviada sin retomar es Cierre (F-04); el
cliente que ya compró es Fidelización (F-11). Las 3.900 conversaciones
represadas del piloto son Reactivación, no Nutrición — entraron y nunca se
atendieron; nutrir presupone que hubo conversación.

---

## A. Componentes

### Cimiento (posicion_journey 50–54)

```yaml
id: nutricion-plantillas-whatsapp
nombre_interno: "Set de plantillas WhatsApp aprobadas por Meta para seguimiento fuera de ventana"
nombre_cliente: "Mensajes de seguimiento que sí llegan, aunque hayan pasado días"
tipo: plantilla_mensaje
visibilidad_cliente: front
posicion_journey: 50
plan_minimo: fundamental
mecanismo_entrega: contenido_a_medida     # se redactan con el lenguaje del cliente
se_instancia_por: [linea_negocio]
depende_de: [gestion-whatsapp-api]
cierra_fugas: []                          # resuelve R-01, prerrequisito de toda secuencia
metrica_que_habilita: [plantillas_aprobadas, tasa_entrega_plantilla]
esfuerzo_base: 2
esfuerzo_por_instancia: 1
prerequisito_plataforma: ["Aprobación de Meta por plantilla (R-05: 1–5 días, afecta cronograma)"]
detalle:
  canal: whatsapp
  proposito: seguimiento_fuera_de_ventana
  variables: [nombre, activo_de_interes, siguiente_paso]
  requiere_aprobacion_meta: true
```

```yaml
id: nutricion-segmentos
nombre_interno: "Segmentación por línea, interés, etapa y temperatura"
nombre_cliente: "Hablarle a cada grupo de lo que le importa, no a todos de todo"
tipo: segmento
visibilidad_cliente: back
posicion_journey: 52
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [unico]                 # un sistema de segmentos con criterios por línea
depende_de: [gestion-base-contactos, gestion-campos-calificacion]
cierra_fugas: []                          # habilita todo lo demás; sin esto la nutrición es spam
metrica_que_habilita: [contactos_por_segmento]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  mecanismo: smart_list
  criterios: [linea_de_interes, etapa_pipeline, temperatura, territorio]
  uso: [nutricion-secuencia-no-respuesta, nutricion-email-goteo, nutricion-alertas-catalogo]
```

### Secuencias (55–64)

```yaml
id: nutricion-secuencia-no-respuesta
nombre_interno: "Secuencia multi-toque para lead que dejó de responder (D+1, D+3, D+7, D+15)"
nombre_cliente: "Nadie vuelve a perderse por falta de seguimiento: el sistema insiste por ti"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 55
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio, sujeto_del_embudo]
aplica_si: "linea.sujeto_del_embudo == demandante"
depende_de: [nutricion-plantillas-whatsapp, nutricion-segmentos, gestion-pipeline-demandante]
cierra_fugas: [F-01]                      # la fuga más frecuente del set: ~25/53
metrica_que_habilita: [leads_en_secuencia, tasa_respuesta_seguimiento, recuperados_por_secuencia]
esfuerzo_base: 3
esfuerzo_por_instancia: 2
detalle:
  disparador: { tipo: sin_respuesta_contacto, condicion: "24h sin respuesta y etapa activa" }
  acciones:
    - { orden: 1, tipo: mensaje, canal: whatsapp, plantilla_ref: seguimiento-d1, espera_min: 1440 }
    - { orden: 2, tipo: mensaje, canal: whatsapp, plantilla_ref: seguimiento-d3, espera_min: 4320 }
    - { orden: 3, tipo: mensaje, canal: whatsapp, plantilla_ref: seguimiento-d7-valor, espera_min: 10080 }
    - { orden: 4, tipo: mensaje, canal: whatsapp, plantilla_ref: seguimiento-d15-cierre, espera_min: 21600 }
  condiciones_salida: [contacto_respondio, cambio_de_etapa, opt_out]
  ramas:
    - { condicion: "fin de secuencia sin respuesta", acciones: [{ tipo: mover_a_etapa, condicion: "dormido" }, { tipo: etiquetar, condicion: "candidato_reactivacion" }] }
  nota: "El paso a 'dormido' es la compuerta hacia Reactivación: nada se descarta, todo se clasifica (anti F-17)."
```

```yaml
id: nutricion-secuencia-oferente
nombre_interno: "Secuencia de retoma al propietario que dijo 'ahora no'"
nombre_cliente: "El propietario que no firmó hoy recibe razones para firmar mañana"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 56
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "existe linea con sujeto_del_embudo == oferente"
depende_de: [nutricion-plantillas-whatsapp, gestion-pipeline-oferente]
cierra_fugas: [FO-02]
metrica_que_habilita: [oferentes_en_secuencia, captaciones_por_retoma]
esfuerzo_base: 3
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: cambio_etapa, condicion: "oferente en 'ahora no' o sin respuesta" }
  acciones:
    - { orden: 1, tipo: mensaje, plantilla_ref: oferente-caso-exito-zona, espera_min: 20160 }
    - { orden: 2, tipo: mensaje, plantilla_ref: oferente-mercado-actualizado, espera_min: 43200 }
    - { orden: 3, tipo: crear_tarea, asigna_a_funcion: captador, espera_min: 43200 }
  condiciones_salida: [firmo_con_nosotros, vendio_por_otro_lado, opt_out]
  nota: "El lenguaje es de dueño de activo (valorización, demanda de la zona), nunca de comprador."
```

```yaml
id: nutricion-nueva-oportunidad-catalogo
nombre_interno: "Alertas de coincidencia: nuevo ítem del catálogo que empata con el interés registrado"
nombre_cliente: "Cuando entra algo que le sirve a tu lead, él es el primero en saberlo"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 58
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "existe catálogo estructurado con atributos consultables"
depende_de: [nutricion-segmentos, gestion-campos-calificacion]
cierra_fugas: []
mitiga_fugas: [F-01]                      # da motivo genuino de contacto: nutrición con sustancia
metrica_que_habilita: [alertas_enviadas, respuesta_a_alerta, conversion_por_alerta]
esfuerzo_base: 4
esfuerzo_por_instancia: 2
prerequisito_plataforma: ["Catálogo con atributos estructurados (tipo, zona, rango de precio) accesible por API o carga periódica"]
detalle:
  disparador: { tipo: nuevo_item_catalogo }
  acciones:
    - { orden: 1, tipo: match, condicion: "atributos del ítem vs interés del segmento" }
    - { orden: 2, tipo: mensaje, canal: whatsapp, plantilla_ref: nueva-coincidencia }
  nota: "Es la nutrición natural de negocios con inventario: el mensaje no es '¿sigues ahí?' sino 'llegó lo que buscabas'."
```

### Contenido y ciclo largo (60–66)

```yaml
id: nutricion-email-goteo
nombre_interno: "Secuencia de email por goteo para ciclo largo, segmentada por línea"
nombre_cliente: "El lead de decisión lenta recibe valor cada semana hasta que esté listo"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 60
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "linea.ciclo_dias >= 30 y contactos con email > umbral"
depende_de: [nutricion-segmentos, nutricion-contenido-valor]
cierra_fugas: []
mitiga_fugas: [F-01]
metrica_que_habilita: [tasa_apertura_email, tasa_clic_email, bajas_email]
esfuerzo_base: 3
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: entrada_a_segmento, condicion: "interesado sin urgencia" }
  acciones: "4–6 correos de valor + 1 de conversión, cadencia semanal"
  condiciones_salida: [avanzo_de_etapa, opt_out]
```

```yaml
id: nutricion-contenido-valor
nombre_interno: "Paquete de piezas de nutrición por línea (guías, checklists, comparativas)"
nombre_cliente: "Material que educa a tu lead y posiciona a tu equipo como el experto"
tipo: contenido
visibilidad_cliente: front
posicion_journey: 59
plan_minimo: avanzado
mecanismo_entrega: contenido_a_medida
se_instancia_por: [linea_negocio]
depende_de: []
cierra_fugas: []
metrica_que_habilita: []
esfuerzo_base: 4
esfuerzo_por_instancia: 3
detalle:
  piezas:
    - { tipo: guia_pdf, cantidad: 1, quien_produce: ropofy_con_insumos_cliente }
    - { tipo: mensajes_de_valor, cantidad: 6, quien_produce: ropofy_con_insumos_cliente }
  nota: "Sin contenido, las secuencias largas degeneran en '¿ya decidiste?'. Este componente es el que las alimenta."
```

```yaml
id: nutricion-encuesta-recalificacion
nombre_interno: "Encuesta corta de recalificación a mitad de secuencia"
nombre_cliente: "Preguntarle al lead qué cambió, y ajustar el trato según su respuesta"
tipo: formulario
visibilidad_cliente: front
posicion_journey: 62
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
depende_de: [nutricion-secuencia-no-respuesta]
cierra_fugas: []
metrica_que_habilita: [tasa_respuesta_encuesta, cambios_de_temperatura]
esfuerzo_base: 2
esfuerzo_por_instancia: 1
detalle:
  campos:
    - { etiqueta: "¿Sigues buscando?", campo_destino: temperatura, obligatorio: true }
    - { etiqueta: "¿Qué cambió?", campo_destino: motivo_pausa, obligatorio: false }
  destino: { pipeline_ref: gestion-pipeline-demandante, etapa: segun_respuesta }
  accion_post_envio: nutricion-triggers-comportamiento
```

### Señales (65+)

```yaml
id: nutricion-triggers-comportamiento
nombre_interno: "Disparadores por señal de intención: clic, apertura, revisita, respuesta a alerta"
nombre_cliente: "Cuando el lead da señales de vida, tu asesor lo sabe en el momento"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 65
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [nutricion-email-goteo, gestion-scoring-contacto]
cierra_fugas: []
mitiga_fugas: [F-01]
metrica_que_habilita: [señales_detectadas_mes, tiempo_señal_a_contacto]
esfuerzo_base: 3
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: señal_comportamiento, filtros: [clic_email, respuesta_alerta, encuesta_positiva] }
  acciones:
    - { orden: 1, tipo: sumar_score, condicion: "vía gestion-scoring-contacto" }
    - { orden: 2, tipo: notificar, asigna_a_funcion: asesor, condicion: "score cruza umbral" }
```

```yaml
id: nutricion-reinyeccion-ia
nombre_interno: "Reinyección conversacional: la IA retoma el hilo tras N días con contexto completo"
nombre_cliente: "La conversación que se enfrió la retoma un asistente que recuerda todo"
tipo: chatbot_ia
visibilidad_cliente: front
posicion_journey: 66
plan_minimo: inteligente
mecanismo_entrega: contenido_a_medida
se_instancia_por: [linea_negocio]
depende_de: [gestion-chatbot-precalificacion, nutricion-plantillas-whatsapp]
cierra_fugas: []
mitiga_fugas: [F-01, F-08]
metrica_que_habilita: [conversaciones_reinyectadas, recuperados_por_ia]
esfuerzo_base: 4
esfuerzo_por_instancia: 2
prerequisito_plataforma: ["O-01: aprobar con el cliente tono y límites de la retoma automática"]
detalle:
  alcance: [retomar_hilo, actualizar_calificacion, reagendar]
  criterio_escalamiento: "intencion transaccional o solicitud de humano"
  handoff_a_funcion: asesor
  horario_activo: horario_declarado
  nota: "Resuelve el patrón 'el bot responde una vez y no reinyecta' (diagnóstico id 13)."
```

### Validaciones del módulo

- **V1** ✔ triggers-comportamiento (inteligente) depende de scoring (inteligente)
  y email-goteo (avanzado); reinyeccion-ia (inteligente) depende del chatbot
  (avanzado). Ninguna dependencia apunta hacia arriba.
- **V2** ✔ Referencias cruzadas a Gestión existen en modulo-gestion.md.
- **V6** ✔ F-01 se cierra con secuencia-no-respuesta; los demás componentes la
  mitigan por capas. FO-02 cerrada por secuencia-oferente.
- **V7** ✔ Nutrición vive en journey 50–66, después de todo Gestión (10–45).
- **Anti-F-17 estructural**: el fin de secuencia nunca descarta — mueve a
  "dormido" y etiqueta para Reactivación. La organización deja de necesitar
  cartas de desistimiento para limpiar su embudo.

---

## B. Validación contra el piloto

| Componente | Instancias | Detalle |
|---|---|---|
| plantillas-whatsapp | 3 | ventas, arriendos, captación — R-05 en cronograma |
| secuencia-no-respuesta | 3 | venta subasta, venta directa, arriendo (Tatiana hoy responde 80–85% pero nadie retoma al que calla) |
| secuencia-oferente | 1 | retoma de propietarios de Steven |
| nueva-oportunidad-catalogo | 2 | **el mejor fit del módulo**: 6.300 inmuebles y entregas masivas nuevas — cada entrega es una ronda de alertas a interesados compatibles. Requiere catálogo por API (R-06, mismo esfuerzo que integracion-plataforma) |
| email-goteo + contenido | 1–2 | ciclo largo natural en subasta |
| reinyeccion-ia | 2 | ventas y arriendos |

Esfuerzo Nutrición plan Inteligente para el piloto: ~30 base + ~19 instancias
≈ **49 puntos ≈ 24 jornadas**. Acumulado con Gestión: ~126 puntos.

Nota de frontera aplicada: las 3.900 conversaciones represadas **no** se
resuelven aquí. Van a Reactivación (envío masivo + IA de precalificación, como
lo planteó el consultor en la sesión). Nutrición evita que la bolsa se vuelva a
llenar.

---

## C. Métricas agregadas al diccionario (v0.2)

| id | Definición | Fuente |
|---|---|---|
| `leads_en_secuencia` | Contactos activos dentro de una secuencia de seguimiento | secuencia-no-respuesta |
| `tasa_respuesta_seguimiento` | % de contactos en secuencia que responden a algún toque | secuencia-no-respuesta |
| `recuperados_por_secuencia` | Contactos que avanzan de etapa tras entrar en secuencia. **Es la medición real de `tasa_recuperacion` de la fórmula F-01: deja de ser supuesto a los 90 días** | secuencia-no-respuesta |
| `oferentes_en_secuencia` / `captaciones_por_retoma` | Equivalentes del embudo oferente | secuencia-oferente |
| `alertas_enviadas` / `respuesta_a_alerta` / `conversion_por_alerta` | Embudo de coincidencias de catálogo | nueva-oportunidad-catalogo |
| `tasa_apertura_email` / `tasa_clic_email` / `bajas_email` | Estándar de email sobre enviados | email-goteo |
| `tasa_respuesta_encuesta` / `cambios_de_temperatura` | Recalificación a mitad de ciclo | encuesta-recalificacion |
| `señales_detectadas_mes` / `tiempo_señal_a_contacto` | Señales de intención y latencia hasta el contacto humano | triggers-comportamiento |
| `conversaciones_reinyectadas` / `recuperados_por_ia` | Retomas automáticas y su resultado | reinyeccion-ia |
| `contactos_por_segmento` | Tamaño de cada segmento activo | segmentos |
| `plantillas_aprobadas` / `tasa_entrega_plantilla` | Salud del canal WhatsApp fuera de ventana | plantillas-whatsapp |

`recuperados_por_secuencia` merece subrayarse: es la métrica que convierte el
supuesto conservador de la propuesta en dato medido del cliente, y por V9 debe
estar en un tablero de todo plan donde F-01 se haya cuantificado.

---

## D. Pendientes y hallazgo de frontera

1. Plantillas concretas (seguimiento-d1…d15, oferente-*, nueva-coincidencia):
   redacción por industria al construir los snapshots.
2. ~~`catalogo_estructurado` en la ficha~~ — resuelto: ficha v0.2, bloque D,
   sección "Catálogo del negocio" (`catalogo_estructurado`, `donde_vive`,
   `items_activos`).
3. **La frontera de planes se sostiene**: Fundamental = ningún interesado queda
   sin seguimiento; Avanzado = el sistema nutre con sustancia (contenido,
   catálogo, oferente); Inteligente = el sistema detecta señales y reacciona
   solo. Misma lógica que Gestión — la matriz de fronteras va tomando forma de
   patrón transversal: **cobertura → sustancia → iniciativa**.
