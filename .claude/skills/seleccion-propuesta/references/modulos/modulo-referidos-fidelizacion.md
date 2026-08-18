# Módulo Referidos y Fidelización — Librería de componentes v0.1

9 componentes conforme al schema v0.2.2. Fidelización = el cliente que firmó
sigue siendo atendido, renueva y recompra. Referidos = ese cliente trae al
siguiente. **Fronteras**: la reseña pública es Reputación (Atracción); el
dormido que nunca compró es Reactivación.

**Argumento de venta mixto**: Fidelización sí tiene fugas (F-11 ~4/53,
F-12 ~2/53). Referidos no tiene ninguna —cero menciones en 264 dolores— y se
vende desde un dato que el Bloque 1 del guión ya captura: **el % de ventas que
hoy llega por referido espontáneo**. Ese número es la línea base del argumento:
"esto ya te pasa sin sistema; esto es sistematizarlo", no una fuga inventada.

---

## A. Componentes

### Cobertura del cliente cerrado (posicion_journey 110–115)

```yaml
id: fidelizacion-onboarding-postfirma
nombre_interno: "Secuencia de bienvenida y onboarding disparada por cerrada_ganada"
nombre_cliente: "El cliente que firma sabe exactamente qué sigue, sin perseguir a nadie"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 110
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
depende_de: [cierre-contrato-firma, nutricion-plantillas-whatsapp]
cierra_fugas: []
mitiga_fugas: [F-11]                      # el abandono post-venta empieza el día uno
metrica_que_habilita: [onboardings_completados, tiempo_firma_primer_contacto_postventa]
esfuerzo_base: 2
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: cambio_etapa, condicion: cerrada_ganada }
  acciones:
    - { orden: 1, tipo: mensaje, plantilla_ref: bienvenida-y-pasos, espera_min: 0 }
    - { orden: 2, tipo: crear_tarea, asigna_a_funcion: postventa_administracion }
    - { orden: 3, tipo: mensaje, plantilla_ref: checkin-semana-1, espera_min: 10080 }
```

```yaml
id: fidelizacion-hitos-vencimientos
nombre_interno: "Registro y alertas de hitos: renovaciones, vencimientos documentales, aniversarios"
nombre_cliente: "Ninguna renovación vuelve a vencerse en silencio"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 112
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "linea.naturaleza in [recurrente, mixta] o existen documentos con vencimiento"
depende_de: [gestion-base-contactos]
cierra_fugas: [F-12]
metrica_que_habilita: [hitos_proximos_30d, renovaciones_a_tiempo_pct]
esfuerzo_base: 2
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: fecha_hito, condicion: "D-60, D-30, D-7" }
  acciones:
    - { orden: 1, tipo: mensaje, plantilla_ref: recordatorio-renovacion, asigna_a_funcion: null }
    - { orden: 2, tipo: crear_tarea, asigna_a_funcion: postventa_administracion, condicion: "D-30 sin respuesta" }
  nota: "El hito vive como campo de fecha en el contrato/cliente; la automatización solo lee. Capturar la fecha es parte del onboarding (componente anterior)."
```

```yaml
id: fidelizacion-segmento-clientes
nombre_interno: "Segmentación de clientes activos por línea, valor y antigüedad"
nombre_cliente: "Tus clientes dejan de ser una lista: son grupos con trato propio"
tipo: segmento
visibilidad_cliente: back
posicion_journey: 111
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [gestion-base-contactos]
cierra_fugas: []
metrica_que_habilita: [clientes_activos, clientes_sin_contacto_90d]
esfuerzo_base: 1
esfuerzo_por_instancia: 0
detalle:
  mecanismo: smart_list
  criterios: [linea, valor_acumulado, antiguedad, ultimo_contacto]
  uso: [fidelizacion-secuencia-recompra, referidos-solicitud, fidelizacion-señales-riesgo]
```

### Recompra y voz del cliente (116–119)

```yaml
id: fidelizacion-secuencia-recompra
nombre_interno: "Secuencias de recompra y venta cruzada entre líneas"
nombre_cliente: "El que arrendó contigo se entera cuando le conviene comprar — y al revés"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 116
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
depende_de: [fidelizacion-segmento-clientes, nutricion-plantillas-whatsapp]
cierra_fugas: [F-11]
metrica_que_habilita: [tasa_recompra, ventas_cruzadas_mes]
esfuerzo_base: 3
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: programado_o_evento, filtros: [aniversario_compra, cambio_situacion, nuevo_catalogo_compatible] }
  acciones:
    - { orden: 1, tipo: mensaje, plantilla_ref: oferta-cruzada-por-linea }
  nota: "En negocios multilínea con base compartida, esta es la razón económica de que comparte_base_contactos exista: el cliente de una línea es el lead más barato de la otra."
```

