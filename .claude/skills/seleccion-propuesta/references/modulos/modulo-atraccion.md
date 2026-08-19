# Módulo Atracción — Librería de componentes v0.1

12 componentes en dos submódulos: **Presencia** (atraccion_presencia) y
**Reputación** (atraccion_reputacion). Schema v0.2.2.

**Advertencia de venta que gobierna este módulo**: en 264 dolores de 53
diagnósticos, Reputación tuvo **cero menciones**. No se vende desde fugas — se
vende desde oportunidad, con dos datos que el guión sí captura: % de ventas que
ya llegan por referido/orgánico (Bloque 1) y el rating público actual del
cliente contra sus competidores (verificable en 2 minutos antes de la sesión).
Presencia sí tiene contraparte en el catálogo: D-01, D-02 (carencias) y F-13.

---

> **Descartado de la oferta — números atribuidos por canal (number pool).**
> Un número dedicado por portal, valla o aviso es la forma clásica de atribución
> telefónica, pero en Colombia el costo mensual por número la hace inviable para
> pyme: no la ofrecemos. La atribución de voz se resuelve con el canal telefónico
> del CRM (registro por origen del contacto) y la de digital con UTM + campos de
> atribución. Si un cliente ya la tiene montada por su cuenta (caso AYC con
> portales), se respeta y se lee, pero Ropofy no instala ni cobra números nuevos.

## A. Componentes — Presencia

### Captura con atribución (posicion_journey 1–8)

```yaml
id: atraccion-landing-captura
nombre_interno: "Landing page por línea con formulario, UTM y destino al CRM"
nombre_cliente: "Una página que convierte visitas en contactos con nombre y origen — no en chats anónimos"
tipo: embudo_web
visibilidad_cliente: front
posicion_journey: 1
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio, sujeto_del_embudo]   # la landing "vende tu inmueble con nosotros" es la captación oferente
depende_de: [gestion-campos-atribucion]
cierra_fugas: [D-02]
mitiga_fugas: [FO-03]
metrica_que_habilita: [visitas_landing, conversion_landing, leads_por_landing]
esfuerzo_base: 3
esfuerzo_por_instancia: 2
detalle:
  embebible: "el formulario se incrusta en cualquier sitio existente — no exige construir página nueva"
  paginas:
    - { nombre: captura, objetivo: lead_con_datos, elementos: [propuesta_valor, formulario, whatsapp_alternativo] }
  metrica_conversion: visitas_a_lead
  nota: "El WhatsApp queda como alternativa, no como único destino: el formulario captura aunque el equipo esté dormido, y captura CON origen."
```

```yaml
id: atraccion-formularios-precalificacion
nombre_interno: "Formularios de captura y precalificación, embebibles en cualquier sitio del cliente"
nombre_cliente: "El curioso se filtra solo, antes de gastar un minuto de tu equipo"
tipo: formulario
visibilidad_cliente: front
posicion_journey: 2
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio, sujeto_del_embudo]
depende_de: [atraccion-landing-captura, gestion-campos-calificacion]
cierra_fugas: [F-13]                      # el cierre en origen; el scoring de Gestión es la segunda capa
metrica_que_habilita: [leads_por_formulario, tasa_descalificacion_origen]
esfuerzo_base: 2
esfuerzo_por_instancia: 1
detalle:
  campos:
    - { etiqueta: presupuesto_o_rango, campo_destino: presupuesto_rango, obligatorio: true }
    - { etiqueta: horizonte_de_decision, campo_destino: temperatura, obligatorio: true }
  destino: { pipeline_ref: gestion-pipeline-demandante, etapa: Nuevo }
  accion_post_envio: gestion-respuesta-inmediata
```

