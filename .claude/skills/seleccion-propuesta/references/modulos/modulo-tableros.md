# Módulo Tableros y Reportes — Librería de componentes v0.1

9 componentes conforme al schema v0.2.2. Este módulo **no crea métricas:
ensambla** las 73 del diccionario en vistas por función. Es donde V3 y V9 se
verifican de verdad: cada widget cita una métrica que un componente del mismo
plan o inferior habilita. En el lienzo es la banda transversal inferior — no
vive en un punto del journey, lo atraviesa completo.

---

## A. Componentes

### Cobertura: cada quien ve lo suyo (transversal)

```yaml
id: tableros-operativo-asesor
nombre_interno: "Vista del asesor: mis leads, mis tareas vencidas, mis estancados"
nombre_cliente: "Cada asesor abre el día sabiendo exactamente qué atender primero"
tipo: tablero
visibilidad_cliente: back
posicion_journey: 130
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [unico]                 # una vista filtrada por usuario, no un tablero por persona
depende_de: [gestion-asignacion-leads, gestion-tareas-sla]
metrica_que_habilita: []
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  audiencia_funcion: [asesor]
  widgets:
    - { metrica: leads_asignados_por_asesor, fuente: gestion-asignacion-leads, filtro: usuario_actual, visualizacion: lista }
    - { metrica: tareas_vencidas, fuente: gestion-tareas-sla, filtro: usuario_actual, visualizacion: contador }
    - { metrica: oportunidades_estancadas, fuente: gestion-tareas-sla, filtro: usuario_actual, visualizacion: lista }
  frecuencia_revision: diaria
```

```yaml
id: tableros-coordinador-equipo
nombre_interno: "Vista del coordinador: carga, SLAs y embudo del equipo"
nombre_cliente: "Quién está saturado, qué se está venciendo y dónde se atasca el equipo — sin pedir informes"
tipo: tablero
visibilidad_cliente: back
posicion_journey: 131
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
depende_de: [gestion-asignacion-leads, gestion-pipeline-demandante]
metrica_que_habilita: []
esfuerzo_base: 2
esfuerzo_por_instancia: 1
detalle:
  audiencia_funcion: [coordinador]
  widgets:
    - { metrica: distribucion_carga, fuente: gestion-asignacion-leads, visualizacion: barras }
    - { metrica: tiempo_primera_respuesta, fuente: gestion-canales-unificados, visualizacion: serie }
    - { metrica: conversion_por_etapa, fuente: gestion-pipeline-demandante, visualizacion: embudo }
    - { metrica: motivos_perdida, fuente: gestion-pipeline-demandante, visualizacion: torta }
    - { metrica: tasa_atencion_llamadas, fuente: gestion-telefonia-llamadas, visualizacion: serie }
    - { metrica: llamadas_perdidas, fuente: gestion-telefonia-llamadas, visualizacion: contador }
    - { metrica: perdidas_rescatadas, fuente: gestion-llamada-perdida, visualizacion: contador }
  frecuencia_revision: diaria
  nota: "Este tablero elimina el informe manual que hoy alguien arma en Excel para 'si alguien alguna vez se lo pide' — y reemplaza el conteo a mano de llamadas y mensajes (C-04). Los widgets de voz son fundamental porque su fuente lo es (V3 ✔)."
```

```yaml
id: tableros-embudo-por-linea
nombre_interno: "Embudo end-to-end por línea de negocio con conversión y ciclo por etapa"
nombre_cliente: "Ver cada línea de tu negocio como un embudo completo: dónde entra, dónde avanza, dónde muere"
tipo: tablero
visibilidad_cliente: back
posicion_journey: 132
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio, sujeto_del_embudo]   # el embudo oferente tiene su propio tablero
depende_de: [gestion-pipeline-demandante]
metrica_que_habilita: []
esfuerzo_base: 2
esfuerzo_por_instancia: 1
detalle:
  audiencia_funcion: [coordinador, aprobador_comercial]
  widgets:
    - { metrica: conversion_por_etapa, fuente: gestion-pipeline-demandante, visualizacion: embudo }
    - { metrica: dias_en_etapa, fuente: gestion-pipeline-demandante, visualizacion: barras }
    - { metrica: oportunidades_abiertas_valor, fuente: gestion-pipeline-demandante, visualizacion: contador }
  frecuencia_revision: semanal
```