```yaml
id: fidelizacion-encuesta-satisfaccion
nombre_interno: "Encuesta de satisfacción periódica (NPS) con derivación por resultado"
nombre_cliente: "Saber quién está feliz y quién está por irse, antes de que pase"
tipo: formulario
visibilidad_cliente: front
posicion_journey: 117
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [fidelizacion-segmento-clientes]
cierra_fugas: []
metrica_que_habilita: [nps, tasa_respuesta_nps]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  campos:
    - { etiqueta: "0-10 ¿nos recomendarías?", campo_destino: nps_score, obligatorio: true }
    - { etiqueta: "¿por qué?", campo_destino: nps_motivo, obligatorio: false }
  destino: { pipeline_ref: null, etapa: null }
  accion_post_envio: "promotor → referidos-solicitud y reputacion-solicitud-resenas; detractor → caso interno a coordinador"
  nota: "Una sola encuesta alimenta tres sistemas: referidos, reseñas y alerta de riesgo. Se pregunta una vez, se usa tres veces."
```

```yaml
id: referidos-solicitud
nombre_interno: "Programa de referidos: solicitud post-satisfacción con link único y registro referidor→referido"
nombre_cliente: "El cliente contento trae al siguiente, y tú sabes exactamente quién trajo a quién"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 118
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
depende_de: [fidelizacion-encuesta-satisfaccion, gestion-campos-atribucion]
cierra_fugas: []                          # oportunidad, no fuga — línea base: % referido espontáneo del Bloque 1
metrica_que_habilita: [referidos_solicitados, tasa_referido, leads_por_referido, clientes_referidores_pct]
esfuerzo_base: 3
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: evento, condicion: "nps promotor o hito exitoso" }
  acciones:
    - { orden: 1, tipo: mensaje, plantilla_ref: invitacion-referido-con-link }
    - { orden: 2, tipo: registrar_relacion, condicion: "referido entra con primera_fuente = referido + referidor_id" }
  nota: "El link único hace dos cosas: le quita fricción al referidor y convierte 'me recomendaron' en un dato con nombre. Sin registro no hay programa — hay esperanza."
```

```yaml
id: referidos-reconocimiento
nombre_interno: "Mecánica de reconocimiento/incentivo al referidor con registro y cumplimiento"
nombre_cliente: "El que refiere recibe algo real, automático y a tiempo — por eso vuelve a referir"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 119
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [referidos-solicitud]
cierra_fugas: []
metrica_que_habilita: [incentivos_entregados, referidores_recurrentes]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: cambio_etapa, condicion: "referido llega a cerrada_ganada" }
  acciones:
    - { orden: 1, tipo: mensaje, plantilla_ref: gracias-referidor }
    - { orden: 2, tipo: crear_tarea, asigna_a_funcion: coordinador, condicion: "entregar incentivo definido por el cliente" }
  nota: "La mecánica del incentivo (descuento, bono, reconocimiento) es decisión del cliente; el componente garantiza que se dispare, se registre y no se olvide."
```

### Iniciativa (120+)

```yaml
id: fidelizacion-señales-riesgo
nombre_interno: "Detección de señales de churn en clientes recurrentes con playbook de retención"
nombre_cliente: "El cliente que se está enfriando se detecta por sus señales, no por su carta de retiro"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 120
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
aplica_si: "linea.naturaleza in [recurrente, mixta]"
depende_de: [fidelizacion-segmento-clientes, fidelizacion-encuesta-satisfaccion]
cierra_fugas: []
mitiga_fugas: [F-11]
metrica_que_habilita: [señales_riesgo_detectadas, retenciones_logradas]
esfuerzo_base: 3
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: señal, filtros: [sin_contacto_90d, nps_detractor, queja_abierta, pago_tardio] }
  acciones:
    - { orden: 1, tipo: crear_tarea, asigna_a_funcion: postventa_administracion, condicion: "playbook de retención por señal" }
    - { orden: 2, tipo: notificar, asigna_a_funcion: coordinador, condicion: "cliente de alto valor" }
```

```yaml
id: fidelizacion-tiers-valor
nombre_interno: "Clasificación de clientes por valor acumulado con trato diferenciado"
nombre_cliente: "Tus mejores clientes reciben tu mejor atención — de forma automática, no de memoria"
tipo: scoring
visibilidad_cliente: back
posicion_journey: 121
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [fidelizacion-segmento-clientes, gestion-scoring-contacto]
cierra_fugas: []
metrica_que_habilita: [distribucion_tiers, valor_por_tier]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  sujeto: contacto
  escala: { min: 0, max: 100 }
  variables:
    - { señal: valor_acumulado, puntos: 50, fuente_del_dato: crm, es_descalificadora: false }
    - { señal: antiguedad, puntos: 20, fuente_del_dato: crm, es_descalificadora: false }
    - { señal: referidos_generados, puntos: 20, fuente_del_dato: referidos-solicitud, es_descalificadora: false }
    - { señal: nps_promotor, puntos: 10, fuente_del_dato: encuesta-satisfaccion, es_descalificadora: false }
  umbrales:
    - { nombre: VIP, min: 70, accion: "SLA preferente + gestor asignado" }
    - { nombre: en_desarrollo, min: 30, accion: "secuencia de recompra activa" }
  nota: "Que referir sume al tier cierra el circuito: el mejor cliente no es solo el que más compra, es el que más trae."
```