```yaml
id: atraccion-conexion-pauta
nombre_interno: "Conexión nativa Meta Lead Ads / Google al CRM con atribución por campaña"
nombre_cliente: "Cada peso de pauta entra al sistema con nombre de campaña — se acabó el 'vino de WhatsApp'"
tipo: integracion
visibilidad_cliente: back
posicion_journey: 3
plan_minimo: fundamental
mecanismo_entrega: configuracion_cuenta
se_instancia_por: [unico]
aplica_si: "el cliente invierte en pauta digital"
depende_de: [gestion-campos-atribucion, gestion-ruteo-intencion]
cierra_fugas: []
mitiga_fugas: []                          # es la mitad ejecutora de C-02: atribución de pauta por campaña
metrica_que_habilita: [leads_por_campana, cpl_por_campana]
esfuerzo_base: 3
esfuerzo_por_instancia: 0
prerequisito_plataforma: ["Acceso al Business Manager del cliente o de su agencia"]
detalle:
  sistema: meta_lead_ads_y_google
  direccion: entrada
  objetos_sincronizados: [leads, campana_origen]
  mecanismo: nativa
```

```yaml
id: atraccion-burbuja-web
nombre_interno: "Burbuja de conversación en el sitio del cliente con captura de datos previa"
nombre_cliente: "El visitante de tu web conversa sin salir de ella, y deja sus datos antes del primer mensaje"
tipo: integracion
visibilidad_cliente: front
posicion_journey: 4
plan_minimo: fundamental
mecanismo_entrega: configuracion_cuenta
se_instancia_por: [unico]
aplica_si: "existe sitio web propio activo"
depende_de: [gestion-canales-unificados]
cierra_fugas: []
metrica_que_habilita: [conversaciones_desde_web]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  sistema: webchat_propio
  direccion: entrada
  mecanismo: nativa
  nota: "Reemplaza el patrón 'la web manda a WhatsApp y se pierde el rastro': la conversación nace ya atribuida a la web."
```

```yaml
id: atraccion-qr-atribuido
nombre_interno: "QRs con UTM por punto físico: letreros, vitrina, material impreso, vehículos"
nombre_cliente: "Saber cuántos clientes trae cada letrero, cada valla y cada vitrina"
tipo: embudo_web
visibilidad_cliente: front
posicion_journey: 5
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [territorio]            # o por tipo de punto físico
aplica_si: "existe captación offline (letreros, punto físico, material impreso)"
depende_de: [gestion-campos-atribucion]
cierra_fugas: []
metrica_que_habilita: [escaneos_por_punto, leads_por_canal_fisico]
esfuerzo_base: 1
esfuerzo_por_instancia: 1
detalle:
  paginas:
    - { nombre: destino_qr, objetivo: conversacion_atribuida, elementos: [redireccion_whatsapp_con_utm] }
  metrica_conversion: escaneo_a_conversacion
```

### Presencia propia (6–8)

```yaml
id: atraccion-catalogo-publicado
nombre_interno: "Sitio/catálogo web construido en AI Studio con ficha por ítem y captura por ficha"
nombre_cliente: "Tu inventario visible, buscable, y cada ficha capturando interesados con nombre"
tipo: embudo_web
visibilidad_cliente: front
posicion_journey: 6
plan_minimo: avanzado
mecanismo_entrega: contenido_a_medida     # AI Studio genera; el criterio de marca y estructura lo pone el consultor
se_instancia_por: [linea_negocio]
aplica_si: "D-02 presente, o catálogo estructurado sin vitrina propia"
depende_de: [atraccion-landing-captura]
cierra_fugas: [D-02]
metrica_que_habilita: [visitas_por_ficha, interes_por_item]
esfuerzo_base: 4                          # AI Studio bajó el costo de construcción; el criterio no baja
esfuerzo_por_instancia: 2
prerequisito_plataforma: ["AI Studio habilitado en Labs", "Desde sep-2026 el uso se liga al plan de AI Employee — costo variable a contemplar en la cotización", "Catálogo con atributos (ficha D); si es 'parcial', carga inicial manual-asistida", "Los formularios de AI Studio NO conectan solos: requieren el paso Connect-to-CRM para que las capturas lleguen al sistema y disparen workflows"]
detalle:
  paginas:
    - { nombre: catalogo, objetivo: navegacion_filtrada }
    - { nombre: ficha_item, objetivo: interes_por_item_especifico, elementos: [galeria, atributos, formulario_corto] }
  metrica_conversion: ficha_a_interes
  nota_alcance: "AI Studio también produce experiencias interactivas simples (encuestas multi-paso, flujos de agendamiento, portales livianos) — dentro del alcance de Ropofy. Aplicaciones con lógica de negocio o backend propio quedan fuera: se declaran y se derivan. Los proyectos de AI Studio viajan en snapshots, así que las vitrinas por industria son replicables como el resto de la librería."
  nota_plan: "Decisión de producto: NO es add-on. El plan acumulativo + aplica_si ya resuelven el dilema — quien no lo necesita (la mayoría) no lo ve en su propuesta aunque su plan lo incluya, y quien apenas empieza (D-02) lo encuentra en Avanzado. Un add-on rompería la simplicidad de las tres frases."
```