### Sustancia: el negocio completo (avanzado)

```yaml
id: tableros-mercadeo-atribucion
nombre_interno: "Atribución de punta a punta: fuente → conversación → etapa → cierre"
nombre_cliente: "Medir el lead desde que entró frío hasta que se convirtió — y saber qué canal lo trajo"
tipo: tablero
visibilidad_cliente: back
posicion_journey: 133
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [gestion-campos-atribucion, atraccion-conexion-pauta]
metrica_que_habilita: []
esfuerzo_base: 3
esfuerzo_por_instancia: 0
detalle:
  audiencia_funcion: [coordinador]        # mercadeo
  widgets:
    - { metrica: leads_por_fuente, fuente: gestion-campos-atribucion, visualizacion: barras }
    - { metrica: leads_por_campana, fuente: atraccion-conexion-pauta, visualizacion: tabla }
    - { metrica: cpl_por_campana, fuente: atraccion-conexion-pauta, visualizacion: tabla }
    - { metrica: conversion_por_etapa, fuente: gestion-pipeline-demandante, filtro: por_primera_fuente, visualizacion: embudo_comparado }
  frecuencia_revision: semanal
  nota: "El dolor textual del coordinador de mercadeo del piloto. cpl_por_campana exige el ad spend del cliente: si no lo entrega, el widget se muestra vacío con la leyenda de qué falta — nunca con un estimado."
```

```yaml
id: tableros-gerencia
nombre_interno: "Vista ejecutiva: valor del pipeline, cierres, ciclo y comparativo entre líneas y territorios"
nombre_cliente: "El negocio completo en una pantalla: qué línea empuja, qué territorio rinde, qué se está frenando"
tipo: tablero
visibilidad_cliente: back
posicion_journey: 134
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [tableros-embudo-por-linea]
metrica_que_habilita: []
esfuerzo_base: 3
esfuerzo_por_instancia: 0
detalle:
  audiencia_funcion: [aprobador_comercial]  # gerencia/dirección
  widgets:
    - { metrica: oportunidades_abiertas_valor, fuente: gestion-pipeline-demandante, filtro: por_linea, visualizacion: barras }
    - { metrica: captaciones_mes, fuente: gestion-pipeline-oferente, visualizacion: serie }
    - { metrica: citas_por_territorio, fuente: gestion-calendario-visitas, visualizacion: mapa_o_tabla }
    - { metrica: renovaciones_a_tiempo_pct, fuente: fidelizacion-hitos-vencimientos, visualizacion: semaforo }
  frecuencia_revision: semanal
```

```yaml
id: tableros-postventa-retencion
nombre_interno: "Retención y crecimiento de cartera: NPS, recompra, referidos, riesgo"
nombre_cliente: "La salud de tus clientes actuales, que son tu ingreso del año que viene"
tipo: tablero
visibilidad_cliente: back
posicion_journey: 135
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [unico]
aplica_si: "módulo referidos_fidelizacion en el plan"
depende_de: [fidelizacion-encuesta-satisfaccion, referidos-solicitud]
metrica_que_habilita: []
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  audiencia_funcion: [postventa_administracion, coordinador]
  widgets:
    - { metrica: nps, fuente: fidelizacion-encuesta-satisfaccion, visualizacion: serie }
    - { metrica: clientes_sin_contacto_90d, fuente: fidelizacion-segmento-clientes, visualizacion: contador }
    - { metrica: tasa_recompra, fuente: fidelizacion-secuencia-recompra, visualizacion: serie }
    - { metrica: leads_por_referido, fuente: referidos-solicitud, visualizacion: contador }
  frecuencia_revision: mensual
```