### Validaciones del módulo

- **V1** ✔ señales-riesgo y tiers-valor (inteligente) dependen de avanzados o de
  scoring (inteligente).
- **V2** ✔ referencias a Gestión, Nutrición, Cierre y Atracción existen.
- **V6** ✔ F-11 cerrada por secuencia-recompra, mitigada por onboarding y
  señales-riesgo. F-12 cerrada por hitos-vencimientos. Los cuatro componentes de
  referidos no citan fugas — argumento de oportunidad con línea base del
  Bloque 1, misma disciplina que Reputación.
- **V7** ✔ Journey 110–121, el tramo final. Igual que Reputación, Referidos es
  un lazo de retorno: `leads_por_referido` alimenta la primera etapa del journey
  vía `primera_fuente = referido`. Segunda geometría no lineal para el lienzo.

---

## B. Validación contra el piloto

| Componente | Instancias | Detalle |
|---|---|---|
| onboarding-postfirma | 2 | arriendo firmado y venta escriturada |
| hitos-vencimientos | 2 | **F-12 literal en la línea de administración**: renovaciones anuales de contratos de arriendo y mandatos de administración (Steven administra comercial/industrial) |
| segmento-clientes | 1 | |
| secuencia-recompra | 2 | los cruces naturales: arrendatario → comprador; propietario que vendió → vuelve a consignar |
| encuesta-satisfaccion | 1 | alimenta además la compuerta de Reputación |
| referidos-solicitud | 2 | **el referido más valioso del caso es el oferente**: un propietario satisfecho refiere a otro propietario — inventario, no demanda. Steven lo dijo en sesión: "encontramos clientes por propietario" |
| referidos-reconocimiento | 1 | mecánica a definir por el cliente |
| señales-riesgo | 1 | línea de administración (la única recurrente pura) |
| tiers-valor | 1 | |

Esfuerzo plan Inteligente: ~20 base + ~10 instancias ≈ **30 puntos ≈ 15
jornadas**. Acumulado 6 módulos: ~272 puntos.

Dato faltante del piloto para este módulo: % de ventas por referido espontáneo —
el Bloque 1 lo pregunta, la sesión no llegó ahí. Modo B para el argumento de
referidos hasta capturarlo.

---

## C. Métricas agregadas al diccionario (v0.6)

| id | Definición | Fuente |
|---|---|---|
| `onboardings_completados` / `tiempo_firma_primer_contacto_postventa` | Cobertura del día uno post-firma | onboarding |
| `hitos_proximos_30d` / `renovaciones_a_tiempo_pct` | Salud del calendario de vencimientos. **Medición real de F-12** | hitos-vencimientos |
| `clientes_activos` / `clientes_sin_contacto_90d` | La segunda es la fuga F-11 hecha número vivo | segmento-clientes |
| `tasa_recompra` / `ventas_cruzadas_mes` | Rendimiento de recompra. **Medición real de `tasa_recompra_incremental` de F-11** | secuencia-recompra |
| `nps` / `tasa_respuesta_nps` | Voz del cliente | encuesta-satisfaccion |
| `referidos_solicitados` / `tasa_referido` / `leads_por_referido` / `clientes_referidores_pct` | El embudo de referidos completo, contra la línea base espontánea del Bloque 1 | referidos-solicitud |
| `incentivos_entregados` / `referidores_recurrentes` | Cumplimiento y recurrencia del programa | referidos-reconocimiento |
| `señales_riesgo_detectadas` / `retenciones_logradas` | Churn anticipado | señales-riesgo |
| `distribucion_tiers` / `valor_por_tier` | Composición de la cartera de clientes | tiers-valor |

---

## D. Pendientes y frontera

1. Plantillas del módulo (bienvenida, recordatorios de renovación, invitación de
   referido): con los snapshots.
2. El guión necesita la pregunta de referidos del Bloque nuevo con un matiz que
   el piloto enseñó: en negocios con embudo oferente, preguntar por referidos
   **de ambos lados** — quién refiere compradores y quién refiere propietarios.
3. **Frontera, sexta confirmación**: Fundamental = ningún cliente cerrado queda
   sin contacto ni hito vencido (cobertura); Avanzado = recompra, voz del
   cliente y referidos con sistema (sustancia); Inteligente = el riesgo se
   detecta y el mejor cliente se reconoce solo (iniciativa).