```yaml
id: atraccion-seo-contenido
nombre_interno: "Blog con SEO local y contenido por línea, calendario editorial trimestral"
nombre_cliente: "Aparecer cuando buscan lo tuyo en tu zona, sin pagar por cada clic"
tipo: contenido
visibilidad_cliente: front
posicion_journey: 7
plan_minimo: avanzado
mecanismo_entrega: contenido_a_medida
se_instancia_por: [linea_negocio]
aplica_si: "existe sitio propio o atraccion-catalogo-publicado en el plan"
depende_de: [atraccion-catalogo-publicado]
cierra_fugas: []
mitiga_fugas: [D-01]                      # reduce dependencia de pauta a mediano plazo; nunca la reemplaza en el corto
metrica_que_habilita: [trafico_organico, leads_organicos_mes]
esfuerzo_base: 4
esfuerzo_por_instancia: 2
detalle:
  piezas:
    - { tipo: articulo_seo_local, cantidad: 6, quien_produce: ropofy_con_insumos_cliente }
  nota: "Se vende como inversión de mediano plazo con expectativa explícita: el orgánico tarda meses. Prometerlo como solución a D-01 inmediata es sobreventa."
```

```yaml
id: atraccion-ab-testing
nombre_interno: "Pruebas A/B sobre landings y formularios con criterio de cierre"
nombre_cliente: "La página aprende qué versión convierte más, y se queda con la ganadora"
tipo: automatizacion
visibilidad_cliente: back
posicion_journey: 8
plan_minimo: inteligente
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [atraccion-landing-captura]
cierra_fugas: []
metrica_que_habilita: [experimentos_activos, mejora_conversion_acumulada]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  disparador: { tipo: programado, condicion: "experimento activo con tráfico suficiente" }
  acciones:
    - { orden: 1, tipo: dividir_trafico }
    - { orden: 2, tipo: declarar_ganadora, condicion: "significancia o tope de tiempo" }
```

---

## B. Componentes — Reputación

```yaml
id: reputacion-solicitud-resenas
nombre_interno: "Solicitud automática de reseña post-experiencia con compuerta de satisfacción"
nombre_cliente: "Cada cliente contento se convierte en una reseña pública; cada inconforme, en un caso privado"
tipo: automatizacion
visibilidad_cliente: front
posicion_journey: 105                     # vive después del cierre en el journey
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio]
depende_de: [gestion-pipeline-demandante, nutricion-plantillas-whatsapp]
cierra_fugas: []
metrica_que_habilita: [resenas_solicitadas, tasa_resena, casos_internos_abiertos]
esfuerzo_base: 2
esfuerzo_por_instancia: 1
detalle:
  disparador: { tipo: cambio_etapa, condicion: "cerrada_ganada + N días de experiencia" }
  acciones:
    - { orden: 1, tipo: encuesta_corta, canal: whatsapp, plantilla_ref: como-te-fue }
  ramas:
    - { condicion: "satisfaccion >= 4", acciones: [{ tipo: mensaje, plantilla_ref: link-resena-google }] }
    - { condicion: "satisfaccion < 4", acciones: [{ tipo: crear_tarea, asigna_a_funcion: coordinador }, { tipo: no_pedir_resena }] }
  nota: "La compuerta es el componente completo: pedir reseña sin filtrar convierte cada mala experiencia en daño público permanente."
```