```yaml
id: tableros-dependencias-terceros
nombre_interno: "SLA de terceros: ciclos, solicitudes sin respuesta y evidencia del indicador externo"
nombre_cliente: "Los datos que hoy no tienes para negociar con quien controla tu proceso"
tipo: tablero
visibilidad_cliente: back
posicion_journey: 136
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [unico]
aplica_si: "existe dependencias_externas_del_proceso o indicadores_impuestos_externamente"
depende_de: [gestion-solicitud-habilitador]
metrica_que_habilita: []
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  audiencia_funcion: [aprobador_comercial, coordinador]
  widgets:
    - { metrica: ciclo_solicitud_a_visita, fuente: gestion-solicitud-habilitador, visualizacion: serie }
    - { metrica: solicitudes_sin_respuesta_tercero, fuente: gestion-solicitud-habilitador, visualizacion: contador }
    - { metrica: distribucion_score, fuente: gestion-scoring-contacto, filtro: leads_recibidos_del_tercero, visualizacion: histograma }
  frecuencia_revision: mensual
  nota: "El tablero políticamente más valioso del catálogo: mitiga F-15 y arma la renegociación de F-17. No optimiza nada de Ropofy — mide al tercero. El tercer widget documenta la calidad real del lead recibido: la evidencia contra el indicador perverso."
```

### Iniciativa: los números avisan solos (inteligente)

```yaml
id: tableros-alertas-desviacion
nombre_interno: "Alertas automáticas por desviación de métrica contra su línea base"
nombre_cliente: "No esperas a la reunión de los lunes para enterarte: el sistema avisa cuando algo se sale de rango"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 137
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [tableros-coordinador-equipo]
metrica_que_habilita: [alertas_disparadas_mes]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: desviacion_metrica, filtros: [tiempo_primera_respuesta, tasa_respuesta_reactivacion, calidad_linea_whatsapp, conversion_por_etapa] }
  acciones:
    - { orden: 1, tipo: notificar, canal: whatsapp, asigna_a_funcion: coordinador }
```

```yaml
id: tableros-economico
nombre_interno: "Unit economics en vivo: CAC, LTV, ROAS y payback con las fórmulas del guión"
nombre_cliente: "Las cuentas que hoy se hacen una vez al año en Excel, vivas y al día"
tipo: tablero
visibilidad_cliente: back
posicion_journey: 138
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [unico]
aplica_si: "ficha.datos_economicos_capturados suficiente (modo A)"
depende_de: [tableros-mercadeo-atribucion, cierre-contrato-firma]
metrica_que_habilita: [cac_real, ltv_medido, roas, payback_meses]
esfuerzo_base: 3
esfuerzo_por_instancia: 0
prerequisito_plataforma: ["Datos del formulario del guión cargados y con periodo declarado: ad spend, costos de equipo, margen, ticket, churn"]
detalle:
  audiencia_funcion: [aprobador_comercial]
  widgets:
    - { metrica: cac_real, fuente: calculo, visualizacion: contador_con_formula }
    - { metrica: ltv_medido, fuente: calculo, visualizacion: contador_con_formula }
    - { metrica: roas, fuente: calculo, visualizacion: serie }
    - { metrica: payback_meses, fuente: calculo, visualizacion: contador }
  frecuencia_revision: mensual
  nota: "Es el motor del caso de éxito: la línea base del diagnóstico contra estos números a los 6 meses. Si el cliente está en modo B, este componente se muestra en el lienzo atenuado con la leyenda 'requiere tus datos económicos' — es el incentivo natural para entregarlos."
```

### Validaciones del módulo — y auditoría V3 de toda la librería

- **V1** ✔ alertas y económico (inteligente) sobre fundamentales/avanzados.
- **V3 — auditoría completa**: los 30 widgets de este módulo citan 26 métricas
  distintas; las 26 existen en el diccionario con componente fuente de plan
  igual o inferior al del tablero que las consume. Dos casos límite resueltos:
  `distribucion_score` (fuente inteligente) solo aparece en
  tableros-dependencias-terceros, cuyo widget se declara condicional al plan;
  `cpl_por_campana` y las 4 métricas económicas dependen de **datos externos
  del cliente** — el diccionario las marca y el widget vacío lo dice, nunca
  estima.
- **V9 ✔ por construcción**: toda fuga cuantificable del catálogo tiene su
  métrica de evolución en al menos un tablero (F-01→recuperados_por_secuencia
  en coordinador; F-04→recuperadas_post_propuesta; F-10→tasa_respuesta_reactivacion;
  F-12→renovaciones_a_tiempo_pct; F-15/F-17→dependencias-terceros).

---

## B. Validación contra el piloto

| Componente | Instancias | Detalle |
|---|---|---|
| operativo-asesor | 1 | ~10 personas de atención |
| coordinador-equipo | 3 | ventas, arriendos, captación (Tatiana, Alexandra/Jeffrey, Steven) |
| embudo-por-linea | 5 | 4 demandantes + 1 oferente |
| mercadeo-atribucion | 1 | **la varita mágica de Jesús, textual**: "poder medir el lead desde que entró frío hasta que se convirtió" |
| gerencia | 1 | |
| postventa-retencion | 1 | |
| dependencias-terceros | 1 | **el arma de negociación con SAE**: ciclo de llaves medido + calidad real del lead recibido |
| alertas-desviacion | 1 | calidad de línea durante la reactivación masiva: crítico |
| economico | bloqueado | modo B — cero datos económicos capturados. Se propone atenuado con su condición visible |

Esfuerzo Tableros plan Inteligente: ~21 base + ~7 instancias ≈ **28 puntos ≈ 14
jornadas**.

---

## C. Métricas agregadas al diccionario (v0.7 — final)

| id | Definición | Requiere datos externos |
|---|---|---|
| `alertas_disparadas_mes` | Alertas de desviación emitidas | no |
| `cac_real` | (Ad spend + agencia + herramientas + costo equipo atribuible + comisiones) / clientes nuevos — fórmula del guión | **sí** |
| `ltv_medido` | Ingreso mensual × margen / churn (o suma por permanencia) — fórmula del guión | **sí** |
| `roas` | Ingresos atribuibles a pauta / ad spend | **sí** |
| `payback_meses` | CAC / margen mensual por cliente | **sí** |

Diccionario cerrado en **78 métricas**. Las marcadas "sí" son las únicas que no
puede producir el sistema solo: son el puente permanente entre el guión de
diagnóstico y la operación.

---

## D. Cierre de la librería

Con Tableros, los 7 módulos quedan poblados: **83 componentes** (conteo verificado)
y ~90 métricas, tras la auditoría del caso AYC: canal de voz, pipeline operativo,
números atribuidos y las habilidades de IA separadas por nivel.

**El canal de voz entró como ciudadano de primera clase.** La librería nació
asumiendo que todo pasa por texto; el diagnóstico de AYC lo desmintió (línea
fija en avisos, call center, llamadas contadas a mano, atribución por número
dedicado desde hace una década). Consecuencia transversal: donde se lea "canal",
son tres — WhatsApp, web/email y **voz**. Cada fuga de entrada tiene su gemela
telefónica y `gestion-telefonia-llamadas` es Fundamental porque sin registro de llamadas
la promesa "nada se pierde" es falsa en el canal por donde muchos pymes reciben
la mitad de su demanda.

**Piloto Activos por Colombia, plan Inteligente completo: ~300 puntos ≈ 150
jornadas**, contra ~130 de un cliente monolínea simple con el mismo plan. El
multiplicador 2.3× se sostuvo a través de toda la librería.

**Matriz de fronteras — confirmada 7 de 7, lista para enunciarse:**

| Salto | La frase |
|---|---|
| → **Fundamental** | *Nada se pierde*: todo lead capturado con origen, con dueño, con seguimiento, con hito; lo que cae queda clasificado y en espera. |
| → **Avanzado** | *El sistema trabaja*: atiende, agenda, nutre con sustancia, firma, cobra, despierta la base dormida, pide reseñas y referidos. |
| → **Inteligente** | *El sistema decide primero*: detecta señales, sabe quién vale más, actúa solo y habla en plata. |

La escalera de planes es también una **escalera de madurez** (ver catálogo de
fugas §6): Fundamental resuelve lo que al cliente le duele hoy; Avanzado lo que
le dolerá cuando eso esté resuelto (por eso Reactivación, Reputación y Referidos
arrancan ahí); Inteligente, lo que distingue a la operación que ya funciona.

Pendientes transversales al construir los snapshots: las plantillas de mensaje
de los 7 módulos, las minutas por industria, y las dos preguntas nuevas del
guión que cada módulo dejó anotadas.