```yaml
id: reputacion-bandeja-resenas
nombre_interno: "Monitoreo y respuesta de reseñas desde una bandeja única con SLA"
nombre_cliente: "Ninguna reseña —buena o mala— se queda sin respuesta más de 48 horas"
tipo: integracion
visibilidad_cliente: back
posicion_journey: 106
plan_minimo: avanzado
mecanismo_entrega: configuracion_cuenta
se_instancia_por: [unico]
depende_de: []
cierra_fugas: []
metrica_que_habilita: [rating_promedio, resenas_respondidas_pct, tiempo_respuesta_resena]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
prerequisito_plataforma: ["Perfil de Google Business verificado y con acceso"]
detalle:
  sistema: google_business
  direccion: bidireccional
  objetos_sincronizados: [resenas, respuestas]
  mecanismo: nativa
```

```yaml
id: reputacion-prueba-social
nombre_interno: "Reseñas destacadas embebidas en landings y secuencias de cierre"
nombre_cliente: "Lo que dicen tus clientes trabaja en cada página y en cada propuesta"
tipo: contenido
visibilidad_cliente: front
posicion_journey: 107
plan_minimo: avanzado
mecanismo_entrega: snapshot
se_instancia_por: [unico]
depende_de: [reputacion-bandeja-resenas, atraccion-landing-captura]
cierra_fugas: []
metrica_que_habilita: []
esfuerzo_base: 1
esfuerzo_por_instancia: 0
detalle:
  piezas:
    - { tipo: widget_resenas_en_landing, cantidad: 1, quien_produce: ropofy }
    - { tipo: bloque_prueba_social_en_propuesta, cantidad: 1, quien_produce: ropofy }
```

```yaml
id: reputacion-respuestas-ia
nombre_interno: "IA redacta borradores de respuesta a reseñas con tono de marca; humano aprueba las negativas"
nombre_cliente: "Responder cien reseñas cuesta lo mismo que responder una"
tipo: chatbot_ia
visibilidad_cliente: front
habilidad: redactor_resenas
posicion_journey: 108
plan_minimo: inteligente
mecanismo_entrega: contenido_a_medida
se_instancia_por: [unico]
depende_de: [reputacion-bandeja-resenas]
cierra_fugas: []
metrica_que_habilita: [respuestas_generadas_ia, tiempo_respuesta_resena_ia]
esfuerzo_base: 2
esfuerzo_por_instancia: 0
detalle:
  alcance: [respuesta_positivas_auto, borrador_negativas]
  criterio_escalamiento: "toda reseña <= 3 estrellas pasa por humano"
  handoff_a_funcion: coordinador
```

### Validaciones del módulo

- **V1** ✔ en ambos submódulos; ab-testing y respuestas-ia (inteligente)
  dependen de fundamentales/avanzados.
- **V2** ✔ referencias cruzadas existen.
- **V6** ✔ D-01 solo mitigada por SEO (con expectativa declarada); D-02 cerrada
  por landing/catálogo; F-13 cerrada en origen aquí y reforzada por scoring en
  Gestión — dos capas, un solo conteo en la propuesta.
- **V7** ✔ Presencia abre el journey (1–8); Reputación vive post-cierre
  (105–108) aunque pertenezca a Atracción — su efecto es de captación, su
  disparador es la experiencia. El lienzo debe dibujarla como el lazo que vuelve
  del final al inicio.
- **Nota de venta**: los componentes de Reputación no citan fugas. Su argumento
  es la brecha de rating contra competidores y el % de ventas que ya llega por
  orgánico/referido. Si la propuesta intenta monetizarlos como fuga, miente.

---

## C. Validación contra el piloto

| Componente | Instancias | Detalle |
|---|---|---|
| landing-captura | 3 | venta, arriendo, y **captación oferente** ("vende tu inmueble con nosotros") — hoy el sitio no tiene un solo formulario: "no hay una landing que permita registrar los datos y caigan a un CRM, sería chévere poder testearlo" (Jesús, literal) |
| formularios-precalificacion | 3 | el filtro que Alexandra pide: 60% de chats son curiosos |
| conexion-pauta | 1 | **resuelve la contradicción Jhonny/Jesús sobre lead forms**: con conexión nativa, exista o no el formulario hoy, mañana existe y atribuye |
| burbuja-web | 1 | reemplaza el webchat de Actichat apagado |
| qr-atribuido | 2 | letreros de precaptación de Steven + material físico |
| catalogo-publicado | parcial | ya tienen sitio con catálogo; lo que falta es captura por ficha — se implementa como mejora, no construcción |
| seo-contenido | 1–2 | |
| reputacion (4) | 1 c/u | **modo B declarado**: la sesión no capturó rating actual ni % referidos — verificar el perfil de Google Business antes de proponer |

Esfuerzo Atracción plan Inteligente: ~31 base + ~17 instancias ≈ **48 puntos ≈
24 jornadas**. Acumulado 5 módulos: ~242 puntos.

---

## D. Métricas agregadas al diccionario (v0.5)

| id | Definición | Fuente |
|---|---|---|
| `visitas_landing` / `conversion_landing` / `leads_por_landing` | Embudo de cada landing, por instancia | landing-captura |
| `leads_por_formulario` / `tasa_descalificacion_origen` | Captura y filtro en origen | formularios |
| `leads_por_campana` / `cpl_por_campana` | Atribución de pauta. **cpl requiere ad spend del cliente: dato del guión, no del sistema** | conexion-pauta |
| `conversaciones_desde_web` | Conversaciones nacidas en el sitio | burbuja-web |
| `escaneos_por_punto` / `leads_por_canal_fisico` | El offline, medido | qr-atribuido |
| `visitas_por_ficha` / `interes_por_item` | Demanda por ítem del catálogo — insumo directo de alertas de coincidencia y de decisiones de alistamiento (F-14) | catalogo-publicado |
| `trafico_organico` / `leads_organicos_mes` | Rendimiento SEO | seo-contenido |
| `experimentos_activos` / `mejora_conversion_acumulada` | Rendimiento del AB | ab-testing |
| `resenas_solicitadas` / `tasa_resena` / `casos_internos_abiertos` | Embudo de reputación con compuerta | solicitud-resenas |
| `rating_promedio` / `resenas_respondidas_pct` / `tiempo_respuesta_resena` | Salud pública de la marca | bandeja-resenas |

---

## E. Pendientes y frontera

1. El guión sigue sin preguntas de Reputación (hallazgo original intacto): las
   dos preguntas propuestas (¿piden reseñas? ¿quién responde las malas?) deben
   entrar al Bloque nuevo, y el consultor debería llegar a la sesión con el
   rating de Google ya consultado — es público.
2. `interes_por_item` conecta Atracción con F-14: la demanda medida por ficha es
   el criterio objetivo para priorizar alistamientos/avalúos. Vale mencionarlo
   en la propuesta del piloto.
3. **Frontera, quinta confirmación**: Fundamental = todo canal captura con
   atribución (cobertura); Avanzado = presencia propia que convierte y reputación
   gestionada (sustancia); Inteligente = la captación se optimiza sola
   (iniciativa).
